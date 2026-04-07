# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FTTransaction(Document):
    pass


@frappe.whitelist()
def get_project_stages(doctype, txt, searchfield, start, page_len, filters):
    project = filters.get("project")

    return frappe.db.sql("""
        SELECT name
        FROM `tabFT Project Stages Child`
        WHERE parent = %(project)s
        AND name LIKE %(txt)s
        ORDER BY idx ASC
        LIMIT %(start)s, %(page_len)s
    """, {
        "project": project,
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })