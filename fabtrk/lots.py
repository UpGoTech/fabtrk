"""Voucher hooks that keep Fabtrk Lots in step with Bin.

Quantity and weight change only here, inside the voucher transaction.
"""

from __future__ import annotations

from decimal import Decimal

import frappe
from frappe.utils import flt, today

from fabtrk.geometry import (
	OverIssue,
	assess_conservation,
	assess_weight,
	suggest_scrap,
	weight_from_density,
	weight_from_kg_per_metre,
)


class DuplicateReference(frappe.ValidationError):
	def __init__(self, voucher_type, voucher_no, reference):
		self.voucher_type = voucher_type
		self.voucher_no = voucher_no
		self.reference = reference
		super().__init__(
			f"Duplicate reference {reference}. Already posted on {voucher_type} {voucher_no}"
		)


def stock_group_for_warehouse(warehouse):
	name = (warehouse or "").lower()
	if "scrap" in name:
		return "Scrap"
	if "offcut" in name:
		return "Offcut Stock"
	return "Full Stock"


def before_submit(doc, method=None):
	if doc.doctype == "Stock Reconciliation":
		return
	plan_voucher(doc)


def on_submit(doc, method=None):
	if doc.doctype == "Stock Reconciliation":
		return
	plan = plan_voucher(doc)
	if not plan:
		return
	apply_plan(doc, plan)
	frappe.flags.fabtrk_warnings = plan["warnings"]
	for warning in plan["warnings"]:
		frappe.msgprint(warning, indicator="orange", alert=True)


def on_cancel(doc, method=None):
	reverse_voucher(doc)


def alert_drift():
	from fabtrk.stock_reports import reconcile_rows

	rows = [row for row in reconcile_rows() if abs(row["drift_kg"]) > 0.001]
	if rows:
		frappe.log_error(title="Fabtrk stock drift", message=frappe.as_json(rows))


def plan_voucher(doc):
	details = list(doc.get("fabtrk_lot_details") or [])
	tracked_lines = [line for line in _voucher_lines(doc) if _tracked(line["item_code"])]
	if not tracked_lines and not details:
		return None
	if not doc.get("fabtrk_reference"):
		frappe.throw("Reference is required on a voucher that moves geometry-tracked items")
	if tracked_lines and not details:
		frappe.throw("Add lot detail rows for each geometry-tracked item")
	_reject_duplicate(doc)
	if doc.get("fabtrk_is_adjustment") and not (doc.get("fabtrk_reason") or all(row.reason for row in details)):
		frappe.throw("An adjustment needs a reason")

	settings = _settings()
	warnings = []
	items = {}
	for row in details:
		_check_detail_row(doc, row, settings, items, warnings)

	_check_line_weights(doc, details, settings)
	_check_issue_limits(doc, details, settings)
	_check_conservation(doc, details, settings, warnings)
	effects = _effects(doc, details, settings)
	return {"warnings": warnings, "effects": effects}


def apply_plan(doc, plan):
	_insert_posting_key(doc)
	lot_for_detail = {}
	for effect in plan["effects"]:
		lot = _apply_effect(doc, effect)
		for detail_name in effect["detail_names"]:
			lot_for_detail[detail_name] = lot.name
	for detail_name, lot_name in lot_for_detail.items():
		if detail_name:
			frappe.db.set_value("Fabtrk Lot Detail", detail_name, "lot", lot_name)


def post_opening_lots(reference, posting_date, rows, voucher_type, voucher_no):
	"""Geometry for a Stock Reconciliation that already set the Bin quantities."""
	doc = frappe._dict(
		doctype=voucher_type,
		name=voucher_no,
		fabtrk_reference=reference,
		posting_date=posting_date,
		fabtrk_origin_job=None,
		fabtrk_reason=None,
		purpose="Material Receipt",
	)
	_insert_posting_key(doc)
	settings = _settings()
	for row in rows:
		effect = {
			"action": "create",
			"detail_names": [],
			"delta_qty": _d(row["qty_pieces"]),
			"delta_weight": _d(row["weight_kg"]),
			"lot_fields": _lot_fields_from_row(doc, row, settings),
		}
		_apply_effect(doc, effect)


