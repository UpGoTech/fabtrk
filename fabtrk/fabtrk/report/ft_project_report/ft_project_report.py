# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe.utils import formatdate

def execute(filters=None):
    filters = filters or {}
    year = filters.get("year")
    project = filters.get("project")

    columns = get_columns()
    data = get_data(year, project)

    total_target = sum(d.get("target", 0) for d in data)
    total_achieved = sum(d.get("achieved", 0) for d in data)
    achieved_percent = round((total_achieved / total_target) * 100, 2) if total_target else 0

    def fmt(value):
        return "{:,.0f}".format(value) if isinstance(value, (int, float)) else value

    # New Bootstrap class logic
    if achieved_percent == 100:
        perc_class = "text-info"
    elif achieved_percent >= 75:
        perc_class = "text-success"
    elif achieved_percent >= 50:
        perc_class = "text-warning"
    else:
        perc_class = "text-danger"

    summary = [
        {"label": "Total Target (Kg)", "value": f'<span class="text-info">{fmt(total_target)}</span>'},
        {"label": "Total Achieved (Kg)", "value": f'<span class="text-warning">{fmt(total_achieved)}</span>'},
        {"label": "Balance", "value": f'<span class="text-danger">{fmt(total_target - total_achieved)}</span>'},
        {"label": "Achieved %", "value": f'<span class="{perc_class}">{achieved_percent}%</span>'}
    ]

    return columns, data, None, None, summary

def get_columns():
    return [
        {"label": "Month", "fieldname": "month_display", "width": 120},
        {"label": "Target (Kg)", "fieldname": "target", "width": 140},
        {"label": "Achieved (Kg)", "fieldname": "achieved", "width": 140},
        {"label": "Balance", "fieldname": "balance", "width": 120},
        {"label": "Achieved %", "fieldname": "achieved_percent", "width": 120},
        {"label": "View", "fieldname": "view", "width": 80},
    ]


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
            mt.select_month AS month_name,
            mt.year AS month_year,

            -- SUM of unique project targets per month
            SUM(DISTINCT ct.total_weight_of_project) AS target,

            -- Sum of all achieved values
            COALESCE(SUM(ma.total_weight_for_project_achieved), 0) AS achieved

        FROM `tabFT Monthly Target` mt
        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name

        LEFT JOIN `tabFT Monthly Achievement` ma
            ON ma.project_number = ct.project_number
            AND ma.select_month = mt.name
           

        {where}

        GROUP BY mt.name, mt.select_month, mt.year
        ORDER BY mt.year, FIELD(mt.select_month,
            'January','February','March','April','May','June','July','August','September','October','November','December')
    """, values, as_dict=True)

    for d in data:
        month_abbr = d["month_name"][:3]
        year_short = str(d["month_year"])[-2:]
        d["month_display"] = f"{month_abbr}-{year_short}"

        # Calculate balance
        d["balance"] = (d["target"] or 0) - (d["achieved"] or 0)

        # Achieved %
        d["achieved_percent"] = round((d["achieved"] / d["target"]) * 100, 2) if d["target"] else 0

        d["view"] = ""

    return data









@frappe.whitelist()
def get_month_details(year=None, project=None, month=None):
    if not month:
        return []

    return frappe.db.sql("""
        SELECT
            ct.project_number,
            ct.project_name,
            ct.customer_name,
            ct.description,
            ct.total_weight_of_project AS target_weight,

            COALESCE(ma.total_weight_for_project_achieved, 0) AS achieved_weight,

            (ct.total_weight_of_project -
             COALESCE(ma.total_weight_for_project_achieved, 0)) AS balance_weight,

            ma.achievement_type,

            ic.invoice_no,
            ic.invoice_weight,
            ic.invoice_amount,
            ic.attach_file

        FROM `tabFT Monthly Target` mt

        INNER JOIN `tabFT Month Target Childtable` ct
            ON ct.parent = mt.name

        LEFT JOIN `tabFT Monthly Achievement` ma
            ON ma.project_number = ct.project_number
            AND ma.select_month = mt.name

        LEFT JOIN `tabFT Invoice Childtable` ic
            ON ic.parent = ma.name
            AND ic.parenttype = 'FT Monthly Achievement'

        WHERE mt.name = %(month)s

          AND (
                IFNULL(%(year)s, '') = ''
                OR mt.year = %(year)s
          )

          AND (
                IFNULL(%(project)s, '') = ''
                OR ct.project_number = %(project)s
          )
    """, {
        "year": year,
        "project": project,
        "month": month
    }, as_dict=True)





# #3////////////////////////////isse are project number single show hore hai 1st table me
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

#     # First, fetch all data grouped by month + project_number
#     raw_data = frappe.db.sql(f"""
#         SELECT
#             mt.name AS month_id,
#             mt.select_month AS month_name,
#             mt.year AS month_year,
#             ct.project_number,
#             SUM(ct.total_weight_of_project) AS target,
#             COALESCE(SUM(ma.total_weight_for_project_achieved), 0) AS achieved

#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         LEFT JOIN `tabFT Monthly Achievement` ma
#             ON ma.project_number = ct.project_number
#             AND ma.select_month = mt.name
#             AND ma.year = mt.year

#         {where}

#         GROUP BY mt.name, mt.select_month, mt.year, ct.project_number
#         ORDER BY mt.year, FIELD(mt.select_month,
#             'January','February','March','April','May','June','July','August','September','October','November','December')
#     """, values, as_dict=True)

#     # Now, combine same project numbers within a month into one row
#     combined = {}
#     for d in raw_data:
#         key = (d["month_id"], d["project_number"])
#         if key not in combined:
#             combined[key] = d
#         else:
#             # Same project_number exists in same month → just sum target & achieved
#             combined[key]["target"] += d["target"] or 0
#             combined[key]["achieved"] += d["achieved"] or 0

#     # Prepare final list
#     data = []
#     for d in combined.values():
#         # Format month_display as "Mon-YY"
#         month_abbr = d["month_name"][:3]
#         year_short = str(d["month_year"])[-2:]
#         d["month_display"] = f"{month_abbr}-{year_short}"

#         # Calculate balance
#         d["balance"] = (d["target"] or 0) - (d["achieved"] or 0)

#         # Calculate Achieved %
#         d["achieved_percent"] = round((d["achieved"] / d["target"]) * 100, 2) if d["target"] else 0

#         # View button flag
#         d["view"] = ""  # Button rendered via JS

#         data.append(d)

#     # Sort by month_id for consistency
#     data.sort(key=lambda x: (x["month_year"], x["month_name"]))

#     return data

