# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe

def execute(filters=None):
    filters = filters or {}

    # ── Columns ──
    columns = [
        {
            "label": "Project",
            "fieldname": "project_number",
            "fieldtype": "Link",
            "options": "FT Project Stages",
            "width": 160,
        },
        {
            "label": "Stage",
            "fieldname": "stage",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Available",
            "fieldname": "available",
            "fieldtype": "Int",
            "width": 200,
            "align": "center",
        },
        {
            "label": "Addition",
            "fieldname": "addition",
            "fieldtype": "Int",
            "width": 190,
            "align": "center",
        },
        {
            "label": "Subtraction",
            "fieldname": "subtraction",
            "fieldtype": "Int",
            "width": 120,
            "align": "center",
        },
        {
            "label": "Completed",
            "fieldname": "completed",
            "fieldtype": "Int",
            "width": 190,
            "align": "center",
        },
        {
            "label": "Balance",
            "fieldname": "balance",
            "fieldtype": "Int",
            "width": 150,
            "align": "center",
        },
    ]

    # ── Conditions ──
    conditions = "WHERE 1=1"
    values = {}

    if filters.get("project_number"):
        conditions += " AND ps.name = %(project_number)s"
        values["project_number"] = filters["project_number"]

    if filters.get("stages"):
        conditions += " AND sm.name = %(stages)s"
        values["stages"] = filters["stages"]

    # ── Main Query ──
    # FT Project Stages → Child (stages list) → FT Transaction (addition, subtraction, completed)
    # Available = SUM(addition) - SUM(subtraction) - SUM(completed) so far
    # Balance   = Available - Completed (current period)
    raw_data = frappe.db.sql(f"""
        SELECT
            ps.name                         AS project_number,
            sm.name                         AS stage,
            psc.stages_key                  AS stages_key,

            -- Transactions aggregate karo per project+stage
            COALESCE(SUM(t.addition), 0)    AS addition,
            COALESCE(SUM(t.subtraction), 0) AS subtraction,
            COALESCE(SUM(t.completed), 0)   AS completed

        FROM `tabFT Project Stages` ps
        INNER JOIN `tabFT Project Stages Child` psc
            ON psc.parent = ps.name
        INNER JOIN `tabFT Stages Master` sm
            ON sm.name = psc.stages

        -- Transactions left join (ho sakta hai koi transaction na ho)
        LEFT JOIN `tabFT Transaction` t
            ON t.project_number = ps.name
            AND t.stages = psc.name

        {conditions}

        GROUP BY
            ps.name,
            sm.name,
            psc.stages_key

        ORDER BY
            ps.name ASC,
            psc.stages_key ASC
    """, values, as_dict=True)

    if not raw_data:
        return columns, []

    # ── Calculate Available & Balance ──
    # Available = cumulative: pichle saare addition - subtraction - completed
    # Balance   = Available (running total after this row's transactions)
    # Logic per project:
    #   available (start of stage) = previous balance
    #   balance   = available + addition - subtraction - completed

    data = []
    grand = {
        "addition": 0,
        "subtraction": 0,
        "completed": 0,
        "available": 0,
        "balance": 0,
    }

    # Group by project for running balance
    from collections import defaultdict
    project_rows = defaultdict(list)
    for row in raw_data:
        project_rows[row["project_number"]].append(row)

    for project, rows in project_rows.items():
        running_balance = 0  # har project ke liye fresh start

        for row in rows:
            addition    = int(row.get("addition")    or 0)
            subtraction = int(row.get("subtraction") or 0)
            completed   = int(row.get("completed")   or 0)

            available = running_balance  # is stage ke start mein kitna tha
            balance   = available + addition - subtraction - completed
            running_balance = balance   # agla stage yahan se start karega

            data.append({
                "project_number": project,
                "stage":          row["stage"],
                "available":      available,
                "addition":       addition,
                "subtraction":    subtraction,
                "completed":      completed,
                "balance":        balance,
                "is_total":       0,
            })

            grand["addition"]    += addition
            grand["subtraction"] += subtraction
            grand["completed"]   += completed
            grand["available"]   += available
            grand["balance"]     += balance

    # ── Grand Total Row ──
    data.append({
        "project_number": "TOTAL",
        "stage":          "",
        "available":      grand["available"],
        "addition":       grand["addition"],
        "subtraction":    grand["subtraction"],
        "completed":      grand["completed"],
        "balance":        grand["balance"],
        "is_total":       1,
    })

    return columns, data