def plan_voucher_preview(doc):
	plan = plan_voucher(doc)
	if not plan:
		return {"warnings": [], "lines": []}
	lines = []
	for effect in plan["effects"]:
		fields = effect.get("lot_fields") or {}
		lot_name = effect.get("lot")
		if lot_name and effect["action"] != "create":
			current = frappe.db.get_value(
				"Fabtrk Lot", lot_name, ["qty_pieces", "weight_kg", "length_mm", "width_mm", "item_code", "warehouse"], as_dict=True
			)
		else:
			current = None
		resulting_qty = effect["resulting_qty"]
		resulting_weight = effect["resulting_weight"]
		item_code = fields.get("item_code") or (current.item_code if current else None)
		warehouse = effect.get("warehouse") or fields.get("warehouse") or (current.warehouse if current else None)
		lines.append(
			{
				"item_code": item_code,
				"warehouse": warehouse,
				"length_mm": fields.get("length_mm") if fields else (current.length_mm if current else None),
				"width_mm": fields.get("width_mm") if fields else (current.width_mm if current else None),
				"qty_pieces": float(effect["delta_qty"]),
				"weight_kg": float(effect["delta_weight"]),
				"weight_mt": float(_d(effect["delta_weight"]) / Decimal(1000)),
				"lot": lot_name,
				"lot_qty_pieces": float(resulting_qty),
				"lot_weight_kg": float(resulting_weight),
				"bin_qty": _preview_bin(item_code, warehouse, effect),
			}
		)
	return {"warnings": plan["warnings"], "lines": lines}


def reverse_voucher(doc):
	movements = [
		row
		for row in frappe.get_all(
			"Fabtrk Lot Movement",
			filters={"voucher_type": doc.doctype, "voucher_no": doc.name},
			fields=[
				"name",
				"lot",
				"qty_pieces",
				"weight_kg",
				"warehouse",
				"from_warehouse",
				"length_mm",
				"width_mm",
				"reference",
				"reason",
			],
			order_by="creation desc",
		)
		if row.reason != "Cancel"
	]
	if movements and not doc.get("fabtrk_reference"):
		doc.fabtrk_reference = movements[0].reference
	for movement in movements:
		lot = frappe.get_doc("Fabtrk Lot", movement.lot)
		delta_qty = -_d(movement.qty_pieces)
		delta_weight = -_d(movement.weight_kg)
		new_qty, new_weight = _write_lot_delta(lot, delta_qty, delta_weight)
		if movement.from_warehouse and not movement.qty_pieces:
			lot.db_set("warehouse", movement.from_warehouse)
			lot.warehouse = movement.from_warehouse
		_insert_movement(
			doc,
			lot,
			delta_qty,
			delta_weight,
			new_qty,
			new_weight,
			reason="Cancel",
			from_warehouse=movement.warehouse if movement.from_warehouse else None,
		)
	key = _posting_key(doc)
	if frappe.db.exists("Fabtrk Posting Key", key):
		frappe.delete_doc("Fabtrk Posting Key", key, ignore_permissions=True, force=True)


def _effects(doc, details, settings):
	effects = []
	grouped = {}
	outs = {}
	for row in details:
		kind = _kind(doc, row)
		if kind == "in" and not row.lot:
			grouped.setdefault(_group_key(doc, row), []).append(row)
		elif kind == "out":
			outs.setdefault(row.lot, []).append(row)
		elif kind == "move":
			effects.append(_move_effect(row))
		else:
			effects.append(_explicit_in_effect(doc, row, settings))
	for rows in grouped.values():
		effects.append(_create_effect(doc, rows, settings))
	for lot_name, rows in outs.items():
		effects.append(_out_effect(doc, lot_name, rows))
	return effects


