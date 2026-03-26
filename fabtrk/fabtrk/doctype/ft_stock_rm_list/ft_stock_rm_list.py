# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.xlsxutils import make_xlsx

class FTStockRMList(Document):
	pass





@frappe.whitelist()
def export_with_value():

    # 👉 DocType ke all fields get karo
    meta = frappe.get_meta("FT Stock RM List")
    fieldnames = [f.fieldname for f in meta.fields]

    # 👉 DB se data fetch
    records = frappe.get_all(
        "FT Stock RM List",
        fields=fieldnames
    )

    # 👉 Header
    data = [fieldnames]

    for d in records:
        row = []

        for field in fieldnames:

            value = d.get(field)

            # 👉 Grade ka special handling (Link → Value)
            if field == "grade" and value:
                value = frappe.db.get_value(
                    "FT Material Grade Catalogues",
                    value,
                    "grade"
                )

            row.append(value)

        data.append(row)

    # 👉 Excel create
    xlsx_file = make_xlsx(data, "FT Stock RM List")

    # 👉 Download
    frappe.local.response.filename = "FT_Stock_RM_List.xlsx"
    frappe.local.response.filecontent = xlsx_file.getvalue()
    frappe.local.response.type = "binary"
    