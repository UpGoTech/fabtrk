"""Geometry reports. Length totals are sum(length_mm * qty_pieces)."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def geometry_rows(filters=None):
	filters = filters or {}
	clauses = ["ifnull(qty_pieces, 0) != 0"]
	values = {}
	if filters.get("item_code"):
		clauses.append("item_code = %(item_code)s")
		values["item_code"] = filters["item_code"]
	if filters.get("warehouse"):
		clauses.append("warehouse = %(warehouse)s")
		values["warehouse"] = filters["warehouse"]
	if filters.get("grade"):
		clauses.append("fabtrk_grade = %(grade)s")
		values["grade"] = filters["grade"]
	rows = frappe.db.sql(
		f"""
		select item_code, fabtrk_grade as grade, length_mm, width_mm, warehouse, division, stock_group,
			sum(qty_pieces) as qty_pieces,
			sum(weight_kg) as weight_kg,
			sum(length_mm * qty_pieces) as total_length_mm
		from `tabFabtrk Lot`
		where {" and ".join(clauses)}
		group by item_code, fabtrk_grade, length_mm, width_mm, warehouse, division, stock_group
		order by item_code, length_mm, width_mm
		""",
		values,
		as_dict=True,
	)
	for row in rows:
		row["weight_mt"] = flt(row.weight_kg) / 1000
	return rows


def availability_rows(filters=None):
	filters = filters or {}
	clauses = ["ifnull(qty_pieces, 0) != 0"]
	values = {}
	if filters.get("item_code"):
		clauses.append("item_code = %(item_code)s")
		values["item_code"] = filters["item_code"]
	rows = frappe.db.sql(
		f"""
		select item_code, fabtrk_grade as grade, warehouse, division, stock_group,
			sum(qty_pieces) as qty_pieces,
			sum(weight_kg) as weight_kg
		from `tabFabtrk Lot`
		where {" and ".join(clauses)}
		group by item_code, fabtrk_grade, warehouse, division, stock_group
		order by item_code, stock_group
		""",
		values,
		as_dict=True,
	)
	for row in rows:
		row["weight_mt"] = flt(row.weight_kg) / 1000
	return rows


def offcut_rows(filters=None):
	filters = filters or {}
	clauses = ["lot_type = 'Offcut'", "status = 'In Stock'", "ifnull(qty_pieces, 0) > 0"]
	values = {
		"min_length_mm": flt(filters.get("min_length_mm")),
		"min_width_mm": flt(filters.get("min_width_mm")),
	}
	clauses.append("length_mm >= %(min_length_mm)s")
	clauses.append("ifnull(width_mm, 0) >= %(min_width_mm)s")
	if filters.get("item_code"):
		clauses.append("item_code = %(item_code)s")
		values["item_code"] = filters["item_code"]
	if filters.get("grade"):
		clauses.append("fabtrk_grade = %(grade)s")
		values["grade"] = filters["grade"]
	if filters.get("warehouse"):
		clauses.append("warehouse = %(warehouse)s")
		values["warehouse"] = filters["warehouse"]
	rows = frappe.db.sql(
		f"""
		select name as lot, item_code, fabtrk_grade as grade, length_mm, width_mm, warehouse,
			qty_pieces, weight_kg, received_on
		from `tabFabtrk Lot`
		where {" and ".join(clauses)}
		order by length_mm, width_mm
		""",
		values,
		as_dict=True,
	)
	for row in rows:
		row["weight_mt"] = flt(row.weight_kg) / 1000
	return rows


def lot_movements(lot=None, item_code=None):
	clauses = ["1=1"]
	values = {}
	if lot:
		clauses.append("lot = %(lot)s")
		values["lot"] = lot
	if item_code:
		clauses.append("item_code = %(item_code)s")
		values["item_code"] = item_code
	return frappe.db.sql(
		f"""
		select name, lot, posting_date, voucher_type, voucher_no, item_code, warehouse,
			qty_pieces, length_mm, width_mm, weight_kg, resulting_qty_pieces, resulting_weight_kg,
			reference, reason, actor, creation
		from `tabFabtrk Lot Movement`
		where {" and ".join(clauses)}
		order by posting_date asc, creation asc
		""",
		values,
		as_dict=True,
	)


def sku_ledger(item_code):
	sizes = geometry_rows({"item_code": item_code})
	for row in sizes:
		row["row_type"] = "Size"
	movements = lot_movements(item_code=item_code)
	for row in movements:
		row["row_type"] = "Movement"
		row["weight_mt"] = flt(row.weight_kg) / 1000
	return sizes + movements


def reconcile_rows():
	lot_rows = frappe.db.sql(
		"""
		select item_code, warehouse, sum(weight_kg) as lot_kg
		from `tabFabtrk Lot`
		where ifnull(qty_pieces, 0) != 0 or ifnull(weight_kg, 0) != 0
		group by item_code, warehouse
		""",
		as_dict=True,
	)
	bin_rows = frappe.db.sql(
		"""
		select bin.item_code, bin.warehouse, bin.actual_qty as bin_kg
		from `tabBin` bin
		inner join `tabItem` item on item.name = bin.item_code
		where item.fabtrk_is_geometry_tracked = 1
		""",
		as_dict=True,
	)
	combined = {}
	for row in lot_rows:
		combined[(row.item_code, row.warehouse)] = {"item_code": row.item_code, "warehouse": row.warehouse, "lot_kg": flt(row.lot_kg), "bin_kg": 0}
	for row in bin_rows:
		key = (row.item_code, row.warehouse)
		combined.setdefault(key, {"item_code": row.item_code, "warehouse": row.warehouse, "lot_kg": 0, "bin_kg": 0})
		combined[key]["bin_kg"] = flt(row.bin_kg)
	rows = []
	for row in combined.values():
		row["drift_kg"] = flt(row["lot_kg"]) - flt(row["bin_kg"])
		row["lot_mt"] = flt(row["lot_kg"]) / 1000
		row["bin_mt"] = flt(row["bin_kg"]) / 1000
		rows.append(row)
	rows.sort(key=lambda row: (row["item_code"], row["warehouse"]))
	return rows