def _create_effect(doc, rows, settings):
	qty = sum((_d(row.qty_pieces) for row in rows), Decimal(0))
	weight = sum((_d(row.weight_kg) for row in rows), Decimal(0))
	sample = rows[0]
	existing = None
	if not sample.parent_lot:
		existing = _find_open_lot(sample, doc)
	if existing:
		current_qty, current_weight = _lot_balance(existing)
		return {
			"action": "update",
			"lot": existing,
			"detail_names": [row.name for row in rows],
			"delta_qty": qty,
			"delta_weight": weight,
			"warehouse": sample.warehouse,
			"resulting_qty": current_qty + qty,
			"resulting_weight": current_weight + weight,
			"lot_fields": {},
			"reason": sample.reason or doc.get("fabtrk_reason"),
		}
	return {
		"action": "create",
		"lot": None,
		"detail_names": [row.name for row in rows],
		"delta_qty": qty,
		"delta_weight": weight,
		"warehouse": sample.warehouse,
		"resulting_qty": qty,
		"resulting_weight": weight,
		"lot_fields": _lot_fields_from_detail(doc, sample, qty, weight, settings),
		"reason": sample.reason or doc.get("fabtrk_reason"),
	}


def _explicit_in_effect(doc, row, settings):
	qty = _d(row.qty_pieces)
	weight = _d(row.weight_kg)
	current_qty, current_weight = _lot_balance(row.lot)
	return {
		"action": "update",
		"lot": row.lot,
		"detail_names": [row.name],
		"delta_qty": qty,
		"delta_weight": weight,
		"warehouse": row.warehouse,
		"resulting_qty": current_qty + qty,
		"resulting_weight": current_weight + weight,
		"lot_fields": {},
		"reason": row.reason or doc.get("fabtrk_reason"),
		"reopen": True,
	}


def _out_effect(doc, lot_name, rows):
	qty = sum((_d(row.qty_pieces) for row in rows), Decimal(0))
	weight = sum((_d(row.weight_kg) for row in rows), Decimal(0))
	current_qty, current_weight = _lot_balance(lot_name)
	return {
		"action": "update",
		"lot": lot_name,
		"detail_names": [row.name for row in rows],
		"delta_qty": -qty,
		"delta_weight": -weight,
		"warehouse": rows[0].warehouse,
		"resulting_qty": current_qty - qty,
		"resulting_weight": current_weight - weight,
		"lot_fields": {},
		"reason": rows[0].reason or doc.get("fabtrk_reason"),
	}


def _move_effect(row):
	current_qty, current_weight = _lot_balance(row.lot)
	lot_warehouse = frappe.db.get_value("Fabtrk Lot", row.lot, "warehouse")
	return {
		"action": "move",
		"lot": row.lot,
		"detail_names": [row.name],
		"delta_qty": Decimal(0),
		"delta_weight": Decimal(0),
		"warehouse": row.warehouse,
		"from_warehouse": lot_warehouse,
		"resulting_qty": current_qty,
		"resulting_weight": current_weight,
		"lot_fields": {},
		"reason": row.reason,
	}


def _apply_effect(doc, effect):
	if effect["action"] == "create":
		lot = frappe.get_doc({"doctype": "Fabtrk Lot", **effect["lot_fields"]})
		lot.flags.from_voucher = True
		lot.insert(ignore_permissions=True)
		_insert_movement(
			doc,
			lot,
			effect["delta_qty"],
			effect["delta_weight"],
			_d(lot.qty_pieces),
			_d(lot.weight_kg),
			reason=effect.get("reason"),
		)
		return lot
	lot = frappe.get_doc("Fabtrk Lot", effect["lot"])
	if effect["action"] == "move":
		_write_lot_delta(lot, Decimal(0), Decimal(0), warehouse=effect["warehouse"])
		_insert_movement(
			doc,
			lot,
			Decimal(0),
			Decimal(0),
			_d(lot.qty_pieces),
			_d(lot.weight_kg),
			reason=effect.get("reason"),
			from_warehouse=effect["from_warehouse"],
		)
		return lot
	new_qty, new_weight = _write_lot_delta(lot, effect["delta_qty"], effect["delta_weight"])
	if effect.get("reopen") and new_qty > 0:
		lot.db_set("status", "In Stock")
	_insert_movement(
		doc,
		lot,
		effect["delta_qty"],
		effect["delta_weight"],
		new_qty,
		new_weight,
		reason=effect.get("reason"),
	)
	return lot


