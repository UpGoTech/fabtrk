"""Roles, custom fields, warehouses, and the known plate items."""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.permissions import add_permission, update_permission_property

ROLES = ("Fabtrk Stock Owner", "Fabtrk Stock Storekeeper", "Fabtrk Stock Viewer")

# Q4: round bar, pipe, and tube SKUs stay uncreated until the owner confirms them.
PLATE_SKUS = [
	"PL-E250-06MM",
	"PL-E250-08MM",
	"PL-E250-10MM",
	"PL-E250-12MM",
	"PL-E250-16MM",
	"PL-E250-20MM",
	"PL-E250-25MM",
	"PL-E350-06MM",
	"PL-E350-08MM",
	"PL-E350-10MM",
	"PL-E350-12MM",
	"PL-E350-16MM",
	"PL-E350-20MM",
	"PL-E350-25MM",
	"PL-SAILHARD400-10MM",
]


def before_migrate():
	ensure_roles()


def after_migrate():
	ensure_custom_fields()
	ensure_settings()
	ensure_warehouses()
	ensure_known_items()
	ensure_voucher_permissions()


def ensure_roles():
	for role in ROLES:
		if frappe.db.exists("Role", role):
			continue
		frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def ensure_settings():
	if frappe.db.exists("DocType", "Fabtrk Settings") and not frappe.db.exists("Fabtrk Settings", "Fabtrk Settings"):
		frappe.get_doc({"doctype": "Fabtrk Settings"}).insert(ignore_permissions=True)


def company_name():
	return frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")


def warehouse_name(label, company=None):
	company = company or company_name()
	abbr = frappe.db.get_value("Company", company, "abbr")
	return f"{label} - {abbr}"


def ensure_warehouses():
	# Q1 unanswered: one plant (Butibori) and three stock warehouses.
	company = company_name()
	if not company:
		return
	parent = frappe.db.get_value("Warehouse", {"is_group": 1, "company": company}, "name")
	for label in ("Main", "Offcuts", "Scrap"):
		name = warehouse_name(label, company)
		if frappe.db.exists("Warehouse", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": label,
				"company": company,
				"parent_warehouse": parent,
				"is_group": 0,
			}
		).insert(ignore_permissions=True)


def ensure_known_items():
	if not frappe.db.exists("DocType", "Item"):
		return
	hsn = frappe.db.get_value("Item", "PL-E350-12MM", "gst_hsn_code") or "72085190"
	for item_code in PLATE_SKUS:
		grade, thickness = _plate_identity(item_code)
		if item_code.startswith("PL-SAILHARD"):
			item_group = "SAILHARD"
		elif grade == "E250":
			item_group = "E250 - Plates"
		else:
			item_group = "E350 - Plates"
		if frappe.db.exists("Item", item_code):
			item = frappe.get_doc("Item", item_code)
			changed = False
			for field, value in (
				("fabtrk_is_geometry_tracked", 1),
				("fabtrk_grade", grade),
				("fabtrk_shape", "Plate"),
				("fabtrk_thickness_mm", thickness),
			):
				if item.get(field) != value:
					item.set(field, value)
					changed = True
			if changed:
				item.save(ignore_permissions=True)
			continue
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"item_group": item_group,
				"stock_uom": "Kg",
				"is_stock_item": 1,
				"has_batch_no": 0,
				"has_serial_no": 0,
				"gst_hsn_code": hsn,
				"fabtrk_is_geometry_tracked": 1,
				"fabtrk_grade": grade,
				"fabtrk_shape": "Plate",
				"fabtrk_thickness_mm": thickness,
			}
		).insert(ignore_permissions=True)


def ensure_voucher_permissions():
	grants = {
		("Stock Entry", "Fabtrk Stock Storekeeper"): {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 0, "report": 1},
		("Stock Entry", "Fabtrk Stock Owner"): {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "report": 1},
		("Purchase Receipt", "Fabtrk Stock Storekeeper"): {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 0, "report": 1},
		("Purchase Receipt", "Fabtrk Stock Owner"): {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "report": 1},
		("Item", "Fabtrk Stock Storekeeper"): {"read": 1, "write": 0, "create": 0, "report": 1},
		("Item", "Fabtrk Stock Owner"): {"read": 1, "write": 1, "create": 1, "report": 1},
	}
	for (doctype, role), rights in grants.items():
		_grant(doctype, role, rights)


