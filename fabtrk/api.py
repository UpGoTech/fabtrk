"""Token-auth posting and read APIs for geometry lots.

Every write takes ``reference``. Posting the same voucher type and reference
again returns the existing document and writes nothing. ``dry_run=1`` validates
and returns the same receipt shape without writing.
"""

from __future__ import annotations

import frappe
from frappe.utils import cint, flt, today

from fabtrk.lots import DuplicateReference, plan_voucher_preview, post_opening_lots
from fabtrk.stock_reports import geometry_rows, lot_movements, offcut_rows, reconcile_rows
from fabtrk.stock_setup import ROLES, company_name, warehouse_name

POSTERS = {"Fabtrk Stock Owner", "Fabtrk Stock Storekeeper", "System Manager"}


@frappe.whitelist(methods=["POST"])
def post_receipt(reference, lines, posting_date=None, voucher_type="Stock Entry", supplier=None, dry_run=0, company=None):
	_require_poster()
	voucher_type = voucher_type or "Stock Entry"
	return _post(voucher_type, reference, dry_run, lambda: _receipt_doc(reference, lines, posting_date, voucher_type, supplier, company))


@frappe.whitelist(methods=["POST"])
def post_issue(reference, lines, posting_date=None, origin_job=None, dry_run=0, company=None):
	_require_poster()
	return _post("Stock Entry", reference, dry_run, lambda: _issue_doc(reference, lines, posting_date, origin_job, company))


@frappe.whitelist(methods=["POST"])
def post_transfer(reference, lot, to_warehouse, posting_date=None, dry_run=0, company=None):
	_require_poster()
	return _post(
		"Stock Entry",
		reference,
		dry_run,
		lambda: _transfer_doc(reference, lot, to_warehouse, posting_date, company),
	)


@frappe.whitelist(methods=["POST"])
def post_adjustment(reference, lot, qty_pieces, weight_kg, reason, posting_date=None, dry_run=0, company=None):
	_require_poster()
	if not reason:
		frappe.throw("An adjustment needs a reason")
	return _post(
		"Stock Entry",
		reference,
		dry_run,
		lambda: _adjustment_doc(reference, lot, qty_pieces, weight_kg, reason, posting_date, company),
	)


@frappe.whitelist(methods=["POST"])
def import_opening_lots(reference, rows, posting_date=None, dry_run=0, company=None):
	_require_poster()
	reference = _reference(reference)
	rows = _json(rows)
	posting_date = posting_date or today()
	company = company or company_name()
	existing = _existing_response("Stock Reconciliation", reference)
	if existing:
		return existing
	if cint(dry_run):
		return {
			"document_name": None,
			"document_type": "Stock Reconciliation",
			"reference": reference,
			"dry_run": 1,
			"duplicate": 0,
			"warnings": [],
			"lines": [
				{
					"item_code": row["item_code"],
					"warehouse": row["warehouse"],
					"length_mm": row["length_mm"],
					"width_mm": row.get("width_mm") or 0,
					"qty_pieces": row["qty_pieces"],
					"weight_kg": row["weight_kg"],
					"weight_mt": flt(row["weight_kg"]) / 1000,
				}
				for row in rows
			],
		}
	grouped = {}
	for row in rows:
		key = (row["item_code"], row["warehouse"])
		grouped[key] = grouped.get(key, 0) + flt(row["weight_kg"])
	reconciliation = frappe.get_doc(
		{
			"doctype": "Stock Reconciliation",
			"company": company,
			"purpose": "Opening Stock",
			"posting_date": posting_date,
			"fabtrk_reference": reference,
			"items": [
				{
					"item_code": item_code,
					"warehouse": warehouse,
					"qty": qty,
					"valuation_rate": 0,
				}
				for (item_code, warehouse), qty in grouped.items()
			],
		}
	)
	frappe.db.savepoint("fabtrk_write")
	try:
		reconciliation.insert()
		reconciliation.submit()
		post_opening_lots(reference, posting_date, rows, reconciliation.doctype, reconciliation.name)
	except Exception:
		frappe.db.rollback(save_point="fabtrk_write")
		raise
	return _saved_response(reconciliation)


