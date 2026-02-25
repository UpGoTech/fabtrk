# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document


# class FTDrawingParts(Document):
# 	pass



import frappe

records = frappe.get_all("FT Drawing Parts", fields=["name", "item"])

for r in records:
    if r.item:
        item_id = frappe.db.get_value(
            "FT Stock RM List",
            {"computed_name": r.item},
            "name"
        )
        
        if item_id:
            frappe.db.set_value(
                "FT Drawing Parts",
                r.name,
                "item",
                item_id
            )
        else:
            print("Not Found:", r.item)

frappe.db.commit()
print("Conversion Completed")

