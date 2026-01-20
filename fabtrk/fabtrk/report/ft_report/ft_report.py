# # # Copyright (c) 2026, UpGo Technologies and contributors
# # # For license information, please see license.txt

# import frappe


# # def execute(filters=None):
# # 	columns, data = [], []
# # 	return columns, data



import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():
    return [
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 120},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
        {"label": "Total Weight Achieved", "fieldname": "achieved_weight", "fieldtype": "Float", "width": 180},
        {"label": "Achieved %", "fieldname": "achieved_percent", "fieldtype": "Percent", "width": 120},
        {"label": "View", "fieldname": "view", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = ""
    if filters.get("year"):
        conditions = " AND year = %(year)s"

    data = frappe.db.sql(f"""
        SELECT
            t.year,
            t.total_weight,
            IFNULL(a.achieved_weight, 0) AS achieved_weight
        FROM (
            SELECT
                year,
                SUM(kg) AS total_weight
            FROM `tabFT Monthly Target`
            WHERE docstatus = 1
            {conditions}
            GROUP BY year
        ) t
        LEFT JOIN (
            SELECT
                year,
                SUM(total_weight_for_project_achieve) AS achieved_weight
            FROM `tabFT Monthly Achievement`
            WHERE docstatus = 1
            GROUP BY year
        ) a
        ON t.year = a.year
        ORDER BY t.year
    """, filters, as_dict=1)

    for row in data:
        row.total_weight = row.total_weight or 0
        row.achieved_weight = row.achieved_weight or 0

        if row.total_weight:
            row.achieved_percent = round(
                (row.achieved_weight / row.total_weight) * 100, 1
            )
        else:
            row.achieved_percent = 0

        row.view = "View"

    return data


def get_summary(data):
    total_weight = sum(d.total_weight for d in data)
    achieved_weight = sum(d.achieved_weight for d in data)
    balance = total_weight - achieved_weight
    percent = round((achieved_weight / total_weight) * 100, 1) if total_weight else 0

    return [
        {
            "label": "Total Weight",
            "value": total_weight,
            "datatype": "Float",
            "indicator": "Blue",
        },
        {
            "label": "Total Weight Achieved",
            "value": achieved_weight,
            "datatype": "Float",
            "indicator": "Green",
        },
        {
            "label": "Balance",
            "value": balance,
            "datatype": "Float",
            "indicator": "Red",
        },
        {
            "label": "Percent Achieved",
            "value": f"{percent} %",
            "datatype": "Data",
            "indicator": "Red" if percent < 50 else "Green",
        },
    ]


def get_chart(data):
    return {
        "data": {
            "labels": [d.year for d in data],
            "datasets": [
                {
                    "name": "Total Weight",
                    "values": [d.total_weight for d in data],
                },
                {
                    "name": "Achieved Weight",
                    "values": [d.achieved_weight for d in data],
                },
            ],
        },
        "type": "bar",
    }





@frappe.whitelist()
def get_year_wise_project_data(year):
    return frappe.db.sql("""
        SELECT
            project_number,
            project_name,
            customer_name,
            total_weight_for_project_achieve
        FROM `tabFT Monthly Achievement`
        WHERE docstatus = 1
          AND year = %s
        ORDER BY project_name
    """, year, as_dict=1)
