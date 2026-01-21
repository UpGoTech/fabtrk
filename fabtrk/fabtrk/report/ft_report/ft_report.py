# # # # # Copyright (c) 2026, UpGo Technologies and contributors
# # # # # For license information, please see license.txt

# # # import frappe


# # # # def execute(filters=None):
# # # # 	columns, data = [], []
# # # # 	return columns, data


# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters) or []
#     # return columns, data
#     # chart = get_chart(data)
#     summary = get_summary(data)
#     return columns, data, None, None, summary


# def get_columns():
#     return [
#         {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 120},
#         {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
#         {"label": "Achieved Weight", "fieldname": "achieved_weight", "fieldtype": "Float", "width": 150},
#         {"label": "Achieved %", "fieldname": "achieved_percent", "fieldtype": "Percent", "width": 120},
#         {
#             "label": "View",
#             "fieldname": "view",
#             "fieldtype": "HTML",   # 🔥 MUST
#             "width": 100
#         },
#     ]


# def get_data(filters=None):
#     conditions = ""
#     values = {}

#     if filters and filters.get("year"):
#         conditions = " AND year = %(year)s"
#         values["year"] = filters.get("year")

#     data = frappe.db.sql(f"""
#         SELECT
#             t.year,
#             t.total_weight,
#             IFNULL(a.achieved_weight, 0) AS achieved_weight
#         FROM (
#             SELECT
#                 year,
#                 SUM(kg) AS total_weight
#             FROM `tabFT Monthly Target`
#             WHERE docstatus = 1
#             {conditions}
#             GROUP BY year
#         ) t
#         LEFT JOIN (
#             SELECT
#                 year,
#                 SUM(total_weight_for_project_achieve) AS achieved_weight
#             FROM `tabFT Monthly Achievement`
#             WHERE docstatus = 1
#             {conditions}
#             GROUP BY year
#         ) a ON t.year = a.year
#         ORDER BY t.year
#     """, values, as_dict=True) or []

#     # 🔥 ENSURE LIST
#     if not data:
#         return []

#     for row in data:
#         row.total_weight = row.total_weight or 0
#         row.achieved_weight = row.achieved_weight or 0

#         row.achieved_percent = (
#             round((row.achieved_weight / row.total_weight) * 100, 1)
#             if row.total_weight else 0
#         )

#         row.view = f"""
#             <button class="btn btn-xs btn-primary ft-view-btn"
#                     data-year="{row.year}">
#                 View
#             </button>
#         """

#     return data


# def get_summary(data):
#     data = data or []

#     total_weight = sum((d.total_weight or 0) for d in data)
#     achieved_weight = sum((d.achieved_weight or 0) for d in data)
#     balance = total_weight - achieved_weight

#     percent = (
#         round((achieved_weight / total_weight) * 100, 1)
#         if total_weight else 0
#     )

#     return [
#         {
#             "label": "Total Weight",
#             "value": total_weight,
#             "datatype": "Float",
#             "indicator": "Blue",
#         },
#         {
#             "label": "Total Weight Achieved",
#             "value": achieved_weight,
#             "datatype": "Float",
#             "indicator": "Green",
#         },
#         {
#             "label": "Balance",
#             "value": balance,
#             "datatype": "Float",
#             "indicator": "Red",
#         },
#         {
#             "label": "Percent Achieved",
#             "value": f"{percent} %",
#             "datatype": "Data",
#             "indicator": "Red" if percent < 50 else "Green",
#         },
#     ]


# @frappe.whitelist()
# def get_year_wise_project_data(year):
#     return frappe.db.sql("""
#         SELECT
#             project_number,
#             project_name,
#             customer_name,
#             total_weight_for_project_achieve
#         FROM `tabFT Monthly Achievement`
#         WHERE docstatus = 1
#           AND year = %s
#     """, year, as_dict=True)




