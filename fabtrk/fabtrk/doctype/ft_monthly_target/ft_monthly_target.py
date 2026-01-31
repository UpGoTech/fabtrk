# # # Copyright (c) 2026, UpGo Technologies and contributors
# # # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class FTMonthlyTarget(Document):
# 	pass


import frappe
from frappe.model.document import Document

class FTMonthlyTarget(Document):
    def autoname(self):
        if self.select_month and self.year:
            month = self.select_month[:3].upper()
            year = str(self.year)[-2:]
            self.name = f"{month}-{year}"


@frappe.whitelist()
def get_used_months(doctype, txt, searchfield, start, page_len, filters):
    year = filters.get("year")
    current_doc = filters.get("current_doc")

    if not year:
        return []

    values = {"year": year}
    cond = ""

    if current_doc:
        cond = "AND name != %(current_doc)s"
        values["current_doc"] = current_doc

    # 🔹 Already used months (same logic as before)
    used = frappe.db.sql(f"""
        SELECT select_month
        FROM `tabFT Monthly Target`
        WHERE year = %(year)s
        {cond}
    """, values)

    used_months = [d[0] for d in used]

    # 🔥 FIX: Sirf FT Month ke months + correct sorting
    ft_months = frappe.db.sql("""
        SELECT name
        FROM `tabFT Month`
        ORDER BY FIELD(
            name,
            'January','February','March','April','May','June',
            'July','August','September','October','November','December'
        )
    """)

    txt = (txt or "").lower().strip()
    result = []

    for (month,) in ft_months:
        # already used month hide
        if month in used_months:
            continue

        # search text filter
        if not txt or txt in month.lower():
            result.append([month])

    return result


# 🔹 Project balance
@frappe.whitelist()
def get_project_balance(project):
    total = frappe.db.get_value(
        "FT Project", project, "total_weight"
    ) or 0

    used = frappe.db.sql("""
        SELECT SUM(total_weight_of_project)
        FROM `tabFT Month Target Childtable`
        WHERE project_number = %s
          AND docstatus = 1
    """, project)[0][0] or 0

    return total - used
















# ###NOTE:====== is code me all month ke liye hardcode kiya tha jisse jo month ft month doctype me entry bhi nhi hai  vo year selct krne pr sorting me all month show hora tha pr jis month ki entery nhi hai ftmonthdoctype me vo selct nhi hora tha
# # 🔹 Month duplicate prevent (year wise)
# # @frappe.whitelist()
# #def get_used_months(doctype, txt, searchfield, start, page_len, filters):
##     year = filters.get("year")
##     current_doc = filters.get("current_doc")

##     values = {"year": year}
##     cond = ""

##     if current_doc:
##         cond = "AND name != %(current_doc)s"
##         values["current_doc"] = current_doc

##     used = frappe.db.sql(f"""
##         SELECT select_month
##         FROM `tabFT Monthly Target`
##         WHERE year = %(year)s
##         {cond}
##     """, values)

##     used_months = [d[0] for d in used]

##     month_order = [
##         "January", "February", "March", "April", "May", "June",
##         "July", "August", "September", "October", "November", "December"
##     ]

##     result = []
##     txt = (txt or "").lower().strip()

##     for m in month_order:
##         if m in used_months:
##             continue

##         if not txt or txt in m.lower():
##             result.append([m])

##     ## 🔥 IMPORTANT FIX → return ALL months at once
##     return result[:12]
# ###NOTE:====== is code me all month ke liye hardcode kiya tha jisse jo month ft month doctype me entry bhi nhi hai  vo year selct krne pr sorting me all month show hora tha pr jis month ki entery nhi hai ftmonthdoctype me vo selct nhi hora tha