def _write_lot_delta(lot, delta_qty, delta_weight, warehouse=None):
	new_qty = _d(lot.qty_pieces) + _d(delta_qty)
	new_weight = _d(lot.weight_kg) + _d(delta_weight)
	if new_qty < 0 or new_weight < 0:
		if not _settings().allow_negative_stock:
			raise_over_issue(new_qty, new_weight, lot)
	lot.flags.from_voucher = True
	lot.qty_pieces = float(new_qty)
	lot.weight_kg = float(new_weight)
	lot.status = "Consumed" if new_qty == 0 else lot.status or "In Stock"
	if new_qty == 0:
		lot.status = "Consumed"
	elif lot.status == "Consumed":
		lot.status = "In Stock"
	if warehouse:
		lot.warehouse = warehouse
	lot.save(ignore_permissions=True)
	return new_qty, new_weight


def raise_over_issue(new_qty, new_weight, lot):
	piece = _d(lot.qty_pieces) if new_qty < 0 else None
	weight = _d(lot.weight_kg) if new_weight < 0 else None
	exc = OverIssue(available_pieces=piece, available_kg=weight)
	frappe.throw(str(exc))


def _insert_movement(doc, lot, delta_qty, delta_weight, resulting_qty, resulting_weight, reason=None, from_warehouse=None):
	movement = frappe.get_doc(
		{
			"doctype": "Fabtrk Lot Movement",
			"naming_series": "FABTRK-MOV-.YYYY.-.#####",
			"lot": lot.name,
			"posting_date": doc.get("posting_date") or today(),
			"voucher_type": doc.doctype,
			"voucher_no": doc.name,
			"item_code": lot.item_code,
			"warehouse": lot.warehouse,
			"from_warehouse": from_warehouse,
			"qty_pieces": float(delta_qty),
			"length_mm": lot.length_mm,
			"width_mm": lot.width_mm,
			"weight_kg": float(delta_weight),
			"resulting_qty_pieces": float(resulting_qty),
			"resulting_weight_kg": float(resulting_weight),
			"reference": doc.fabtrk_reference,
			"reason": reason,
			"actor": frappe.session.user,
		}
	)
	movement.insert(ignore_permissions=True)


def _lot_fields_from_detail(doc, row, qty, weight, settings):
	rate = _rate_for(doc, row.item_code, row.parent_lot)
	return {
		"naming_series": "FABTRK-LOT-.YYYY.-.#####",
		"item_code": row.item_code,
		"warehouse": row.warehouse,
		"division": "Butibori",
		"length_mm": row.length_mm,
		"width_mm": row.width_mm or 0,
		"qty_pieces": float(qty),
		"weight_kg": float(weight),
		"weight_basis": row.weight_basis,
		"weight_basis_source": row.weight_basis_source,
		"density_kg_m3": settings.default_density_kg_m3,
		"lot_type": row.lot_type or "Parent",
		"status": "In Stock",
		"parent_lot": row.parent_lot,
		"source_doctype": doc.doctype,
		"source_document": doc.name,
		"source_reference": row.source_reference or doc.fabtrk_reference,
		"origin_job": doc.get("fabtrk_origin_job"),
		"received_on": doc.get("posting_date") or today(),
		"valuation_rate": rate,
	}


def _lot_fields_from_row(doc, row, settings):
	return {
		"naming_series": "FABTRK-LOT-.YYYY.-.#####",
		"item_code": row["item_code"],
		"warehouse": row["warehouse"],
		"division": row.get("division") or "Butibori",
		"length_mm": row["length_mm"],
		"width_mm": row.get("width_mm") or 0,
		"qty_pieces": row["qty_pieces"],
		"weight_kg": row["weight_kg"],
		"weight_basis": row.get("weight_basis") or "Weighment",
		"weight_basis_source": row.get("weight_basis_source"),
		"density_kg_m3": settings.default_density_kg_m3,
		"lot_type": row.get("lot_type") or "Parent",
		"status": "In Stock",
		"source_doctype": doc.doctype,
		"source_document": doc.name,
		"source_reference": row.get("source_reference") or doc.fabtrk_reference,
		"received_on": doc.posting_date,
		"valuation_rate": row.get("valuation_rate") or 0,
	}


