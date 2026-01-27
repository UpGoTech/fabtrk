# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document


# class FTMonthlyAchievement(Document):
# 	pass


# // 19-1-26

# import frappe
# @frappe.whitelist()
# def get_months_by_year(doctype, txt, searchfield, start, page_len, filters):
#     year = filters.get("year")

#     if not year:
#         return []

#     # Usi year ke months jo FT Monthly Target me hain
#     months = frappe.db.sql("""
#         SELECT DISTINCT select_month
#         FROM `tabFT Monthly Target`
#         WHERE year = %(year)s
#         ORDER BY FIELD(select_month,
#             'January','February','March','April','May','June',
#             'July','August','September','October','November','December'
#         )
#     """, {"year": year})

#     result = []
#     txt = (txt or "").lower()

#     for m in months:
#         # 🔥 typing optional
#         if not txt or txt in m[0].lower():
#             result.append([m[0]])

#     return result[start:start + page_len]

# @frappe.whitelist()
# def get_projects_by_year_month(doctype, txt, searchfield, start, page_len, filters):
#     year = filters.get("year")
#     month = filters.get("month")

#     if not year or not month:
#         return []

#     data = frappe.db.sql("""
#         SELECT DISTINCT
#             ct.project_number
#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         WHERE mt.year = %(year)s
#           AND mt.select_month = %(month)s
#           AND ct.project_number LIKE %(txt)s
#         ORDER BY ct.project_number
#     """, {
#         "year": year,
#         "month": month,
#         "txt": f"%{txt}%"
#     })

#     return data

# @frappe.whitelist()
# def get_projects_by_month(doctype, txt, searchfield, start, page_len, filters):
#     month = filters.get("month")

#     if not month:
#         return []

#     return frappe.db.sql("""
#         SELECT DISTINCT
#             ct.project_number
#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         WHERE mt.select_month = %(month)s
#           AND ct.project_number LIKE %(txt)s
#         ORDER BY ct.project_number
#     """, {
#         "month": month,
#         "txt": f"%{txt}%"
#     })

# // 19-1-26










import frappe
from frappe.model.document import Document

class FTMonthlyAchievement(Document):

    def validate(self):
        # ❌ Block save if value is 0 or empty
        if not self.total_weight_for_project_achieve or self.total_weight_for_project_achieve <= 0:
            frappe.throw(
                "❌ Total Weight for Project Achieve must be greater than 0"
            )

        # ✅ Run existing validation
        self.validate_project_weight()


    def validate_project_weight(self):
        if not self.project_number or not self.select_month or not self.year:
            return

        # ✅ Use Month Total Weight of Project instead of Actual Project Total Weight
        if not self.month_total_weight_of_project:
            frappe.throw(
                "❌ Month Total Weight of Project is required before saving."
            )

        actual_weight = float(self.month_total_weight_of_project)

        # Already achieved weight
        achieved_weight = frappe.db.sql("""
            SELECT SUM(total_weight_for_project_achieve)
            FROM `tabFT Monthly Achievement`
            WHERE project_number = %(project)s
              AND select_month = %(month)s
              AND year = %(year)s
              AND name != %(name)s
        """, {
            "project": self.project_number,
            "month": self.select_month,
            "year": self.year,
            "name": self.name or ""
        })[0][0] or 0

        achieved_weight = float(achieved_weight)
        balance = actual_weight - achieved_weight

        # Full project check
        if balance <= 0:
            frappe.throw(
                f"""
                🎉 This project is already fully achieved.<br><br>
                <b>Month Total Weight of Project:</b> {actual_weight}<br>
                <b>Already Achieved:</b> {achieved_weight}
                """
            )

        # Over-entry check
        if self.total_weight_for_project_achieve > balance:
            frappe.throw(
                f"""
                ❌ Invalid Entry<br><br>
                <b>Month Total Weight of Project:</b> {actual_weight}<br>
                <b>Already Achieved:</b> {achieved_weight}<br>
                <b>Remaining Balance:</b> {balance}<br><br>
                👉 You can enter maximum <b>{balance}</b>
                """
            )

        # Optional info message
        frappe.msgprint(
            f"""
            ✅ Entry Accepted<br><br>
            <b>Remaining Balance After Save:</b>
            {balance - self.total_weight_for_project_achieve}
            """,
            alert=True
        )

