# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FTStoreRevisionData(Document):
	pass


# @frappe.whitelist()
# def save_row_data(sr_no, project, item_name, item_count, quantity, lenght, width, total_weight):
#     import json
#     from frappe.utils import now_datetime

#     timestamp     = now_datetime().strftime("%d/%m/%Y (%H:%M:%S)")
#     id_timestamp  = now_datetime().strftime("%Y%m%d-%H%M%S")
#     clean_item    = item_name.replace(" ", "-").replace("/", "-")[:20]
#     doc_name      = f"{project}-{clean_item}-{id_timestamp}"

#     new_entry = {
#         "timestamp":     timestamp,
#         "total_entries": float(item_count  or 0),
#         "total_qty":     float(quantity    or 0),
#         "total_length":  float(lenght      or 0),
#         "total_width":   float(width       or 0),
#         "total_weight":  float(total_weight or 0)
#     }

#     existing = frappe.db.exists(
#         "FT Store Revision Data",
#         {
#             "project_number": project,
#             "item":           item_name
#         }
#     )

#     if existing:
#         doc = frappe.get_doc("FT Store Revision Data", existing)

#         try:
#             revision_log = json.loads(doc.revision_log or "[]")
#         except Exception:
#             revision_log = []

#         # Check if data actually changed
#         if revision_log:
#             last = revision_log[-1]
#             changed = (
#                 float(last.get("total_entries") or 0) != float(item_count    or 0) or
#                 float(last.get("total_qty")     or 0) != float(quantity      or 0) or
#                 float(last.get("total_length")  or 0) != float(lenght        or 0) or
#                 float(last.get("total_width")   or 0) != float(width         or 0) or
#                 float(last.get("total_weight")  or 0) != float(total_weight  or 0)
#             )
#             if not changed:
#                 return {"status": "success", "msg": "Data same hai, koi change nahi hua"}

#         revision_log.append(new_entry)

#         doc.sr_no          = sr_no
#         doc.total_entries  = item_count
#         doc.total_qty      = quantity
#         doc.total_length   = lenght
#         doc.total_width    = width
#         doc.total_weight   = total_weight
#         doc.revision_log   = json.dumps(revision_log)

#         doc.save(ignore_permissions=True)

#     else:
#         revision_log = [new_entry]

#         doc = frappe.get_doc({
#             "doctype":        "FT Store Revision Data",
#             "name":           doc_name,
#             "sr_no":          sr_no,
#             "project_number": project,
#             "item":           item_name,
#             "total_entries":  item_count,
#             "total_qty":      quantity,
#             "total_length":   lenght,
#             "total_width":    width,
#             "total_weight":   total_weight,
#             "revision_log":   json.dumps(revision_log)
#         })
#         doc.insert(ignore_permissions=True)

#     frappe.db.commit()
#     return {"status": "success", "msg": "✅ Data saved successfully!"}
