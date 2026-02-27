import frappe
from frappe.utils import fmt_money

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 200},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Data","width": 200,"align": "center"},
        {"label": "PO Serial No", "fieldname": "po_serial_no", "fieldtype": "Data","width": 200,"align": "center"},
        {"label": "Unit Weight", "fieldname": "unit_weight", "fieldtype": "Float", "width": 200,"align": "center"},
        {"label": "Required Qty", "fieldname": "quantity", "fieldtype": "Int", "width": 200,"align": "center"},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 200,"align": "center"},
    ]

    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    query = f"""
        SELECT
            p.name AS project_name,
            ad.name as drawing_id,
            ad.drawing_number AS drawing_number,
            pod.po_serial_no AS po_serial_no,
            IFNULL(ad.unit_weight, 0) AS unit_weight,
            IFNULL(ad.quantity, 0) AS quantity,
            (IFNULL(ad.unit_weight,0) * IFNULL(ad.quantity,0)) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad
            ON ad.project_number = p.name
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.drawing_number = ad.name
        WHERE 1=1 {conditions}
        ORDER BY CAST(pod.po_serial_no AS UNSIGNED) ASC
    """

    raw_data = frappe.db.sql(query, values, as_dict=1) or []

    # ================= SUMMARY =================

    project_names = {d.project_name for d in raw_data if d.project_name}
    drawing_ids = {d.drawing_id for d in raw_data if d.drawing_id}
    po_rows = [d for d in raw_data if d.po_serial_no]

    total_projects = len(project_names)
    total_no_of_drawings = len(drawing_ids)
    total_po_drawings = len(po_rows)

    # Project total weight
    total_weight_as_per_project = sum(d.total_weight for d in raw_data)

    # Drawing total weight (unique drawing wise)
    drawing_weight_map = {}
    for d in raw_data:
        if d.drawing_id:
            drawing_weight_map[d.drawing_id] = d.total_weight

    total_weight_as_per_drawing = sum(drawing_weight_map.values())

    formatted_total_weight_as_per_project = "{:,.3f}".format(total_weight_as_per_project)
    formatted_total_weight_as_per_drawing = "{:,.3f}".format(total_weight_as_per_drawing)

    report_summary = [
        {
            "label": "",
            "value": f"""
            <div class="summary-container">
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total Projects</p>
                        <span>{total_projects}</span>                  
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Project(Kg)</p>
                        <span>{formatted_total_weight_as_per_project}</span>                   
                    </div>
                </div>

                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Drawings</p>
                        <span>{total_no_of_drawings}</span>                    
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Drawings(Kg)</p>
                        <span>{formatted_total_weight_as_per_drawing}</span>                   
                    </div>
                </div>
                
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of PO Drawings</p>
                        <span>{total_po_drawings}</span>                    
                    </div>
                </div>
                
            </div>
            """,
            "datatype": "HTML",
        }
    ]

    return columns, raw_data, None, None, report_summary

