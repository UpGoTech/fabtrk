import frappe

from fabtrk.geometry import GeometryItemError, validate_geometry_tracked_item


def validate_item(doc, method=None):
	if not doc.get("fabtrk_is_geometry_tracked"):
		return
	try:
		validate_geometry_tracked_item(
			stock_uom=doc.stock_uom,
			has_batch_no=doc.has_batch_no,
			has_serial_no=doc.has_serial_no,
			shape=doc.get("fabtrk_shape"),
			thickness_mm=doc.get("fabtrk_thickness_mm"),
			kg_per_metre=doc.get("fabtrk_kg_per_metre"),
			is_geometry_tracked=1,
		)
	except GeometryItemError as exc:
		frappe.throw(str(exc))
