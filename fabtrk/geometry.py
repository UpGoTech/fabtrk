"""Metal lot geometry and weight rules.

This module imports nothing from Frappe. Length is per piece and piece
counts are signed, so a length total is ``sum(length_mm * qty_pieces)``.
Weights are exact ``Decimal`` values; round only for display.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

PLATE = "Plate"
SECTION_SHAPES = frozenset(
	{"Angle", "Channel", "Beam", "NPB", "Pipe", "Tube", "Round Bar"}
)
STOCK_UOMS = frozenset({"Kg", "MT"})


def _d(value) -> Decimal:
	if isinstance(value, Decimal):
		return value
	return Decimal(str(value))


def _pair(row):
	if isinstance(row, (tuple, list)):
		return _d(row[0]), _d(row[1])
	return _d(row.length_mm), _d(row.qty_pieces)


def total_length_mm(rows) -> Decimal:
	"""Signed length. ``qty_pieces`` may be negative on an issue."""
	total = Decimal(0)
	for row in rows:
		length_mm, qty_pieces = _pair(row)
		total += length_mm * qty_pieces
	return total


def weight_from_kg_per_metre(length_mm, kg_per_metre, qty_pieces) -> Decimal:
	return (_d(length_mm) / Decimal(1000)) * _d(kg_per_metre) * _d(qty_pieces)


def weight_from_density(length_mm, width_mm, thickness_mm, density_kg_m3, qty_pieces) -> Decimal:
	metres = Decimal(1000)
	return (
		(_d(length_mm) / metres)
		* (_d(width_mm) / metres)
		* (_d(thickness_mm) / metres)
		* _d(density_kg_m3)
		* _d(qty_pieces)
	)


def round_for_display(value, places: int = 1) -> Decimal:
	return _d(value).quantize(Decimal(10) ** -places)


def kg_to_mt(weight_kg) -> Decimal:
	return _d(weight_kg) / Decimal(1000)


def average_kg_per_piece(weight_kg, qty_pieces):
	qty = _d(qty_pieces)
	if qty == 0:
		return None
	return _d(weight_kg) / qty


@dataclass(frozen=True)
class DeviationAssessment:
	level: str
	calculated: Decimal
	entered: Decimal
	deviation_pct: Decimal
	basis: str


def assess_weight(calculated, entered, basis: str, warn_pct=5, block_pct=10) -> DeviationAssessment:
	calculated = _d(calculated)
	entered = _d(entered)
	if calculated == 0:
		raise ValueError("calculated weight is zero")
	pct = abs(entered - calculated) / abs(calculated) * Decimal(100)
	if pct > _d(block_pct):
		level = "block"
	elif pct > _d(warn_pct):
		level = "warn"
	else:
		level = "ok"
	return DeviationAssessment(level, calculated, entered, pct, basis)


@dataclass(frozen=True)
class ConservationAssessment:
	level: str
	issued_kg: Decimal
	accounted_kg: Decimal
	deviation_pct: Decimal


def assess_conservation(issued_kg, offcut_kg, scrap_kg, consumed_kg, warn_pct=5) -> ConservationAssessment:
	issued = _d(issued_kg)
	accounted = _d(offcut_kg) + _d(scrap_kg) + _d(consumed_kg)
	if issued == 0:
		pct = Decimal(0) if accounted == 0 else Decimal(100)
	else:
		pct = abs(accounted - issued) / abs(issued) * Decimal(100)
	level = "warn" if pct > _d(warn_pct) else "ok"
	return ConservationAssessment(level, issued, accounted, pct)


class OverIssue(Exception):
	def __init__(self, available_pieces=None, available_kg=None):
		self.available_pieces = available_pieces
		self.available_kg = available_kg
		parts = []
		if available_pieces is not None:
			parts.append(f"{available_pieces} pieces available")
		if available_kg is not None:
			parts.append(f"{available_kg} kg available")
		super().__init__("over-issue refused: " + ", ".join(parts))


def guard_issue(qty_pieces, lot_qty_pieces, weight_kg, bin_weight_kg, allow_negative=False):
	qty = _d(qty_pieces)
	lot_qty = _d(lot_qty_pieces)
	weight = _d(weight_kg)
	bin_weight = _d(bin_weight_kg)
	if allow_negative:
		return
	over_pieces = qty > lot_qty
	over_weight = weight > bin_weight
	if over_pieces or over_weight:
		raise OverIssue(
			available_pieces=lot_qty if over_pieces else None,
			available_kg=bin_weight if over_weight else None,
		)


def apply_movement(qty_pieces, weight_kg, delta_qty, delta_weight, allow_negative=False):
	new_qty = _d(qty_pieces) + _d(delta_qty)
	new_weight = _d(weight_kg) + _d(delta_weight)
	if not allow_negative and (new_qty < 0 or new_weight < 0):
		raise OverIssue(
			available_pieces=_d(qty_pieces) if new_qty < 0 else None,
			available_kg=_d(weight_kg) if new_weight < 0 else None,
		)
	status = "Consumed" if new_qty == 0 else "In Stock"
	return new_qty, new_weight, status


class GeometryItemError(Exception):
	pass


def validate_geometry_tracked_item(
	*,
	stock_uom,
	has_batch_no,
	has_serial_no,
	shape,
	thickness_mm,
	kg_per_metre,
	is_geometry_tracked,
):
	if not is_geometry_tracked:
		return
	errors = []
	if stock_uom not in STOCK_UOMS:
		errors.append("stock_uom must be Kg or MT")
	if has_batch_no:
		errors.append("has_batch_no must be off for geometry-tracked items")
	if has_serial_no:
		errors.append("has_serial_no must be off for geometry-tracked items")
	if shape == PLATE and _d(thickness_mm or 0) <= 0:
		errors.append("Plate requires thickness_mm > 0")
	if shape in SECTION_SHAPES and _d(kg_per_metre or 0) <= 0:
		errors.append(f"{shape} requires kg_per_metre > 0")
	if errors:
		raise GeometryItemError("; ".join(errors))


def lot_match_key(item_code, warehouse, length_mm, width_mm, weight_basis, origin):
	return (
		item_code,
		warehouse,
		_d(length_mm),
		_d(width_mm),
		weight_basis,
		origin or "",
	)


def group_receipt_rows(rows):
	"""Collapse identical geometry into one lot balance. One row is not one piece."""
	grouped = {}
	for row in rows:
		key = lot_match_key(
			row.item_code,
			row.warehouse,
			row.length_mm,
			row.width_mm,
			row.weight_basis,
			row.origin,
		)
		qty, weight = grouped.get(key, (Decimal(0), Decimal(0)))
		grouped[key] = (qty + _d(row.qty_pieces), weight + _d(row.weight_kg))
	return grouped


def receipt_identity(voucher_type, reference, item_code, length_mm, width_mm):
	return (voucher_type, reference, item_code, _d(length_mm), _d(width_mm))


def suggest_scrap(length_mm, width_mm, scrap_min_length_mm, scrap_min_width_mm) -> bool:
	"""Suggest scrap when a side is under its minimum. Width 0 is a section, so only length applies."""
	if _d(length_mm) < _d(scrap_min_length_mm):
		return True
	return _d(width_mm) > 0 and _d(width_mm) < _d(scrap_min_width_mm)