@frappe.whitelist(methods=["GET"])
def stock_by_geometry(item_code=None, warehouse=None, grade=None):
	_require_reader()
	return geometry_rows({"item_code": item_code, "warehouse": warehouse, "grade": grade})


@frappe.whitelist(methods=["GET"])
def lot_search(min_length_mm=0, min_width_mm=0, item_code=None, grade=None, warehouse=None):
	_require_reader()
	return offcut_rows(
		{
			"min_length_mm": min_length_mm,
			"min_width_mm": min_width_mm,
			"item_code": item_code,
			"grade": grade,
			"warehouse": warehouse,
		}
	)


@frappe.whitelist(methods=["GET"])
def lot_trace(lot):
	_require_reader()
	return lot_movements(lot=lot)


@frappe.whitelist(methods=["GET"])
def reconcile():
	_require_reader()
	return reconcile_rows()


def _post(voucher_type, reference, dry_run, builder):
	reference = _reference(reference)
	existing = _existing_response(voucher_type, reference)
	if existing:
		return existing
	doc = builder()
	if cint(dry_run):
		preview = plan_voucher_preview(doc)
		return {
			"document_name": None,
			"document_type": doc.doctype,
			"reference": reference,
			"dry_run": 1,
			"duplicate": 0,
			"warnings": preview["warnings"],
			"lines": preview["lines"],
		}
	frappe.db.savepoint("fabtrk_write")
	try:
		doc.insert()
		doc.submit()
	except DuplicateReference:
		frappe.db.rollback(save_point="fabtrk_write")
		found = _existing_response(doc.doctype, reference)
		if found:
			return found
		raise
	except Exception:
		frappe.db.rollback(save_point="fabtrk_write")
		raise
	return _saved_response(doc)


def _receipt_doc(reference, lines, posting_date, voucher_type, supplier, company):
	company = company or company_name()
	posting_date = posting_date or today()
	lines = _json(lines)
	items = []
	details = []
	for line in lines:
		lots = line.get("lots") or []
		warehouse = line["warehouse"]
		weight = flt(line.get("qty_kg") or sum(flt(lot["weight_kg"]) for lot in lots))
		items.append(_item_row(line["item_code"], weight, warehouse, "in", rate=flt(line.get("rate") or 0)))
		for lot in lots:
			details.append(
				{
					"item_code": line["item_code"],
					"warehouse": warehouse,
					"length_mm": lot["length_mm"],
					"width_mm": lot.get("width_mm") or 0,
					"qty_pieces": lot["qty_pieces"],
					"weight_kg": lot["weight_kg"],
					"weight_basis": lot.get("weight_basis") or "Weighment",
					"weight_basis_source": lot.get("weight_basis_source"),
					"source_reference": lot.get("source_reference") or reference,
					"lot": lot.get("lot"),
					"lot_type": lot.get("lot_type") or "Parent",
					"remarks": lot.get("remarks"),
				}
			)
	if voucher_type == "Purchase Receipt":
		if not supplier:
			frappe.throw("Supplier is required for a Purchase Receipt")
		return frappe.get_doc(
			{
				"doctype": "Purchase Receipt",
				"supplier": supplier,
				"company": company,
				"posting_date": posting_date,
				"currency": "INR",
				"conversion_rate": 1,
				"fabtrk_reference": reference,
				"items": [
					{
						"item_code": row["item_code"],
						"qty": row["qty"],
						"warehouse": row["t_warehouse"],
						"uom": "Kg",
						"stock_uom": "Kg",
						"conversion_factor": 1,
						"rate": flt(line.get("rate") or 0),
					}
					for row, line in zip(items, lines, strict=True)
				],
				"fabtrk_lot_details": details,
			}
		)
	return frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"purpose": "Material Receipt",
			"company": company,
			"posting_date": posting_date,
			"fabtrk_reference": reference,
			"items": items,
			"fabtrk_lot_details": details,
		}
	)


def _issue_doc(reference, lines, posting_date, origin_job, company):
	company = company or company_name()
	lines = _json(lines)
	items = []
	details = []
	transfer = False
	for line in lines:
		lot = frappe.get_doc("Fabtrk Lot", line["lot"])
		qty_pieces = flt(line.get("qty_pieces") or lot.qty_pieces)
		remainder = [line.get("consumed"), line.get("offcut"), line.get("scrap")]
		if any(remainder):
			transfer = True
			part_weight = 0
			for payload, label, lot_type in (
				(line.get("consumed"), "Work In Progress", "Parent"),
				(line.get("offcut"), "Offcuts", "Offcut"),
				(line.get("scrap"), "Scrap", "Scrap"),
			):
				if not payload:
					continue
				weight = flt(payload["weight_kg"])
				part_weight += weight
				target = payload.get("warehouse") or warehouse_name(label, company)
				items.append(_transfer_row(lot.item_code, weight, lot.warehouse, target))
				details.append(
					_detail_from_lot(
						lot,
						target,
						payload.get("qty_pieces") or 1,
						weight,
						payload["length_mm"],
						payload.get("width_mm") or 0,
						lot_type=payload.get("lot_type") or lot_type,
						parent_lot=lot.name,
					)
				)
			details.append(
				_detail_from_lot(
					lot,
					lot.warehouse,
					qty_pieces,
					part_weight,
					lot.length_mm,
					lot.width_mm,
					linked=True,
				)
			)
		else:
			weight = flt(line.get("weight_kg") if line.get("weight_kg") is not None else flt(lot.kg_per_piece) * qty_pieces)
			items.append(_item_row(lot.item_code, weight, lot.warehouse, "out"))
			details.append(
				_detail_from_lot(lot, lot.warehouse, qty_pieces, weight, lot.length_mm, lot.width_mm, linked=True)
			)
	purpose = "Material Transfer" if transfer else "Material Issue"
	return frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": purpose,
			"purpose": purpose,
			"company": company,
			"posting_date": posting_date or today(),
			"fabtrk_reference": reference,
			"fabtrk_origin_job": origin_job,
			"items": items,
			"fabtrk_lot_details": details,
		}
	)


def _transfer_doc(reference, lot, to_warehouse, posting_date, company):
	lot = frappe.get_doc("Fabtrk Lot", lot)
	return frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Transfer",
			"purpose": "Material Transfer",
			"company": company or company_name(),
			"posting_date": posting_date or today(),
			"fabtrk_reference": reference,
			"items": [_transfer_row(lot.item_code, lot.weight_kg, lot.warehouse, to_warehouse)],
			"fabtrk_lot_details": [
				_detail_from_lot(
					lot,
					to_warehouse,
					lot.qty_pieces,
					lot.weight_kg,
					lot.length_mm,
					lot.width_mm,
					linked=True,
				)
			],
		}
	)


def _adjustment_doc(reference, lot, qty_pieces, weight_kg, reason, posting_date, company):
	lot = frappe.get_doc("Fabtrk Lot", lot)
	qty_pieces = flt(qty_pieces)
	weight_kg = flt(weight_kg)
	inbound = weight_kg > 0 or (weight_kg == 0 and qty_pieces > 0)
	purpose = "Material Receipt" if inbound else "Material Issue"
	warehouse = lot.warehouse
	item = _item_row(lot.item_code, abs(weight_kg), warehouse, "in" if inbound else "out")
	detail = _detail_from_lot(
		lot,
		warehouse,
		abs(qty_pieces),
		abs(weight_kg),
		lot.length_mm,
		lot.width_mm,
		linked=True,
		reason=reason,
	)
	return frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": purpose,
			"purpose": purpose,
			"company": company or company_name(),
			"posting_date": posting_date or today(),
			"fabtrk_reference": reference,
			"fabtrk_reason": reason,
			"fabtrk_is_adjustment": 1,
			"items": [item],
			"fabtrk_lot_details": [detail],
		}
	)