def _check_detail_row(doc, row, settings, items, warnings):
	if not row.item_code or not row.warehouse:
		frappe.throw("Each lot row needs an item and a warehouse")
	if not _on_voucher(doc, row.item_code):
		frappe.throw(f"{row.item_code} is not on this voucher")
	if flt(row.qty_pieces) <= 0 or flt(row.weight_kg) < 0:
		frappe.throw("Lot rows use a positive piece count and weight")
	if row.weight_basis in ("Kg Per Metre", "Density") and not row.weight_basis_source:
		frappe.throw(f"Weight basis source is required for {row.weight_basis}")
	item = items.get(row.item_code)
	if item is None:
		item = frappe.get_doc("Item", row.item_code)
		items[row.item_code] = item
	calculated = _calculated_weight(item, row, settings)
	if calculated is not None and calculated != 0:
		assessment = assess_weight(
			calculated,
			row.weight_kg,
			row.weight_basis,
			warn_pct=settings.weight_deviation_warn_pct,
			block_pct=settings.weight_deviation_block_pct,
		)
		if assessment.level == "block":
			frappe.throw(
				f"Weight {flt(row.weight_kg)} kg is {flt(assessment.deviation_pct, 2)}% off "
				f"calculated {flt(calculated, 3)} kg ({row.weight_basis})"
			)
		if assessment.level == "warn":
			warnings.append(
				f"Weight {flt(row.weight_kg)} kg is {flt(assessment.deviation_pct, 2)}% off "
				f"calculated {flt(calculated, 3)} kg ({row.weight_basis})"
			)
	if _kind(doc, row) == "in" and not row.lot and settings.scrap_min_length_mm:
		if suggest_scrap(row.length_mm, row.width_mm or 0, settings.scrap_min_length_mm, settings.scrap_min_width_mm):
			if (row.lot_type or "Parent") != "Scrap":
				warnings.append(
					f"Remainder {flt(row.length_mm)} x {flt(row.width_mm)} mm is below the scrap minimum"
				)


def _check_line_weights(doc, details, settings):
	expected = {}
	for line in _voucher_lines(doc):
		if not _tracked(line["item_code"]):
			continue
		key = (line["item_code"], line["warehouse"], line["direction"])
		expected[key] = expected.get(key, Decimal(0)) + line["qty"]
	actual = {}
	for row in details:
		kind = _kind(doc, row)
		weight = _d(row.weight_kg)
		if kind == "move":
			source = frappe.db.get_value("Fabtrk Lot", row.lot, "warehouse")
			actual[(row.item_code, source, "out")] = actual.get((row.item_code, source, "out"), Decimal(0)) + weight
			actual[(row.item_code, row.warehouse, "in")] = actual.get((row.item_code, row.warehouse, "in"), Decimal(0)) + weight
		elif kind == "out":
			key = (row.item_code, row.warehouse, "out")
			actual[key] = actual.get(key, Decimal(0)) + weight
		else:
			key = (row.item_code, row.warehouse, "in")
			actual[key] = actual.get(key, Decimal(0)) + weight
	for key, qty in expected.items():
		got = actual.get(key, Decimal(0))
		if qty == 0:
			continue
		assessment = assess_weight(
			qty,
			got,
			"line qty",
			warn_pct=settings.weight_deviation_warn_pct,
			block_pct=settings.weight_deviation_block_pct,
		)
		if assessment.level == "block":
			item_code, warehouse, direction = key
			frappe.throw(
				f"Lot weight {flt(got, 3)} kg does not match {direction} quantity {flt(qty, 3)} kg "
				f"for {item_code} in {warehouse}"
			)
	for key in actual:
		if key not in expected:
			item_code, warehouse, direction = key
			frappe.throw(f"Lot row warehouse {warehouse} does not match a {direction} line for {item_code}")