# # def get_chart(data):
# #     return {
# #         "data": {
# #             "labels": [d.year for d in data],
# #             "datasets": [
# #                 {
# #                     "name": "Total Weight",
# #                     "values": [d.total_weight for d in data],
# #                 },
# #                 {
# #                     "name": "Achieved Weight",
# #                     "values": [d.achieved_weight for d in data],
# #                 },
# #             ],
# #         },
# #         "type": "bar",
# #     }



import frappe

# ---------------- LEVEL 1 ----------------
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters) or []
    summary = get_summary(data)
    return columns, data, None, None, summary


def get_columns():
    return [
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
        {"label": "Achieved Weight", "fieldname": "achieved_weight", "fieldtype": "Float", "width": 150},
        {"label": "Achieved %", "fieldname": "achieved_percent", "fieldtype": "Percent", "width": 120},
        {"label": "View", "fieldname": "view", "fieldtype": "HTML", "width": 100},
    ]


def get_data(filters=None):
    conditions = ""
    values = {}

    if filters and filters.get("year"):
        conditions = " AND year = %(year)s"
        values["year"] = filters.get("year")

    data = frappe.db.sql(f"""
        SELECT
            t.year,
            t.total_weight,
            IFNULL(a.achieved_weight, 0) achieved_weight
        FROM (
            SELECT year, SUM(kg) total_weight
            FROM `tabFT Monthly Target`
            WHERE docstatus = 1 {conditions}
            GROUP BY year
        ) t
        LEFT JOIN (
            SELECT year, SUM(total_weight_for_project_achieve) achieved_weight
            FROM `tabFT Monthly Achievement`
            WHERE docstatus = 1 {conditions}
            GROUP BY year
        ) a ON t.year = a.year
        ORDER BY t.year
    """, values, as_dict=True)

    for d in data:
        d.achieved_percent = round((d.achieved_weight / d.total_weight) * 100, 1) if d.total_weight else 0
        d.view = f"""
            <button class="btn btn-xs btn-primary ft-view-btn" data-year="{d.year}">
                View
            </button>
        """
    return data


def get_summary(data):
    total = sum(d.total_weight for d in data)
    achieved = sum(d.achieved_weight for d in data)
    bal = total - achieved
    percent = round((achieved / total) * 100, 1) if total else 0

    return [
        {"label": "Total Weight", "value": total, "datatype": "Float"},
        {"label": "Achieved", "value": achieved, "datatype": "Float"},
        {"label": "Balance", "value": bal, "datatype": "Float"},
        {"label": "Percent", "value": f"{percent} %", "datatype": "Data"},
    ]


# ---------------- LEVEL 2 ----------------
@frappe.whitelist()
def get_month_wise_data(year):
    return frappe.db.sql("""
        SELECT
            MONTH(creation) AS month_no,
            DATE_FORMAT(creation, '%%M') AS month,
            SUM(total_weight_for_project_achieve) AS total_weight,
            SUM(total_weight_for_project_achieve) AS achieved_weight
        FROM `tabFT Monthly Achievement`
        WHERE docstatus = 1
          AND year = %s
        GROUP BY MONTH(creation)
        ORDER BY MONTH(creation)
    """, year, as_dict=True)


# ---------------- LEVEL 3 ----------------
@frappe.whitelist()
def get_project_wise_data(year, month):
    return frappe.db.sql("""
        SELECT
            project_name,
            SUM(total_weight_for_project_achieve) AS total_weight,
            SUM(total_weight_for_project_achieve) AS achieved_weight,
            COUNT(name) AS entry_count
        FROM `tabFT Monthly Achievement`
        WHERE docstatus = 1
          AND year = %s
          AND MONTH(creation) = %s
        GROUP BY project_name
    """, (year, month), as_dict=True)


# ---------------- LEVEL 4 ----------------
@frappe.whitelist()
def get_project_entry_data(project_name):
    return frappe.db.sql("""
        SELECT
            project_name,
            description,
            total_weight_for_project_achieve AS project_weight,
            total_weight_for_project_achieve AS achieved_weight,
            creation AS posting_date
        FROM `tabFT Monthly Achievement`
        WHERE docstatus = 1
          AND project_name = %s
        ORDER BY creation
    """, project_name, as_dict=True)

# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters) or []
#     summary = get_summary(data)
#     return columns, data, None, None, summary


# def get_columns():
#     return [
#         {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 120},
#         {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
#         {"label": "Achieved Weight", "fieldname": "achieved_weight", "fieldtype": "Float", "width": 150},
#         {"label": "Achieved %", "fieldname": "achieved_percent", "fieldtype": "Percent", "width": 120},
#         {"label": "View", "fieldname": "view", "fieldtype": "HTML", "width": 100},
#     ]


# def get_data(filters=None):
#     conditions = ""
#     values = {}

#     if filters and filters.get("year"):
#         conditions = " AND year = %(year)s"
#         values["year"] = filters.get("year")

#     data = frappe.db.sql(f"""
#         SELECT
#             t.year,
#             t.total_weight,
#             IFNULL(a.achieved_weight, 0) achieved_weight
#         FROM (
#             SELECT year, SUM(kg) total_weight
#             FROM `tabFT Monthly Target`
#             WHERE docstatus = 1 {conditions}
#             GROUP BY year
#         ) t
#         LEFT JOIN (
#             SELECT year, SUM(total_weight_for_project_achieve) achieved_weight
#             FROM `tabFT Monthly Achievement`
#             WHERE docstatus = 1 {conditions}
#             GROUP BY year
#         ) a ON t.year = a.year
#         ORDER BY t.year
#     """, values, as_dict=True)

#     for d in data:
#         d.achieved_percent = round(
#             (d.achieved_weight / d.total_weight) * 100, 1
#         ) if d.total_weight else 0

#         d.view = f"""
#             <button class="btn btn-xs btn-primary ft-view-btn"
#                 data-year="{d.year}">
#                 View
#             </button>
#         """

#     return data


# def get_summary(data):
#     total = sum(d.total_weight for d in data)
#     achieved = sum(d.achieved_weight for d in data)
#     bal = total - achieved
#     percent = round((achieved / total) * 100, 1) if total else 0

#     return [
#         {"label": "Total Weight", "value": total, "datatype": "Float"},
#         {"label": "Achieved", "value": achieved, "datatype": "Float"},
#         {"label": "Balance", "value": bal, "datatype": "Float"},
#         {"label": "Percent", "value": f"{percent} %", "datatype": "Data"},
#     ]


# # ---------------- LEVEL 2 ----------------
# @frappe.whitelist()
# def get_month_wise_data(year):
#     return frappe.db.sql("""
#         SELECT
#             MONTH(creation) AS month_no,
#             DATE_FORMAT(creation, '%%M') AS month,
#             SUM(total_weight_for_project_achieve) AS total_weight,
#             SUM(total_weight_for_project_achieve) AS achieved_weight
#         FROM `tabFT Monthly Achievement`
#         WHERE docstatus = 1
#           AND year = %s
#         GROUP BY MONTH(creation)
#         ORDER BY MONTH(creation)
#     """, year, as_dict=True)




# # ---------------- LEVEL 3 ----------------
# @frappe.whitelist()
# def get_project_wise_data(year, month):
#     return frappe.db.sql("""
#         SELECT
#             project_name,
#             SUM(total_weight_for_project_achieve) AS total_weight,
#             SUM(total_weight_for_project_achieve) AS achieved_weight,
#             COUNT(name) AS entry_count
#         FROM `tabFT Monthly Achievement`
#         WHERE docstatus = 1
#           AND year = %s
#           AND DATE_FORMAT(creation, '%%M') = %s
#         GROUP BY project_name
#     """, (year, month), as_dict=True)



# # ---------------- LEVEL 4 ----------------
# @frappe.whitelist()
# def get_project_entry_data(project_name):
#     return frappe.db.sql("""
#         SELECT
#             project_name,
#             description,
#             total_weight_for_project_achieve AS achieved_weight,
#             creation AS entry_date
#         FROM `tabFT Monthly Achievement`
#         WHERE docstatus = 1
#           AND project_name = %s
#         ORDER BY creation
#     """, project_name, as_dict=True)

