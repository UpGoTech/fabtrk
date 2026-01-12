# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FTProjectMonth(Document):
	pass

# @frappe.whitelist()
# def get_sorted_months_for_project(doctype, txt, searchfield, start, page_len, filters):
#     months = frappe.db.sql("""
#         SELECT name
#         FROM `tabFT Month`
#         WHERE name LIKE %(txt)s
#         ORDER BY month_order+0 ASC
#         LIMIT %(start)s, %(page_len)s
#     """, {"txt": f"%{txt}%", "start": start, "page_len": page_len})
#     return [m[0] for m in months]
