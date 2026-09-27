"""Plain-Python tests for geometry rules. No Frappe import."""

import unittest
from dataclasses import dataclass
from decimal import Decimal

from fabtrk.geometry import (
	GeometryItemError,
	OverIssue,
	apply_movement,
	assess_conservation,
	assess_weight,
	average_kg_per_piece,
	group_receipt_rows,
	guard_issue,
	kg_to_mt,
	receipt_identity,
	round_for_display,
	suggest_scrap,
	total_length_mm,
	validate_geometry_tracked_item,
	weight_from_density,
)


DENSITY = Decimal(7850)


@dataclass
class LengthRow:
	length_mm: Decimal
	qty_pieces: Decimal


@dataclass
class ReceiptRow:
	item_code: str
	warehouse: str
	length_mm: Decimal
	width_mm: Decimal
	qty_pieces: Decimal
	weight_kg: Decimal
	weight_basis: str
	origin: str = ""


class TestSignedLength(unittest.TestCase):
	def test_ac3_issue_decreases_total_length(self):
		on_hand = [
			LengthRow(Decimal(5800), Decimal(6)),
			LengthRow(Decimal(8000), Decimal(1)),
		]
		self.assertEqual(total_length_mm(on_hand), Decimal(42800))

		after_issue = [
			LengthRow(Decimal(5800), Decimal(3)),
			LengthRow(Decimal(8000), Decimal(1)),
		]
		correct = total_length_mm(after_issue)
		bare = sum(row.length_mm for row in after_issue)
		self.assertEqual(correct, Decimal(25400))
		self.assertLess(correct, total_length_mm(on_hand))
		self.assertNotEqual(correct, bare)

	def test_negative_qty_is_a_signed_delta(self):
		self.assertEqual(
			total_length_mm([(Decimal(5800), Decimal(-3))]),
			Decimal(-17400),
		)


class TestWeight(unittest.TestCase):
	def test_plate_density_matches_published_figures(self):
		cases = [
			(5800, 1500, Decimal("682.95"), Decimal("683.0")),
			(8000, 1500, Decimal(942), Decimal("942.0")),
			(6300, 1500, Decimal("741.825"), Decimal("741.8")),
			(4000, 1500, Decimal(471), Decimal("471.0")),
			(2300, 1500, Decimal("270.825"), Decimal("270.8")),
		]
		for length, width, exact, shown in cases:
			weight = weight_from_density(length, width, 10, DENSITY, 1)
			self.assertEqual(weight, exact)
			self.assertEqual(round_for_display(weight), shown)

	def test_invoice_weights_are_inside_five_percent(self):
		for calculated, invoiced in (
			(Decimal("682.95"), Decimal("686.7")),
			(Decimal(942), Decimal(940)),
		):
			result = assess_weight(calculated, invoiced, "Density")
			self.assertEqual(result.level, "ok")
			self.assertLess(result.deviation_pct, Decimal(5))

	def test_six_percent_warns_and_twelve_percent_blocks(self):
		calculated = Decimal(100)
		warned = assess_weight(calculated, Decimal(106), "Density")
		blocked = assess_weight(calculated, Decimal(112), "Weighment")
		self.assertEqual(warned.level, "warn")
		self.assertEqual(blocked.level, "block")
		self.assertIn("Weighment", blocked.basis)

	def test_mt_is_kg_over_1000(self):
		self.assertEqual(kg_to_mt(Decimal("77866.6")), Decimal("77.8666"))
		self.assertEqual(kg_to_mt(Decimal(5060)), Decimal("5.060"))

	def test_kg_per_piece_is_an_average(self):
		self.assertEqual(average_kg_per_piece(Decimal(4120), Decimal(6)), Decimal(4120) / Decimal(6))
		self.assertIsNone(average_kg_per_piece(Decimal(10), Decimal(0)))


