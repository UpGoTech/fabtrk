"""Sync FabTrk Project form Custom Fields, Property Setters, and field order.

Callable via: bench --site <site> execute fabtrk.project_form_setup.sync
"""

from __future__ import annotations

import json

import frappe

MODULE = "Fabtrk"

# (fieldname, fieldtype, label, opts dict)
CUSTOM_FIELDS = [
	{
		"fieldname": "custom_customer_po",
		"label": "Customer PO",
		"fieldtype": "Data",
		"insert_after": "customer",
		"in_standard_filter": 1,
	},
	{
		"fieldname": "custom_customer_po_date",
		"label": "Customer PO Date",
		"fieldtype": "Date",
		"insert_after": "custom_customer_po",
	},
	{
		"fieldname": "custom_section_timeline",
		"label": "Timeline",
		"fieldtype": "Section Break",
		"insert_after": "custom_customer_po_date",
	},
	{
		"fieldname": "custom_column_timeline",
		"fieldtype": "Column Break",
		"insert_after": "expected_start_date",
	},
	{
		"fieldname": "custom_section_order_details",
		"label": "Order Details",
		"fieldtype": "Section Break",
		"insert_after": "expected_end_date",
	},
	{
		"fieldname": "custom_order_qty_kg",
		"label": "Order Qty (kg)",
		"fieldtype": "Float",
		"insert_after": "custom_section_order_details",
		"non_negative": 1,
	},
	{
		"fieldname": "custom_column_order_1",
		"fieldtype": "Column Break",
		"insert_after": "custom_order_qty_kg",
	},
	{
		"fieldname": "custom_rate_per_kg",
		"label": "Rate Per KG",
		"fieldtype": "Currency",
		"insert_after": "custom_column_order_1",
		"non_negative": 1,
	},
	{
		"fieldname": "custom_order_row_2",
		"fieldtype": "Section Break",
		"insert_after": "custom_rate_per_kg",
	},
	{
		"fieldname": "custom_order_value",
		"label": "Order Value",
		"fieldtype": "Currency",
		"insert_after": "custom_order_row_2",
		"read_only": 1,
	},
	{
		"fieldname": "custom_column_order_2",
		"fieldtype": "Column Break",
		"insert_after": "custom_order_value",
	},
	{
		"fieldname": "custom_gst_rate",
		"label": "GST Rate",
		"fieldtype": "Percent",
		"insert_after": "custom_column_order_2",
	},
	{
		"fieldname": "custom_column_order_3",
		"fieldtype": "Column Break",
		"insert_after": "custom_gst_rate",
	},
	{
		"fieldname": "custom_assembly_percentage",
		"label": "Assembly Percentage",
		"fieldtype": "Data",
		"insert_after": "custom_column_order_3",
	},
	{
		"fieldname": "custom_billing_shipping_tab",
		"label": "Billing and Shipping",
		"fieldtype": "Tab Break",
		"insert_after": "custom_assembly_percentage",
	},
	{
		"fieldname": "custom_bill_to",
		"label": "Bill To",
		"fieldtype": "Link",
		"options": "Address",
		"insert_after": "custom_billing_shipping_tab",
	},
	{
		"fieldname": "custom_ship_to",
		"label": "Ship To",
		"fieldtype": "Table",
		"options": "Project Ship To",
		"insert_after": "custom_bill_to",
	},
	{
		"fieldname": "custom_section_transport_scope",
		"label": "Transport Scope",
		"fieldtype": "Section Break",
		"insert_after": "custom_ship_to",
	},
	{
		"fieldname": "custom_transport_scope",
		"label": "Transport Scope",
		"fieldtype": "Select",
		"options": "\nSelf\nCustomer",
		"insert_after": "custom_section_transport_scope",
	},
	{
		"fieldname": "custom_payment_terms_tab",
		"label": "Payment Terms",
		"fieldtype": "Tab Break",
		"insert_after": "custom_transport_scope",
	},
	{
		"fieldname": "custom_advance",
		"label": "Advance",
		"fieldtype": "Percent",
		"insert_after": "custom_payment_terms_tab",
		"description": "Percentage",
	},
	{
		"fieldname": "custom_rm",
		"label": "RM",
		"fieldtype": "Percent",
		"insert_after": "custom_advance",
		"description": "Percentage",
	},
	{
		"fieldname": "custom_black_inspection",
		"label": "Black Inspection",
		"fieldtype": "Percent",
		"insert_after": "custom_rm",
		"description": "Percentage",
	},
	{
		"fieldname": "custom_final_invoice",
		"label": "Final Invoice",
		"fieldtype": "Percent",
		"insert_after": "custom_black_inspection",
		"description": "Percentage",
	},
]

# Visible Details / new tabs / Connections only
FIELD_ORDER = [
	"naming_series",
	"project_name",
	"customer",
	"custom_customer_po",
	"custom_customer_po_date",
	"custom_section_timeline",
	"expected_start_date",
	"custom_column_timeline",
	"expected_end_date",
	"custom_section_order_details",
	"custom_order_qty_kg",
	"custom_column_order_1",
	"custom_rate_per_kg",
	"custom_order_row_2",
	"custom_order_value",
	"custom_column_order_2",
	"custom_gst_rate",
	"custom_column_order_3",
	"custom_assembly_percentage",
	"custom_billing_shipping_tab",
	"custom_bill_to",
	"custom_ship_to",
	"custom_section_transport_scope",
	"custom_transport_scope",
	"custom_payment_terms_tab",
	"custom_advance",
	"custom_rm",
	"custom_black_inspection",
	"custom_final_invoice",
	"connections_tab",
]

