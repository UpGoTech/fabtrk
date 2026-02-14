# import frappe

# def execute(filters=None):
#     filters = filters or {}
#     filters = frappe._dict({
#         "project_number": filters.get("project_number"),
#         "drawing_number": filters.get("drawing_number"),
#         "item": filters.get("item"),
#     })

#     # -------------------------
#     # COLUMNS
#     # -------------------------
#     columns = [
#         {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 130},
#         {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Link", "options": "Add Drawing", "width": 200},
#         {"label": "Unit weight", "fieldname": "unit_weight", "fieldtype": "Float", "width": 200},
#         {"label": "Required Qty", "fieldname": "quantity", "fieldtype": "Int", "width": 200},
#         {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 120},
#     ]

#     # -------------------------
#     # RAW DATA FROM DRAWINGS
#     # -------------------------
#     query = """
#         SELECT
#             ad.project_number AS project_name,
#             ad.name AS drawing_number,
#             ad.unit_weight,
#             ad.quantity,
#             ad.total_weight
#         FROM `tabAdd Drawing` ad
#         WHERE (%(project_number)s IS NULL OR ad.project_number = %(project_number)s)
#           AND (%(drawing_number)s IS NULL OR ad.name = %(drawing_number)s)
#         ORDER BY ad.project_number, ad.name
#     """

#     raw_data = frappe.db.sql(query, filters, as_dict=1) or []

#     # -------------------------
#     # DATA TABLE
#     # -------------------------
#     data = []
#     for d in raw_data:
#         data.append({
#             "project_name": d.project_name,
#             "drawing_number": d.drawing_number,
#             "unit_weight": d.unit_weight,
#             "quantity": d.quantity,
#             "total_weight": d.total_weight
#         })

#     # -------------------------
#     # SUMMARY CALCULATIONS
#     # -------------------------
#     project_names = {d.project_name for d in raw_data if d.project_name}

#     # Total Projects
#     total_projects = len(project_names)

#     # Total Drawings
#     total_no_of_drawings = len({d.drawing_number for d in raw_data if d.drawing_number})

#     # Total Weight as per Project (sum from Project Doctype)
#     if project_names:
#         project_list = "', '".join(project_names)
#         total_weight_as_per_project = frappe.db.sql(f"""
#             SELECT SUM(`total_weight`) 
#             FROM `tabFT Project`
#             WHERE name IN ('{project_list}')
#         """, as_list=1)[0][0] or 0
#     else:
#         total_weight_as_per_project = 0

#     # Total Weight as per Drawing (sum of drawings)
#     total_weight_as_per_drawing = sum(d.total_weight or 0 for d in raw_data)

#     # -------------------------
#     # REPORT SUMMARY
#     # -------------------------
#     report_summary = [
#         {"label": "Total Projects", "value": total_projects, "datatype": "Int"},
#         {"label": "Total No of Drawings", "value": total_no_of_drawings, "datatype": "Int"},
#         {"label": "Total Weight as per Project", "value": total_weight_as_per_project, "datatype": "Float"},
#         {"label": "Total Weight as per Drawing", "value": total_weight_as_per_drawing, "datatype": "Float"},
#     ]

#     return columns, data, None, None, report_summary







# this code for multi select filter filed
import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 130},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Data","width": 200},
        {"label": "Unit Weight", "fieldname": "unit_weight", "fieldtype": "Float", "width": 150},
        {"label": "Required Qty", "fieldname": "quantity", "fieldtype": "Int", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
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
            IFNULL(ad.unit_weight, 0) AS unit_weight,
            IFNULL(ad.quantity, 0) AS quantity,
            IFNULL(ad.total_weight, 0) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabAdd Drawing` ad
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
        {"label": "Total Projects", "value": total_projects, "datatype": "Int"},
        {"label": "Total No of Drawings", "value": total_no_of_drawings, "datatype": "Int"},
        {"label": "Total Weight as per Project", "value": total_weight_as_per_project, "datatype": "Float"},
        {"label": "Total Weight as per Drawing", "value": total_weight_as_per_drawing, "datatype": "Float"},
    ]

    return columns, raw_data, None, None, report_summary



