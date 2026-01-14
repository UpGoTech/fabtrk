# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

# import frappe

# def execute(filters=None):
#     filters = filters or {}

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data

# def get_columns():
#     return [
#         {"label": "Project", "fieldname": "name", "fieldtype": "Link", "options": "FT Project", "width": 130},
#         {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 120},
#         {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
#         {"label": "Project Type", "fieldname": "project_type", "fieldtype": "Link", "options": "FT Project Type", "width": 110},
#         {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 80},
#         {"label": "% Completed", "fieldname": "percentage_completed", "fieldtype": "Percent", "width": 120},
#         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "FT Customer", "width": 150},
#         {"label": "Shipping Scope", "fieldname": "shipping_scope", "fieldtype": "Data", "width": 130},
#         {"label": "Destination", "fieldname": "shipping_destination", "fieldtype": "Data", "width": 130},
#         {"label": "Total Weight (Kg)", "fieldname": "total_weight", "fieldtype": "Float", "width": 140},
#         {"label": "Bill Weight By", "fieldname": "bill_weight_by", "fieldtype": "Data", "width": 125},
#         {"label": "Start Date", "fieldname": "excepted_start_date", "fieldtype": "Date", "width": 120},
#         {"label": "End Date", "fieldname": "excepted_end_date", "fieldtype": "Date", "width": 120},
#         {"label": "Is Active", "fieldname": "is_active", "fieldtype": "Check", "width": 90},
		
#     ]

# def get_data(filters):
#     conditions = "1=1"
#     values = {}

#     if filters.get("project_name"):
#         conditions += " AND project_name LIKE %(project_name)s"
#         values["project_name"] = f"%{filters['project_name']}%"

#     if filters.get("status"):
#         conditions += " AND status = %(status)s"
#         values["status"] = filters["status"]

#     if filters.get("project_type"):
#         conditions += " AND project_type = %(project_type)s"
#         values["project_type"] = filters["project_type"]

#     if filters.get("customer"):
#         conditions += " AND customer = %(customer)s"
#         values["customer"] = filters["customer"]

#     if filters.get("is_active") is not None:
#         conditions += " AND is_active = %(is_active)s"
#         values["is_active"] = filters["is_active"]

#     if filters.get("from_date"):
#         conditions += " AND excepted_start_date >= %(from_date)s"
#         values["from_date"] = filters["from_date"]

#     if filters.get("to_date"):
#         conditions += " AND excepted_end_date <= %(to_date)s"
#         values["to_date"] = filters["to_date"]

#     return frappe.db.sql(f"""
#         SELECT
#             name, project_name, status, project_type, priority,
#             percentage_completed, customer, shipping_scope,
#             shipping_destination, total_weight, bill_weight_by,
#             excepted_start_date, excepted_end_date, is_active
#         FROM `tabFT Project`
#         WHERE {conditions}
#         ORDER BY excepted_start_date DESC
#     """, values, as_dict=True)


import frappe


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Project", "fieldname": "name", "fieldtype": "Link", "options": "FT Project", "width": 130},
        {"label": "Project Name", "fieldname": "project_name", "fieldtype": "Data", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Project Type", "fieldname": "project_type", "fieldtype": "Link", "options": "FT Project Type", "width": 110},
        {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 80},
        {"label": "% Completed", "fieldname": "percentage_completed", "fieldtype": "Percent", "width": 120},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "FT Customer", "width": 150},
        {"label": "Shipping Scope", "fieldname": "shipping_scope", "fieldtype": "Data", "width": 130},
        {"label": "Destination", "fieldname": "shipping_destination", "fieldtype": "Data", "width": 130},
        {"label": "Total Weight (Kg)", "fieldname": "total_weight", "fieldtype": "Float", "width": 140},
        {"label": "Bill Weight By", "fieldname": "bill_weight_by", "fieldtype": "Data", "width": 125},
        {"label": "Start Date", "fieldname": "excepted_start_date", "fieldtype": "Date", "width": 120},
        {"label": "End Date", "fieldname": "excepted_end_date", "fieldtype": "Date", "width": 120},
        {"label": "Is Active", "fieldname": "is_active", "fieldtype": "Check", "width": 90},
    ]


def get_data(filters):
    conditions = "1=1"
    values = {}

    # ✅ MULTI PROJECT FILTER (FIXED)
    if filters.get("project_name"):
        projects = filters.get("project_name")

        if isinstance(projects, list) and projects:
            conditions += " AND name IN %(projects)s"
            values["projects"] = tuple(projects)
        elif isinstance(projects, str):
            conditions += " AND name = %(project_name)s"
            values["project_name"] = projects

    if filters.get("status"):
        conditions += " AND status = %(status)s"
        values["status"] = filters["status"]

    if filters.get("project_type"):
        conditions += " AND project_type = %(project_type)s"
        values["project_type"] = filters["project_type"]

    if filters.get("customer"):
        conditions += " AND customer = %(customer)s"
        values["customer"] = filters["customer"]

    if filters.get("is_active") is not None:
        conditions += " AND is_active = %(is_active)s"
        values["is_active"] = filters["is_active"]

    if filters.get("from_date"):
        conditions += " AND excepted_start_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND excepted_end_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    return frappe.db.sql(
        f"""
        SELECT
            name, project_name, status, project_type, priority,
            percentage_completed, customer, shipping_scope,
            shipping_destination, total_weight, bill_weight_by,
            excepted_start_date, excepted_end_date, is_active
        FROM `tabFT Project`
        WHERE {conditions}
        ORDER BY excepted_start_date DESC
        """,
        values,
        as_dict=True,
    )
