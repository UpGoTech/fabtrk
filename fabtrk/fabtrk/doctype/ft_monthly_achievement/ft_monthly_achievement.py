# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document


# class FTMonthlyAchievement(Document):
# 	pass



import frappe


@frappe.whitelist()
def get_months_by_year(doctype, txt, searchfield, start, page_len, filters):
    year = filters.get("year")

    if not year:
        return []

    # Usi year ke months jo FT Monthly Target me hain
    months = frappe.db.sql("""
        SELECT DISTINCT select_month
        FROM `tabFT Monthly Target`
        WHERE year = %(year)s
        ORDER BY FIELD(select_month,
            'January','February','March','April','May','June',
            'July','August','September','October','November','December'
        )
    """, {"year": year})

    result = []
    txt = (txt or "").lower()

    for m in months:
        # 🔥 typing optional
        if not txt or txt in m[0].lower():
            result.append([m[0]])

    return result[start:start + page_len]


@frappe.whitelist()
def get_projects_by_year_month(doctype, txt, searchfield, start, page_len, filters):
    year = filters.get("year")
    month = filters.get("month")

    if not year or not month:
        return []

    data = frappe.db.sql("""
        SELECT DISTINCT
            ct.project_number
        FROM `tabFT Monthly Target` mt
        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name
        WHERE mt.year = %(year)s
          AND mt.select_month = %(month)s
          AND ct.project_number LIKE %(txt)s
        ORDER BY ct.project_number
    """, {
        "year": year,
        "month": month,
        "txt": f"%{txt}%"
    })

    return data



@frappe.whitelist()
def get_projects_by_month(doctype, txt, searchfield, start, page_len, filters):
    month = filters.get("month")

    if not month:
        return []

    return frappe.db.sql("""
        SELECT DISTINCT
            ct.project_number
        FROM `tabFT Monthly Target` mt
        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name
        WHERE mt.select_month = %(month)s
          AND ct.project_number LIKE %(txt)s
        ORDER BY ct.project_number
    """, {
        "month": month,
        "txt": f"%{txt}%"
    })
