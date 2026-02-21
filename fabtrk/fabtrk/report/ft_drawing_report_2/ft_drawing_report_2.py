

# this code for multi select filter filed
import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 130},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Data","width": 200,"align": "center"},
        {"label": "PO Position No", "fieldname": "po_position_no", "fieldtype": "Data","width": 200,"align": "center"},
        {"label": "Unit Weight", "fieldname": "unit_weight", "fieldtype": "Float", "width": 150,"align": "center"},
        {"label": "Required Qty", "fieldname": "quantity", "fieldtype": "Int", "width": 120,"align": "center"},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150,"align": "center"},
    ]

    conditions = ""
    values = {}

    # Multi Project Filter
    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    # Multi Drawing Filter
    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    # Project Is Active Filter
    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

   # MAIN QUERY (PROJECT BASED)
    query = f"""
        SELECT
            p.name AS project_name,
            ad.drawing_number AS drawing_number,
            ad.po_position_no AS po_position_no,
            IFNULL(ad.unit_weight, 0) AS unit_weight,
            IFNULL(ad.quantity, 0) AS quantity,
            IFNULL(ad.total_weight, 0) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad
            ON ad.project_number = p.name
        WHERE 1=1
        {conditions}
        ORDER BY p.name, ad.name
    """

    raw_data = frappe.db.sql(query, values, as_dict=1) or []

    # SUMMARY CALCULATIONS
    project_names = {d.project_name for d in raw_data if d.project_name}
    drawing_names = {d.drawing_number for d in raw_data if d.drawing_number}

    total_projects = len(project_names)
    total_no_of_drawings = len(drawing_names)

    if project_names:
        total_weight_as_per_project = frappe.db.sql("""
            SELECT SUM(total_weight)
            FROM `tabFT Project`
            WHERE name IN %(projects)s
        """, {"projects": tuple(project_names)}, as_list=1)[0][0] or 0
    else:
        total_weight_as_per_project = 0

    total_weight_as_per_drawing = sum(d.total_weight or 0 for d in raw_data)

      
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
                        <span>{total_weight_as_per_project}</span>                    
                    </div>
                </div>
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Drawings</p>
                        <span>{total_no_of_drawings}</span>                    
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Drawing(Kg)</p>
                        <span>{total_weight_as_per_drawing}</span>                    
                    </div>
                </div>
                
            </div>
            """,
            "datatype": "HTML",
        }
    ]

    return columns, raw_data, None, None, report_summary