@frappe.whitelist()
def check_project_weight(year, select_month, project_number, current_value, docname=None, actual_weight=None):
    # Use passed month_total_weight_of_project from JS
    if actual_weight is None:
        actual_weight = frappe.db.get_value(
            "FT Monthly Achievement",
            {"project_number": project_number, "select_month": select_month, "year": year},
            "month_total_weight_of_project"
        )
        if not actual_weight:
            return {"status": "error", "message": "Month Total Weight of Project not found."}

    actual_weight = float(actual_weight)

    achieved_weight = frappe.db.sql("""
        SELECT SUM(total_weight_for_project_achieve)
        FROM `tabFT Monthly Achievement`
        WHERE project_number = %(project)s
          AND select_month = %(month)s
          AND year = %(year)s
          AND name != %(name)s
    """, {
        "project": project_number,
        "month": select_month,
        "year": year,
        "name": docname or ""
    })[0][0] or 0

    achieved_weight = float(achieved_weight)
    balance = actual_weight - achieved_weight
    current_value = float(current_value or 0)

    if balance <= 0:
        return {"status": "full", "actual": actual_weight, "achieved": achieved_weight, "balance": 0}

    if current_value > balance:
        return {"status": "exceed", "actual": actual_weight, "achieved": achieved_weight, "balance": balance}

    return {"status": "ok", "actual": actual_weight, "achieved": achieved_weight, "balance": balance - current_value}

# //////////////////////////// year pe  month filter
# @frappe.whitelist()
# def get_months_by_year(doctype, txt, searchfield, start, page_len, filters):
#     year = filters.get("year")

#     if not year:
#         return []

#     return frappe.db.sql("""
#         SELECT name
#         FROM `tabFT Monthly Target`
#         WHERE year = %(year)s
#           AND name LIKE %(txt)s
#         ORDER BY name
#     """, {
#         "year": year,
#         "txt": f"%{txt}%"
#     })

# //////////////////// year pe  month filter

# seperat month sort
@frappe.whitelist()
def get_months_by_year(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""
        SELECT name
        FROM `tabFT Monthly Target`
        WHERE name LIKE %(txt)s
        ORDER BY
            year DESC,
            FIELD(select_month,
                'December','November','October','September','August','July',
                'June','May','April','March','February','January'
            )
    """, {
        "txt": f"%{txt}%"
    })

# seperat month sort


#### ////project number filter after select month
@frappe.whitelist()
def get_projects_by_year_month(doctype, txt, searchfield, start, page_len, filters):
    year = filters.get("year")
    month_docname = filters.get("month")  # FT Monthly Target NAME

    if not year or not month_docname:
        return []

    return frappe.db.sql("""
        SELECT DISTINCT ct.project_number
        FROM `tabFT Month Target Childtable` ct
        WHERE ct.parent = %(parent)s
          AND ct.project_number LIKE %(txt)s
        ORDER BY ct.project_number
    """, {
        "parent": month_docname,
        "txt": f"%{txt}%"
    })


# fetch target weight amount
@frappe.whitelist()
def get_monthly_total_weight(month_target, project_number):
    """
    Returns total weight of the selected project from FT Monthly Target child table
    """
    res = frappe.db.sql("""
        SELECT ct.total_weight_of_project
        FROM `tabFT Month Target Childtable` ct
        WHERE ct.parent = %(parent)s
          AND ct.project_number = %(project_number)s
    """, {
        "parent": month_target,
        "project_number": project_number
    })

    if res:
        return res[0][0]
    else:
        return 0


