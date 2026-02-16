# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data



import frappe
def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 150},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Data", "width": 150},
        {"label": "Total Drawing Parts", "fieldname": "drawing_part_count", "fieldtype": "Int", "width": 200},
        {"label": "Unit Weight", "fieldname": "unit_weight", "fieldtype": "Float", "width": 150},
        {"label": "Required Qty", "fieldname": "required_qty", "fieldtype": "Int", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
        {"label": "View", "fieldname": "view", "fieldtype": "HTML", "width": 120},
    ]

    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))


    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    query = f"""
        SELECT
            p.name AS project_name,
            ad.name AS drawing_id,
            ad.drawing_number AS drawing_number,
            COUNT(dp.name) AS drawing_part_count,
            COALESCE(ad.unit_weight, 0) AS unit_weight,
            COALESCE(ad.quantity, 0) AS required_qty,
            COALESCE(ad.total_weight, 0) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabAdd Drawing` ad ON ad.project_number = p.name
        LEFT JOIN `tabDrawing Parts` dp ON dp.drawing_number = ad.name
        WHERE 1=1
        {conditions}
        GROUP BY ad.name
        ORDER BY p.name, ad.name
    """

    data = frappe.db.sql(query, values, as_dict=True) or []

    # Add View button
    for row in data:
        if row.get("drawing_id"):
            row["view"] = f"""
                <button class="btn btn-xs btn-primary view-btn"
                    data-drawing-id="{row.get('drawing_id')}">
                    View
                </button>
            """
        else:
            row["view"] = ""

    # -------- REPORT SUMMARY --------

    total_projects = len(set([d.project_name for d in data if d.project_name]))
    total_drawings = len(set([d.drawing_number for d in data if d.drawing_number]))
    total_drawing_parts = sum([d.drawing_part_count or 0 for d in data])
    total_weight = sum([d.total_weight or 0 for d in data])
    
    # total weight as per project (from FT Project)
    project_conditions = ""
    project_values = {}

    if filters.get("project_number"):
        project_conditions += " AND name IN %(project_number)s"
        project_values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("is_active"):
        project_conditions += " AND is_active = 1"

    project_total_weight = frappe.db.sql(f"""
        SELECT SUM(total_weight)
        FROM `tabFT Project`
        WHERE 1=1
        {project_conditions}
    """, project_values)

    project_total_weight = project_total_weight[0][0] if project_total_weight and project_total_weight[0][0] else 0

    report_summary = [
        {"label": "Total Projects", "value": total_projects, "datatype": "Int"},
        {"label": "Total No of Drawings", "value": total_drawings, "datatype": "Int"},      
        {"label": "Total No of Drawing Parts", "value": total_drawing_parts, "datatype": "Int"}, 
        {"label": "Total Weight as per Drawing Parts", "value": total_weight, "datatype": "Float"}, 
        {"label": "Total Weight as per Project", "value": project_total_weight, "datatype": "Float"},
        {"label": "Total Weight as per Drawing", "value": total_weight, "datatype": "Float"},
        
    ]

    return columns, data, None, None, report_summary

@frappe.whitelist()
def get_drawing_part_details(drawing_id):

    if not drawing_id:
        return []

    return frappe.db.sql("""
        SELECT
            dp.name,
            dp.position_no,
            dp.project_number,
            dp.drawing_number,
            dp.item AS item_id,
            rm.computed_name AS item_name,
            dp.quantity,
            dp.breath,
            dp.lenght,
            dp.single_weight,
            dp.total_weight,
            dp.painted_surface_percentage
        FROM `tabDrawing Parts` dp
        LEFT JOIN `tabFT Stock RM List` rm 
            ON rm.name = dp.item
        WHERE dp.drawing_number = %s
        ORDER BY dp.position_no
    """, drawing_id, as_dict=True)

