# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe.utils import formatdate


def execute(filters=None):
    filters = filters or {}

    month = filters.get("month")
    project = filters.get("project")

    columns = get_columns()
    data = get_data(month, project)

    total_target = sum(d.get("target", 0) for d in data)
    total_achieved = sum(d.get("achieved", 0) for d in data)
    achieved_percent = round((total_achieved / total_target) * 100, 2) if total_target else 0

    def fmt(value):
        return "{:,.0f}".format(value) if isinstance(value, (int, float)) else value

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



# def get_data(month=None, project=None):
#     conditions = []
#     values = {}

#     if month:
#         conditions.append("mt.name = %(month)s")
#         values["month"] = month

#     if project:
#         conditions.append("ct.project_number = %(project)s")
#         values["project"] = project

#     where = " AND ".join(conditions)
#     if where:
#         where = "WHERE " + where

#     data = frappe.db.sql(
#         f"""
#         SELECT
#             mt.name AS month_id,
#             mt.select_month AS month_name,
#             mt.year AS month_year,
#             SUM(ct.total_weight_of_project) AS target,
#             COALESCE(SUM(ma.total_weight_for_project_achieved), 0) AS achieved
#         FROM `tabFT Monthly Target` mt
#         INNER JOIN `tabFT Month Target Childtable` ct
#             ON ct.parent = mt.name
#         LEFT JOIN `tabFT Monthly Achievement` ma
#             ON ma.project_number = ct.project_number
#             AND ma.select_month = mt.name
#         {where}
#         GROUP BY mt.name
#         ORDER BY mt.year,
#             FIELD(
#                 mt.select_month,
#                 'January','February','March','April','May','June',
#                 'July','August','September','October','November','December'
#             )
#         """,
#         values,
#         as_dict=True,
#     )

#     for d in data:
#         d["month_display"] = f"{d['month_name'][:3]}-{str(d['month_year'])[-2:]}"
#         d["balance"] = (d["target"] or 0) - (d["achieved"] or 0)
#         d["achieved_percent"] = round((d["achieved"] / d["target"]) * 100, 2) if d["target"] else 0
#         d["view"] = ""

#     return data

def get_data(month=None, project=None):
    conditions = []
    values = {}

    if month:
        conditions.append("t.month_id = %(month)s")
        values["month"] = month

    if project:
        conditions.append("t.project_number = %(project)s")
        values["project"] = project

    where = " AND ".join(conditions)
    if where:
        where = "WHERE " + where

    data = frappe.db.sql(
        f"""
        SELECT
            t.month_id,
            t.month_name,
            t.month_year,
            SUM(t.project_target) AS target,
            COALESCE(SUM(a.project_achieved), 0) AS achieved
        FROM (
            /* ✅ UNIQUE TARGET PER PROJECT */
            SELECT
                mt.name AS month_id,
                mt.select_month AS month_name,
                mt.year AS month_year,
                ct.project_number,
                MAX(ct.total_weight_of_project) AS project_target
            FROM `tabFT Monthly Target` mt
            INNER JOIN `tabFT Month Target Childtable` ct
                ON ct.parent = mt.name
            GROUP BY mt.name, ct.project_number
        ) t
        LEFT JOIN (
            /* ✅ AGGREGATED ACHIEVEMENT PER PROJECT */
            SELECT
                select_month,
                project_number,
                SUM(total_weight_for_project_achieved) AS project_achieved
            FROM `tabFT Monthly Achievement`
            GROUP BY select_month, project_number
        ) a
            ON a.select_month = t.month_id
            AND a.project_number = t.project_number
        {where}
        GROUP BY t.month_id
        ORDER BY t.month_year,
            FIELD(
                t.month_name,
                'January','February','March','April','May','June',
                'July','August','September','October','November','December'
            )
        """,
        values,
        as_dict=True,
    )

    for d in data:
        d["month_display"] = f"{d['month_name'][:3]}-{str(d['month_year'])[-2:]}"
        d["balance"] = (d["target"] or 0) - (d["achieved"] or 0)
        d["achieved_percent"] = round(
            (d["achieved"] / d["target"]) * 100, 2
        ) if d["target"] else 0
        d["view"] = ""

    return data


@frappe.whitelist()
def get_month_details(project=None, month=None):

    # ✅ Month blank → latest month
    if not month:
        res = frappe.db.sql(
            """
            SELECT name
            FROM `tabFT Monthly Target`
            ORDER BY
                year DESC,
                FIELD(
                    select_month,
                    'January','February','March','April','May','June',
                    'July','August','September','October','November','December'
                ) DESC
            LIMIT 1
            """,
            as_dict=False
        )
        month = res[0][0] if res else None

    if not month:
        return []

    return frappe.db.sql(
        """
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
            ic.attach_file,
            CONCAT(LEFT(mt.select_month,3), '-', RIGHT(mt.year,2)) AS month_display
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
            IFNULL(%(project)s, '') = ''
            OR ct.project_number = %(project)s
        )
        """,
        {"project": project, "month": month},
        as_dict=True,
    )


@frappe.whitelist()
def get_sorted_months(*args, **kwargs):
    res = frappe.db.sql(
        """
        SELECT CONCAT(LEFT(select_month,3), '-', RIGHT(year,2)) AS month_display
        FROM `tabFT Monthly Target`
        ORDER BY year DESC,
            FIELD(select_month,
                'January','February','March','April','May','June',
                'July','August','September','October','November','December') DESC
        """,
        as_dict=False
    )
    # return [(value, title), ...] but make both same so no double display
    return [(r[0], r[0]) for r in res]

##### // all monh+year show
@frappe.whitelist()
def get_all_months(*args, **kwargs):
    # Start aur end year define karo
    start_year = 2024
    end_year = 2026
    
    months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    
    all_months = []
    for year in range(start_year, end_year + 1):
        for month in months:
            month_display = f"{month[:3]}-{str(year)[-2:]}"  # e.g. Mar-26
            all_months.append((month_display, month_display))  # value, title same
    
    # Descending order (latest month first)
    all_months.reverse()
    
    return all_months






