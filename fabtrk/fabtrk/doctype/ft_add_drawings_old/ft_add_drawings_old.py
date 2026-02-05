# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document


# class FTAddDrawingsOld(Document):
# 	pass



import frappe
from frappe.model.document import Document


class FTAddDrawingsOld(Document):
    pass


@frappe.whitelist()
def get_available_drawings(doctype, txt, searchfield, start, page_len, filters):
    po_number = filters.get("po_number")

    used = frappe.get_all(
        "FT Add Drawings",
        filters={"po_number": po_number},
        pluck="select_drawing_no",
        ignore_permissions=True
    )

    drawings = frappe.get_all(
        "FT Po List  Child",
        filters={
            "parent": po_number,
            "name": ["not in", used] if used else ["!=", ""]
        },
        fields=["name"],
        start=start,
        page_length=page_len,
        ignore_permissions=True
    )

    return [(d.name, d.name) for d in drawings]


@frappe.whitelist()
def get_qty_set_from_po_child(drawing_name):
    """
    SAFE way to read qty_set from child table (Frappe v15 compatible)
    """
    result = frappe.get_all(
        "FT Po List  Child",
        filters={"name": drawing_name},
        fields=["qty_set"],
        ignore_permissions=True,
        limit=1
    )

    return result[0].qty_set if result else 0