def _check_issue_limits(doc, details, settings):
	per_lot = {}
	per_bin = {}
	for row in details:
		if _kind(doc, row) not in ("out", "move"):
			continue
		weight = _d(row.weight_kg)
		if _kind(doc, row) == "out":
			per_lot.setdefault(row.lot, Decimal(0))
			per_lot[row.lot] += _d(row.qty_pieces)
			warehouse = row.warehouse
		else:
			warehouse = frappe.db.get_value("Fabtrk Lot", row.lot, "warehouse")
		per_bin.setdefault((row.item_code, warehouse), Decimal(0))
		per_bin[(row.item_code, warehouse)] += weight
	allow = bool(settings.allow_negative_stock)
	for lot_name, qty in per_lot.items():
		available = _d(frappe.db.get_value("Fabtrk Lot", lot_name, "qty_pieces"))
		if qty > available and not allow:
			frappe.throw(str(OverIssue(available_pieces=available)))
	for (item_code, warehouse), weight in per_bin.items():
		available = _d(frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"))
		if weight > available and not allow:
			frappe.throw(str(OverIssue(available_kg=available)))


def _check_conservation(doc, details, settings, warnings):
	issued = {}
	accounted = {}
	for row in details:
		if _kind(doc, row) == "out":
			issued[row.lot] = issued.get(row.lot, Decimal(0)) + _d(row.weight_kg)
		elif row.parent_lot:
			accounted.setdefault(row.parent_lot, {"offcut": Decimal(0), "scrap": Decimal(0), "consumed": Decimal(0)})
			bucket = "scrap" if row.lot_type == "Scrap" else "offcut" if row.lot_type == "Offcut" else "consumed"
			accounted[row.parent_lot][bucket] += _d(row.weight_kg)
	for lot_name, weight in issued.items():
		parts = accounted.get(lot_name)
		if not parts:
			lot = frappe.db.get_value("Fabtrk Lot", lot_name, ["length_mm", "width_mm", "qty_pieces", "weight_kg"], as_dict=True)
			row = next(row for row in details if row.lot == lot_name and _kind(doc, row) == "out")
			full = (_d(lot.weight_kg) / _d(lot.qty_pieces)) * _d(row.qty_pieces) if lot.qty_pieces else weight
			geometry_changed = abs(flt(row.length_mm) - flt(lot.length_mm)) > 0.05 or abs(flt(row.width_mm) - flt(lot.width_mm)) > 0.05
			if settings.enforce_offcut_creation and (geometry_changed or weight + Decimal("0.001") < full):
				frappe.throw("A partial cut needs the remaining piece as an offcut or scrap row on this voucher")
			continue
		result = assess_conservation(
			weight,
			parts["offcut"],
			parts["scrap"],
			parts["consumed"],
			warn_pct=settings.weight_deviation_warn_pct,
		)
		if result.level == "warn":
			warnings.append(
				f"Cut of lot {lot_name} does not conserve weight: issued {flt(weight, 3)} kg, "
				f"accounted {flt(result.accounted_kg, 3)} kg"
			)


def _calculated_weight(item, row, settings):
	qty = row.qty_pieces
	if row.weight_basis == "Kg Per Metre" or (row.weight_basis == "Weighment" and item.fabtrk_shape != "Plate"):
		if not item.fabtrk_kg_per_metre:
			return None
		return weight_from_kg_per_metre(row.length_mm, item.fabtrk_kg_per_metre, qty)
	if item.fabtrk_shape == "Plate" and item.fabtrk_thickness_mm:
		return weight_from_density(
			row.length_mm,
			row.width_mm or 0,
			item.fabtrk_thickness_mm,
			settings.default_density_kg_m3,
			qty,
		)
	return None


def _voucher_lines(doc):
	lines = []
	purpose = _purpose(doc)
	for item in doc.items:
		rate = item.get("valuation_rate") or item.get("basic_rate") or 0
		qty = _d(item.qty)
		if purpose in ("Purchase Receipt", "Material Receipt"):
			warehouse = item.warehouse if purpose == "Purchase Receipt" else item.t_warehouse
			lines.append({"item_code": item.item_code, "warehouse": warehouse, "qty": qty, "direction": "in", "rate": _d(rate)})
		elif purpose == "Material Issue":
			lines.append({"item_code": item.item_code, "warehouse": item.s_warehouse, "qty": qty, "direction": "out", "rate": _d(rate)})
		elif purpose in ("Material Transfer", "Repack"):
			lines.append({"item_code": item.item_code, "warehouse": item.s_warehouse, "qty": qty, "direction": "out", "rate": _d(rate)})
			lines.append({"item_code": item.item_code, "warehouse": item.t_warehouse, "qty": qty, "direction": "in", "rate": _d(rate)})
		elif _tracked(item.item_code):
			frappe.throw(f"Fabtrk does not post geometry for {purpose}")
	return lines


def _kind(doc, row):
	purpose = _purpose(doc)
	if purpose in ("Purchase Receipt", "Material Receipt"):
		return "in"
	if not row.lot:
		return "in"
	if purpose == "Material Transfer" and not _has_remainder(doc, row.lot):
		lot_length, lot_width = frappe.db.get_value("Fabtrk Lot", row.lot, ["length_mm", "width_mm"])
		if abs(flt(row.length_mm) - flt(lot_length)) < 0.05 and abs(flt(row.width_mm) - flt(lot_width)) < 0.05:
			return "move"
	return "out"


def _has_remainder(doc, lot_name):
	return any(row.parent_lot == lot_name for row in doc.get("fabtrk_lot_details") or [])


def _purpose(doc):
	if doc.doctype == "Purchase Receipt":
		return "Purchase Receipt"
	return doc.purpose


def _on_voucher(doc, item_code):
	return any(item.item_code == item_code for item in doc.items)


def _tracked(item_code):
	return bool(frappe.db.get_value("Item", item_code, "fabtrk_is_geometry_tracked"))


def _group_key(doc, row):
	return (
		row.item_code,
		row.warehouse,
		round(flt(row.length_mm), 3),
		round(flt(row.width_mm), 3),
		row.weight_basis,
		row.source_reference or doc.fabtrk_reference,
		row.parent_lot or "",
		row.lot_type or "Parent",
	)


def _find_open_lot(row, doc):
	origin = row.source_reference or doc.fabtrk_reference
	found = frappe.db.sql(
		"""
		select name from `tabFabtrk Lot`
		where item_code=%s and warehouse=%s and weight_basis=%s
			and ifnull(source_reference, '')=%s and status='In Stock'
			and ifnull(parent_lot, '')=%s
			and abs(length_mm-%s)<0.05 and abs(ifnull(width_mm, 0)-%s)<0.05
		order by creation limit 1
		""",
		(row.item_code, row.warehouse, row.weight_basis, origin, row.parent_lot or "", row.length_mm, row.width_mm or 0),
	)
	return found[0][0] if found else None


def _lot_balance(name):
	qty, weight = frappe.db.get_value("Fabtrk Lot", name, ["qty_pieces", "weight_kg"])
	return _d(qty), _d(weight)


def _rate_for(doc, item_code, parent_lot):
	if parent_lot:
		return flt(frappe.db.get_value("Fabtrk Lot", parent_lot, "valuation_rate"))
	for line in _voucher_lines(doc):
		if line["item_code"] == item_code and line["rate"]:
			return float(line["rate"])
	return 0


def _reject_duplicate(doc):
	existing = frappe.db.get_value(
		"Fabtrk Posting Key", _posting_key(doc), ["voucher_type", "voucher_no"], as_dict=True
	)
	if existing:
		raise DuplicateReference(existing.voucher_type, existing.voucher_no, doc.fabtrk_reference)


def _insert_posting_key(doc):
	_reject_duplicate(doc)
	try:
		frappe.get_doc(
			{
				"doctype": "Fabtrk Posting Key",
				"posting_key": _posting_key(doc),
				"voucher_type": doc.doctype,
				"voucher_no": doc.name,
				"reference": doc.fabtrk_reference,
			}
		).insert(ignore_permissions=True)
	except frappe.DuplicateEntryError:
		_reject_duplicate(doc)


def _posting_key(doc):
	return f"{doc.doctype}::{doc.fabtrk_reference}"


def _settings():
	return frappe.get_single("Fabtrk Settings")


def _preview_bin(item_code, warehouse, effect):
	current = _d(frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"))
	if effect["action"] == "move":
		return float(current)
	return float(current + effect["delta_weight"])


def _d(value):
	return Decimal(str(value or 0))
