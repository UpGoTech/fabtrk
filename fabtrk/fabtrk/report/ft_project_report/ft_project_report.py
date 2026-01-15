# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data






import frappe

# def execute(filters=None):
#     filters = filters or {}
#     year = filters.get("year")
#     project = filters.get("project")

#     columns = get_columns()
#     data = get_data(year, project)

#     total_target = sum(d.target for d in data)
#     total_achieved = sum(d.achieved for d in data)

#     summary = [
#         {"label": "Total Target (Kg)", "value": total_target},
#         {"label": "Total Achieved (Kg)", "value": total_achieved},
#         {"label": "Balance", "value": total_target - total_achieved}
#     ]

#     return columns, data, None, None, summary
def execute(filters=None):
    filters = filters or {}
    year = filters.get("year")
    project = filters.get("project")

    columns = get_columns()
    data = get_data(year, project)

    total_target = sum(d.get("target", 0) for d in data)
    total_achieved = sum(d.get("achieved", 0) for d in data)

    summary = [
        {"label": "Total Target (Kg)", "value": total_target},
        {"label": "Total Achieved (Kg)", "value": total_achieved},
        {"label": "Balance", "value": total_target - total_achieved}
    ]

    return columns, data, None, None, summary


def get_columns():
    return [
        {"label": "Month", "fieldname": "month_display", "width": 120},
        {"label": "Target (Kg)", "fieldname": "target", "width": 140},
        {"label": "Achieved (Kg)", "fieldname": "achieved", "width": 140},
        {"label": "Balance", "fieldname": "balance", "width": 120},
        {"label": "View", "fieldname": "view", "width": 80},
    ]


# def get_data(year=None, project=None):
#     conditions = []
#     values = {}

#     if year:
#         conditions.append("mt.year = %(year)s")
#         values["year"] = year

#     if project:
#         conditions.append("ct.project_number = %(project)s")
#         values["project"] = project

#     where = " AND ".join(conditions)
#     if where:
#         where = "WHERE " + where

#     data = frappe.db.sql(f"""
#         SELECT
#             mt.select_month AS month_raw,
#             SUM(ct.total_weight_of_project) AS target,
#             COALESCE(SUM(ma.total_weight_for_project_achieve),0) AS achieved
#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         LEFT JOIN `tabFT Monthly Achievement` ma
#             ON ma.project_number = ct.project_number
#             AND ma.select_month = mt.name
#         {where}
#         GROUP BY mt.select_month
#     """, values, as_dict=True)

#     for d in data:
#         d.month_display = d.month_raw
#         d.balance = (d.target or 0) - (d.achieved or 0)
#         d.view = ""

#     return data
def get_data(year=None, project=None):
    conditions = []
    values = {}

    if year:
        conditions.append("mt.year = %(year)s")
        values["year"] = year

    if project:
        conditions.append("ct.project_number = %(project)s")
        values["project"] = project

    where = " AND ".join(conditions)
    if where:
        where = "WHERE " + where

    data = frappe.db.sql(f"""
        SELECT
            mt.name AS month_id,
            mt.select_month AS month_display,
            SUM(ct.total_weight_of_project) AS target,
            COALESCE(SUM(ma.total_weight_for_project_achieve), 0) AS achieved
        FROM `tabFT Monthly Target` mt
        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name
        LEFT JOIN `tabFT Monthly Achievement` ma
            ON ma.project_number = ct.project_number
            AND ma.select_month = mt.name
        {where}
        GROUP BY mt.name, mt.select_month
    """, values, as_dict=True)

    for d in data:
        d["balance"] = (d["target"] or 0) - (d["achieved"] or 0)
        d["view"] = ""

    return data


# @frappe.whitelist()
# def get_month_details(year=None, project=None, month=None):
#     return frappe.db.sql("""
#         SELECT
#             ct.project_number AS project,
#             ct.total_weight_of_project AS target,
#             ma.total_weight_for_project_achieve AS achieved,
#             (ct.total_weight_of_project -
#              COALESCE(ma.total_weight_for_project_achieve,0)) AS balance,
#             ic.invoice_no,
#             ic.attach_file AS attachment
#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         LEFT JOIN `tabFT Monthly Achievement` ma
#             ON ma.project_number = ct.project_number
#             AND ma.select_month = mt.name
#         LEFT JOIN `tabFT Invoice Childtable` ic
#             ON ic.parent = ma.name
#         WHERE mt.year = %(year)s
#           AND mt.select_month = %(month)s
#           AND (%(project)s IS NULL OR ct.project_number = %(project)s)
#     """, {
#         "year": year,
#         "month": month,
#         "project": project
#     }, as_dict=True)
@frappe.whitelist()
def get_month_details(year=None, project=None, month=None):
    if not month:
        return []

    return frappe.db.sql("""
        SELECT
            ct.project_number AS project,
            ct.total_weight_of_project AS target,

            COALESCE(ma.total_weight_for_project_achieve, 0) AS achieved,

            (ct.total_weight_of_project -
             COALESCE(ma.total_weight_for_project_achieve, 0)) AS balance,

            ic.invoice_no,
            ic.attach_file AS attachment

        FROM `tabFT Monthly Target` mt

        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name

        LEFT JOIN `tabFT Monthly Achievement` ma
            ON ma.project_number = ct.project_number
            AND ma.select_month = mt.name

        LEFT JOIN `tabFT Invoice Childtable` ic
            ON ic.parenttype = 'FT Monthly Achievement'
            AND ic.parent = ma.name

        WHERE mt.name = %(month)s
          AND mt.year = %(year)s
          AND (%(project)s IS NULL OR ct.project_number = %(project)s)
    """, {
        "year": year,
        "month": month,
        "project": project
    }, as_dict=True)
