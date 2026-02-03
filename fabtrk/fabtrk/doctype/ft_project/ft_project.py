# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FTProject(Document):
	pass



# #hidden hai    Add Drawings table ke liye  backend se Stock summnery me stock ke total show hoge with name
# import frappe
# from frappe.model.document import Document

# class FTProject(Document):

#     def validate(self):
#         self.update_stock_summary()

#     def update_stock_summary(self):
#         # clear old summary
#         self.set("stock_summary", [])

#         stock_map = {}

#         for row in self.add_drawings:
#             if not row.stock_item:
#                 continue

#             stock_map.setdefault(row.stock_item, 0)
#             stock_map[row.stock_item] += row.total_weight_kg or 0

#         # push into summary child table
#         for stock_item, total_weight in stock_map.items():
#             self.append("stock_summary", {
#                 "stock_item": stock_item,
#                 "total_weight_kg": total_weight
#             })
