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
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 130},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Link", "options": "Add Drawing", "width": 200},
        {"label": "Drawing Part", "fieldname": "drawing_part", "fieldtype": "Data", "width": 150},
        {"label": "Position No", "fieldname": "position_no", "fieldtype": "Data", "width": 120},
        {"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float", "width": 100},
        {"label": "Single Weight", "fieldname": "single_weight", "fieldtype": "Float", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 130},
        {"label": "View", "fieldname": "view", "fieldtype": "HTML", "width": 80},
    ]

    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("drawing_part"):
        conditions += " AND dp.name IN %(drawing_part)s"
        values["drawing_part"] = tuple(filters.get("drawing_part"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    query = f"""
        SELECT
            p.name AS project_name,
            ad.name AS drawing_number,
            dp.name AS drawing_part,
            dp.position_no,
            COALESCE(dp.quantity, 0) AS quantity,
            COALESCE(dp.single_weight, 0) AS single_weight,
            COALESCE(dp.total_weight, 0) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabAdd Drawing` ad ON ad.project_number = p.name
        LEFT JOIN `tabDrawing Part` dp ON dp.drawing_number = ad.name
        WHERE 1=1
        {conditions}
        ORDER BY p.name, ad.name, dp.position_no
    """

    data = frappe.db.sql(query, values, as_dict=True) or []

    # Add View button HTML to each row
    for row in data:
        # You can customize this button as per your need
        row['view'] = f'<button class="btn btn-xs btn-primary view-btn" data-drawing-part="{row.get("drawing_part")}" data-project="{row.get("project_name")}">View</button>'

    return columns, data