# Stock fields to hide (everything not in the fabtrk Project layout)
HIDE_FIELDS = [
	"status",
	"project_type",
	"is_active",
	"percent_complete_method",
	"percent_complete",
	"project_template",
	"priority",
	"department",
	"customer_details",
	"column_break_5",
	"column_break_14",
	"sales_order",
	"users_section",
	"users",
	"copied_from",
	"section_break0",
	"notes",
	"section_break_18",
	"actual_start_date",
	"actual_time",
	"column_break_20",
	"actual_end_date",
	"costing_tab",
	"project_details",
	"estimated_costing",
	"total_costing_amount",
	"total_purchase_cost",
	"company",
	"column_break_28",
	"total_sales_amount",
	"total_billable_amount",
	"total_billed_amount",
	"total_consumed_material_cost",
	"cost_center",
	"margin",
	"gross_margin",
	"column_break_37",
	"per_gross_margin",
	"monitor_progress_tab",
	"collect_progress",
	"holiday_list",
	"frequency",
	"from_time",
	"to_time",
	"first_email",
	"second_email",
	"daily_time_to_send",
	"day_to_send",
	"weekly_time_to_send",
	"column_break_45",
	"message",
	"subject",
	"more_info_tab",
]

LABELS = {
	"customer": "Customer Name",
	"expected_start_date": "Start Date",
	"expected_end_date": "End Date",
}

PROPERTY_SETTERS = [
	("customer", "reqd", "1", "Check"),
	("customer", "label", "Customer Name", "Data"),
	("expected_start_date", "label", "Start Date", "Data"),
	("expected_end_date", "label", "End Date", "Data"),
	("naming_series", "hidden", "1", "Check"),
]


def _upsert_custom_field(spec: dict) -> None:
	name = f"Project-{spec['fieldname']}"
	if frappe.db.exists("Custom Field", name):
		doc = frappe.get_doc("Custom Field", name)
		for key, value in spec.items():
			doc.set(key, value)
		doc.dt = "Project"
		doc.module = MODULE
		doc.save()
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": "Project",
				"module": MODULE,
				**spec,
			}
		)
		doc.insert()


def _upsert_property_setter(
	field_name: str | None,
	prop: str,
	value: str,
	property_type: str,
	doctype_or_field: str = "DocField",
) -> None:
	filters = {
		"doc_type": "Project",
		"property": prop,
	}
	if field_name:
		filters["field_name"] = field_name
	else:
		filters["field_name"] = ["in", ["", None]]

	existing = frappe.db.exists("Property Setter", filters)
	# field_order uses null field_name — look up by name convention
	if prop == "field_order":
		existing = frappe.db.exists("Property Setter", "Project-main-field_order") or existing

	if existing:
		name = existing if isinstance(existing, str) else existing
		frappe.db.set_value("Property Setter", name, {"value": value, "property_type": property_type})
		return

	doc = {
		"doctype": "Property Setter",
		"doctype_or_field": doctype_or_field,
		"doc_type": "Project",
		"property": prop,
		"value": value,
		"property_type": property_type,
		"module": MODULE,
	}
	if field_name:
		doc["field_name"] = field_name
	if prop == "field_order":
		doc["name"] = "Project-main-field_order"
	frappe.get_doc(doc).insert()


def _hide_field(fieldname: str) -> None:
	_upsert_property_setter(fieldname, "hidden", "1", "Check")


def sync() -> None:
	"""Create/update Project form customization for FabTrk."""
	for spec in CUSTOM_FIELDS:
		_upsert_custom_field(spec)

	for fieldname, prop, value, ptype in PROPERTY_SETTERS:
		_upsert_property_setter(fieldname, prop, value, ptype)

	for fieldname in HIDE_FIELDS:
		_hide_field(fieldname)

	# Ensure start/end sit under Timeline section (not still under old Timeline section_break_18)
	_upsert_property_setter("expected_start_date", "insert_after", "custom_section_timeline", "Data")
	_upsert_property_setter("expected_end_date", "insert_after", "custom_column_timeline", "Data")

	# Unhide start/end in case they were under a hidden section previously
	_upsert_property_setter("expected_start_date", "hidden", "0", "Check")
	_upsert_property_setter("expected_end_date", "hidden", "0", "Check")

	# Append any remaining meta fields not listed so Customize Form stays valid
	meta = frappe.get_meta("Project", cached=False)
	all_names = [df.fieldname for df in meta.fields]
	ordered = list(FIELD_ORDER)
	for name in all_names:
		if name not in ordered:
			ordered.append(name)

	_upsert_property_setter(
		None,
		"field_order",
		json.dumps(ordered),
		"Text",
		doctype_or_field="DocType",
	)

	frappe.clear_cache(doctype="Project")
	frappe.db.commit()
	print("Project form sync complete")