def _item_row(item_code, qty, warehouse, direction, rate=0):
	row = {
		"item_code": item_code,
		"qty": qty,
		"uom": "Kg",
		"stock_uom": "Kg",
		"conversion_factor": 1,
		"basic_rate": rate or 0,
		"allow_zero_valuation_rate": 0 if rate else 1,
	}
	if direction == "in":
		row["t_warehouse"] = warehouse
	else:
		row["s_warehouse"] = warehouse
	return row


def _transfer_row(item_code, qty, source, target):
	return {
		"item_code": item_code,
		"qty": qty,
		"uom": "Kg",
		"stock_uom": "Kg",
		"conversion_factor": 1,
		"allow_zero_valuation_rate": 1,
		"s_warehouse": source,
		"t_warehouse": target,
	}


def _detail_from_lot(lot, warehouse, qty_pieces, weight_kg, length_mm, width_mm, linked=False, lot_type=None, parent_lot=None, reason=None):
	return {
		"item_code": lot.item_code,
		"warehouse": warehouse,
		"length_mm": length_mm,
		"width_mm": width_mm or 0,
		"qty_pieces": qty_pieces,
		"weight_kg": weight_kg,
		"weight_basis": lot.weight_basis,
		"weight_basis_source": lot.weight_basis_source,
		"source_reference": lot.source_reference,
		"lot": lot.name if linked else None,
		"lot_type": lot_type or "",
		"parent_lot": parent_lot,
		"reason": reason,
	}


def _saved_response(doc):
	movements = frappe.get_all(
		"Fabtrk Lot Movement",
		filters={"voucher_type": doc.doctype, "voucher_no": doc.name},
		fields=[
			"item_code",
			"warehouse",
			"length_mm",
			"width_mm",
			"qty_pieces",
			"weight_kg",
			"lot",
			"resulting_qty_pieces",
			"resulting_weight_kg",
			"reason",
		],
		order_by="creation asc",
	)
	lines = []
	for movement in movements:
		if movement.reason == "Cancel":
			continue
		bin_qty = flt(frappe.db.get_value("Bin", {"item_code": movement.item_code, "warehouse": movement.warehouse}, "actual_qty"))
		lines.append(
			{
				"item_code": movement.item_code,
				"warehouse": movement.warehouse,
				"length_mm": movement.length_mm,
				"width_mm": movement.width_mm,
				"qty_pieces": movement.qty_pieces,
				"weight_kg": movement.weight_kg,
				"weight_mt": flt(movement.weight_kg) / 1000,
				"lot": movement.lot,
				"lot_qty_pieces": movement.resulting_qty_pieces,
				"lot_weight_kg": movement.resulting_weight_kg,
				"bin_qty": bin_qty,
			}
		)
	return {
		"document_name": doc.name,
		"document_type": doc.doctype,
		"reference": doc.get("fabtrk_reference"),
		"dry_run": 0,
		"duplicate": 0,
		"warnings": list(getattr(frappe.flags, "fabtrk_warnings", None) or []),
		"lines": lines,
	}


def _existing_response(voucher_type, reference):
	row = frappe.db.get_value(
		"Fabtrk Posting Key", f"{voucher_type}::{reference}", ["voucher_type", "voucher_no"], as_dict=True
	)
	if not row:
		return None
	doc = frappe.get_doc(row.voucher_type, row.voucher_no)
	response = _saved_response(doc)
	response["duplicate"] = 1
	return response


def _reference(reference):
	reference = (reference or "").strip()
	if not reference:
		frappe.throw("Reference is required")
	return reference


def _json(value):
	if isinstance(value, str):
		return frappe.parse_json(value)
	return value


def _require_poster():
	if frappe.session.user == "Administrator":
		return
	if not set(frappe.get_roles()).intersection(POSTERS):
		frappe.throw("Not permitted to post Fabtrk stock", frappe.PermissionError)


def _require_reader():
	if frappe.session.user == "Administrator":
		return
	allowed = set(ROLES) | {"System Manager"}
	if not set(frappe.get_roles()).intersection(allowed):
		frappe.throw("Not permitted to read Fabtrk stock", frappe.PermissionError)
