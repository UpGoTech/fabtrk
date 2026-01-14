# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# Year Level Data (Main Report)
def get_year_data(filters):
    year = filters.get("year") if filters else None

    condition = ""
    values = {}

    if year:
        condition = "WHERE YEAR(date) = %(year)s"
        values["year"] = year

    rows = frappe.db.sql(f"""
        SELECT
            YEAR(date) AS year,
            SUM(total_weight) AS achieved
        FROM `tabFT Monthly Achievement`
        {condition}
        GROUP BY YEAR(date)
        ORDER BY year
    """, values, as_dict=True)

    # Total Target from FT Monthly Target
    target_rows = frappe.db.sql("""
        SELECT
            SUM(mt) AS target
        FROM `tabFT Monthly Target`
    """, as_dict=True)

    target = target_rows[0].target or 0

    data = []
    for r in rows:
        percent = (r.achieved / target * 100) if target else 0
        data.append({
            "year": r.year,
            "target": target,
            "achieved": r.achieved,
            "percent": round(percent, 1),
            "view": "View"
        })

    return data

# Month Drilldown (Year → Month)
@frappe.whitelist()
def get_month_data(year):
    rows = frappe.db.sql("""
        SELECT
            t.month AS month,
            SUM(t.mt) AS target,
            COALESCE(SUM(a.total_weight), 0) AS achieved,
            COUNT(a.name) AS entry
        FROM `tabFT Monthly Target` t
        LEFT JOIN `tabFT Monthly Achievement` a
            ON t.month = MONTHNAME(a.date)
           AND YEAR(a.date) = %s
        GROUP BY t.month
        ORDER BY t.month_sort
    """, year, as_dict=True)

    for r in rows:
        r["balance"] = (r.target or 0) - (r.achieved or 0)
        r["percent"] = (r.achieved / r.target * 100) if r.target else 0

    return rows

# Project Drilldown (Month → Project)
@frappe.whitelist()
def get_project_data(year, month):
    return frappe.db.sql("""
        SELECT
            a.project_number AS project,
            SUM(t.mt) AS project_target,
            SUM(a.total_weight) AS achieved,
            (SUM(t.mt) - SUM(a.total_weight)) AS balance,
            COUNT(a.name) AS entry_count
        FROM `tabFT Monthly Achievement` a
        INNER JOIN `tabFT Monthly Target` t
            ON t.month = %s
        WHERE YEAR(a.date) = %s
          AND MONTHNAME(a.date) = %s
        GROUP BY a.project_number
        ORDER BY a.project_number
    """, (month, year, month), as_dict=True)

# Project Entry Level (Final Drilldown)
@frappe.whitelist()
def get_project_entries(year, month, project):
    return frappe.db.sql("""
        SELECT
            project_number AS project,
            project_description,
            customer,
            target_amount AS project_target,
            total_weight AS achieved,
            (target_amount - total_weight) AS balance,
            date
        FROM `tabFT Monthly Achievement`
        WHERE YEAR(date) = %s
          AND MONTHNAME(date) = %s
          AND project_number = %s
        ORDER BY date
    """, (year, month, project), as_dict=True)