def ensure_custom_fields():
	module = {"module": "Fabtrk"}
	grade = "\nE250\nE350\nSAILHARD400\nHARDOX400\nHARDOX500"
	shape = "\nPlate\nAngle\nChannel\nBeam\nNPB\nPipe\nTube\nRound Bar\nCoil\nOther"
	voucher_fields = [
		{"fieldname": "fabtrk_section", "label": "Fabtrk Geometry", "fieldtype": "Section Break", "insert_after": "items", **module},
		{
			"fieldname": "fabtrk_reference",
			"label": "Reference",
			"fieldtype": "Data",
			"insert_after": "fabtrk_section",
			"description": "Invoice, challan, or job reference",
			"in_standard_filter": 1,
			**module,
		},
		{"fieldname": "fabtrk_origin_job", "label": "Origin Job", "fieldtype": "Data", "insert_after": "fabtrk_reference", **module},
		{"fieldname": "fabtrk_reason", "label": "Adjustment Reason", "fieldtype": "Data", "insert_after": "fabtrk_origin_job", **module},
		{
			"fieldname": "fabtrk_is_adjustment",
			"label": "Adjustment",
			"fieldtype": "Check",
			"insert_after": "fabtrk_reason",
			**module,
		},
		{
			"fieldname": "fabtrk_lot_details",
			"label": "Lot Details",
			"fieldtype": "Table",
			"options": "Fabtrk Lot Detail",
			"insert_after": "fabtrk_is_adjustment",
			**module,
		},
	]
	create_custom_fields(
		{
			"Item": [
				{"fieldname": "fabtrk_section", "label": "Fabtrk Geometry", "fieldtype": "Section Break", "insert_after": "stock_uom", **module},
				{
					"fieldname": "fabtrk_is_geometry_tracked",
					"label": "Geometry Tracked",
					"fieldtype": "Check",
					"insert_after": "fabtrk_section",
					**module,
				},
				{
					"fieldname": "fabtrk_grade",
					"label": "Grade",
					"fieldtype": "Select",
					"options": grade,
					"insert_after": "fabtrk_is_geometry_tracked",
					**module,
				},
				{
					"fieldname": "fabtrk_shape",
					"label": "Shape",
					"fieldtype": "Select",
					"options": shape,
					"insert_after": "fabtrk_grade",
					**module,
				},
				{
					"fieldname": "fabtrk_thickness_mm",
					"label": "Thickness (mm)",
					"fieldtype": "Float",
					"insert_after": "fabtrk_shape",
					**module,
				},
				{
					"fieldname": "fabtrk_kg_per_metre",
					"label": "Kg per Metre",
					"fieldtype": "Float",
					"insert_after": "fabtrk_thickness_mm",
					**module,
				},
				{
					"fieldname": "fabtrk_default_length_mm",
					"label": "Default Length (mm)",
					"fieldtype": "Float",
					"insert_after": "fabtrk_kg_per_metre",
					**module,
				},
			],
			("Stock Entry", "Purchase Receipt"): voucher_fields,
			"Stock Reconciliation": [
				{
					"fieldname": "fabtrk_reference",
					"label": "Reference",
					"fieldtype": "Data",
					"insert_after": "purpose",
					"in_standard_filter": 1,
					**module,
				}
			],
		},
		update=True,
	)


def _grant(doctype, role, rights):
	if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0}):
		add_permission(doctype, role, 0, "read")
	for ptype, value in rights.items():
		update_permission_property(doctype, role, 0, ptype, value, validate=False)


def _plate_identity(item_code):
	parts = item_code.split("-")
	grade = "SAILHARD400" if "SAILHARD" in item_code else parts[1]
	thickness = int(parts[-1].replace("MM", ""))
	return grade, thickness