class TestConservationAndIssue(unittest.TestCase):
	def test_cut_conserves_weight(self):
		result = assess_conservation(
			issued_kg=Decimal("741.825"),
			offcut_kg=Decimal("270.825"),
			scrap_kg=0,
			consumed_kg=Decimal(471),
		)
		self.assertEqual(result.level, "ok")
		self.assertEqual(result.accounted_kg, result.issued_kg)

	def test_over_issue_names_available_pieces(self):
		with self.assertRaises(OverIssue) as caught:
			guard_issue(8, 6, Decimal(100), Decimal(1000))
		self.assertIn("6", str(caught.exception))
		self.assertEqual(caught.exception.available_pieces, Decimal(6))

	def test_movement_decrements_and_marks_consumed(self):
		qty, weight, status = apply_movement(6, Decimal(4120), -3, Decimal(-2060))
		self.assertEqual((qty, weight, status), (Decimal(3), Decimal(2060), "In Stock"))
		qty, weight, status = apply_movement(qty, weight, -3, Decimal(-2060))
		self.assertEqual(status, "Consumed")
		self.assertEqual(qty, Decimal(0))

	def test_movement_refuses_to_go_negative(self):
		with self.assertRaises(OverIssue):
			apply_movement(6, Decimal(4120), -8, Decimal(-5000))


class TestLotsAndItems(unittest.TestCase):
	def test_receipt_groups_pieces_into_two_lots(self):
		rows = [
			ReceiptRow("PL-E350-10MM", "Main - FXL", Decimal(5800), Decimal(1500), Decimal(6), Decimal(4120), "Weighment", "INV AS/077/26-27"),
			ReceiptRow("PL-E350-10MM", "Main - FXL", Decimal(8000), Decimal(1500), Decimal(1), Decimal(940), "Weighment", "INV AS/077/26-27"),
		]
		grouped = group_receipt_rows(rows)
		self.assertEqual(len(grouped), 2)
		self.assertEqual(sum(qty for qty, _weight in grouped.values()), Decimal(7))
		self.assertEqual(sum(weight for _qty, weight in grouped.values()), Decimal(5060))

	def test_duplicate_identity_matches_geometry(self):
		first = receipt_identity("Purchase Receipt", "INV AS/077/26-27", "PL-E350-10MM", 5800, 1500)
		again = receipt_identity("Purchase Receipt", "INV AS/077/26-27", "PL-E350-10MM", Decimal(5800), Decimal(1500))
		other_size = receipt_identity("Purchase Receipt", "INV AS/077/26-27", "PL-E350-10MM", 8000, 1500)
		self.assertEqual(first, again)
		self.assertNotEqual(first, other_size)

	def test_tracked_item_rejects_batch_and_serial(self):
		with self.assertRaises(GeometryItemError) as caught:
			validate_geometry_tracked_item(
				stock_uom="Kg",
				has_batch_no=1,
				has_serial_no=0,
				shape="Plate",
				thickness_mm=10,
				kg_per_metre=0,
				is_geometry_tracked=1,
			)
		self.assertIn("has_batch_no", str(caught.exception))

	def test_plate_needs_thickness_section_needs_kg_per_metre(self):
		with self.assertRaises(GeometryItemError):
			validate_geometry_tracked_item(
				stock_uom="Nos",
				has_batch_no=0,
				has_serial_no=0,
				shape="Plate",
				thickness_mm=0,
				kg_per_metre=0,
				is_geometry_tracked=1,
			)
		with self.assertRaises(GeometryItemError):
			validate_geometry_tracked_item(
				stock_uom="Kg",
				has_batch_no=0,
				has_serial_no=0,
				shape="Round Bar",
				thickness_mm=0,
				kg_per_metre=0,
				is_geometry_tracked=1,
			)

	def test_untracked_item_is_ignored(self):
		validate_geometry_tracked_item(
			stock_uom="Nos",
			has_batch_no=1,
			has_serial_no=1,
			shape="Other",
			thickness_mm=0,
			kg_per_metre=0,
			is_geometry_tracked=0,
		)

	def test_scrap_suggestion_uses_each_minimum(self):
		self.assertFalse(suggest_scrap(2300, 1500, 500, 300))
		self.assertTrue(suggest_scrap(200, 1500, 500, 300))
		self.assertTrue(suggest_scrap(2300, 100, 500, 300))
		self.assertFalse(suggest_scrap(800, 0, 500, 300))
		self.assertTrue(suggest_scrap(400, 0, 500, 300))


if __name__ == "__main__":
	unittest.main()
