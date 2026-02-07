# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe

def execute(filters=None):
    filters = filters or {}
    filters = frappe._dict({
        "project_number": filters.get("project_number"),
        "drawing_number": filters.get("drawing_number"),
        "item": filters.get("item"),
    })

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 200},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Link", "options": "Add Drawing", "width": 150},
        {"label": "Drawing Part", "fieldname": "drawing_part", "fieldtype": "Link", "options": "FT Stock RM List", "width": 150},
        
        {"label": "Pos Number", "fieldname": "position_number", "fieldtype": "Data", "width": 90},
        {"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float", "width": 100},
        {"label": "Single Weight", "fieldname": "single_weight", "fieldtype": "Float", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 120},
        {"label": "View", "fieldname": "view", "fieldtype": "Button", "width": 80 }
    ]

    query = """
        SELECT
            p.name AS project_name,
            p.total_weight AS project_weight,
            ad.name AS drawing_number,
            ad.total_weight AS drawing_weight,     
            dp.position_number AS position_number,
            rm.computed_name AS drawing_part,
            dp.quantity,
            dp.single_weight,
            dp.total_weight AS part_weight

        FROM `tabFT Project` p
        LEFT JOIN `tabAdd Drawing` ad
            ON ad.project_number = p.name
            AND (%(drawing_number)s IS NULL OR ad.name = %(drawing_number)s)
        LEFT JOIN `tabDrawing Parts` dp
            ON dp.drawing_number = ad.name

        LEFT JOIN `tabFT Stock RM List` rm
            ON rm.name = dp.item
        WHERE (%(project_number)s IS NULL OR p.name = %(project_number)s)
          AND (%(item)s IS NULL OR dp.item = %(item)s)
        ORDER BY p.name, ad.name, dp.item
		
    """

    raw_data = frappe.db.sql(query, filters, as_dict=1) or []

    data = [{
        "project_name": d.project_name,
        "drawing_number": d.drawing_number,
        "drawing_part": d.drawing_part,

        "position_number": d.position_number,
        "quantity": d.quantity,
        "single_weight": d.single_weight,
        "total_weight": d.part_weight
    } for d in raw_data]

    # project_weight_total = sum(d.get("project_weight") or 0 for d in raw_data)
    project_weight_total = sum({d.project_name: d.project_weight or 0 for d in raw_data}.values())
    drawing_weight_total = sum(d.get("drawing_weight") or 0 for d in raw_data)
    part_weight_total = sum(d.get("part_weight") or 0 for d in raw_data)

    report_summary = [
        {"label": "Project Total Weight", "value": project_weight_total, "datatype": "Float"},
        {"label": "Drawing Number Weight", "value": drawing_weight_total, "datatype": "Float"},
        {"label": "Drawing Part Weight", "value": part_weight_total, "datatype": "Float"},
        {"label": "Sum of Total Weight", "value": project_weight_total + drawing_weight_total + part_weight_total, "datatype": "Float", "indicator": "Green"},
        {"label": "Balance", "value": 0, "datatype": "Float"},
        {"label": "Percent Achieved", "value": "100 %", "datatype": "Data"},
    ]

    data.append({
        "project_name": "Total",
        "drawing_number": "",
        "drawing_part": "",
        "position_number": "",
        "quantity": sum(d.get("quantity") or 0 for d in data),
        "single_weight": sum(d.get("single_weight") or 0 for d in data),
        "total_weight": part_weight_total
    })

    return columns, data, None, None, report_summary

@frappe.whitelist()
def get_parts(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT DISTINCT dp.item
        FROM `tabDrawing Parts` dp
        WHERE dp.drawing_number = %(drawing_number)s
          AND dp.item LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
    """, {
        "drawing_number": filters.get("drawing_number"),
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })
