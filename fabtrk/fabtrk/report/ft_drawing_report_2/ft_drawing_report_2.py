


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
        # ===== TOTAL Row (Unit Weight + Total Weight) =====
    total_unit_weight = sum(d.get("unit_weight", 0) for d in raw_data)
    total_total_weight = sum(d.get("total_weight", 0) for d in raw_data)

    raw_data.append({
        "project_name": "TOTAL",
        "drawing_number": "",
        "po_serial_no": "",
        "unit_weight": total_unit_weight,
        "quantity": "",
        "total_weight": total_total_weight
    })

    

# ================= SUMMARY =================

    project_names = {d.get("project_name") for d in raw_data if d.get("project_name") != "TOTAL"}
    drawing_ids = {d.get("drawing_id") for d in raw_data if d.get("drawing_id")}
    po_rows = [d for d in raw_data if d.get("po_serial_no")]

    total_projects = len(project_names)
    total_no_of_drawings = len(drawing_ids)
    total_po_drawings = len(po_rows)

    total_weight_as_per_project = sum(d.get("total_weight", 0) for d in raw_data if d.get("project_name") != "TOTAL")
    total_weight_po_items = sum(d.get("total_weight", 0) for d in po_rows)

    # project_names = {d.project_name for d in raw_data if d.project_name}
    # drawing_ids = {d.drawing_id for d in raw_data if d.drawing_id}
    # po_rows = [d for d in raw_data if d.po_serial_no]

    # total_projects = len(project_names)
    # total_no_of_drawings = len(drawing_ids)
    # total_po_drawings = len(po_rows)

    # # Project total weight
    # total_weight_as_per_project = sum(d.total_weight for d in raw_data)

    # # PO Line Items total weight
    # total_weight_po_items = sum(d.total_weight for d in po_rows)

    # Drawing balance for customer = project total - PO items total
    drawing_balance_for_customer = total_weight_as_per_project - total_weight_po_items

    formatted_total_weight_as_per_project = "{:,.3f}".format(total_weight_as_per_project)
    formatted_total_weight_po_items = "{:,.3f}".format(total_weight_po_items)
    formatted_drawing_balance_for_customer = "{:,.3f}".format(drawing_balance_for_customer)

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
                        <p>Project Total No of Line Items</p>
                        <span>{total_po_drawings}</span>                    
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight of Line Items<br>Assign to Project(Kg)</p>
                        <span>{formatted_total_weight_po_items}</span>                    
                    </div>
                </div>
                
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Unique Drawings</p>
                        <span>{total_no_of_drawings}</span>                    
                    </div>
                </div>
                
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Drawing Balance for Customer(Kg)</p>
                        <span>{formatted_drawing_balance_for_customer}</span>                   
                    </div>
                </div>

            </div>
            """,
            "datatype": "HTML",
        }
    ]
    return columns, raw_data, None, None, report_summary




