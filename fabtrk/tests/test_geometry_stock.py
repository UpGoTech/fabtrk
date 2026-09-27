import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt

from fabtrk.api import post_issue, post_receipt
from fabtrk.geometry import weight_from_density
from fabtrk.stock_reports import reconcile_rows
from fabtrk.stock_setup import warehouse_name


class TestFabtrkLot(IntegrationTestCase):
	def setUp(self):
		self.item = "PL-E350-10MM"
		self.warehouse = warehouse_name("Main")
		self.company = frappe.db.get_value("Company", {"abbr": "FXL"}, "name")

	def test_ac1_receipt_creates_two_lots(self):
		before = flt(self._bin())
		result = self._receipt("INV AS/077/26-27")
		self.assertEqual(len(result["lines"]), 2)
		self.assertEqual(frappe.db.count("Fabtrk Lot", {"item_code": self.item, "source_reference": "INV AS/077/26-27"}), 2)
		self.assertEqual(frappe.db.count("Fabtrk Lot Movement", {"reference": "INV AS/077/26-27"}), 2)
		self.assertEqual(flt(self._bin()) - before, 5060)

	def test_ac3_signed_length_drops_on_issue(self):
		reference = "INV AS/077/26-27 LENGTH"
		before_bin = flt(self._bin())
		self._receipt(reference)
		before = self._length_for(reference)
		self.assertEqual(before, 42800)
		lot = frappe.db.get_value(
			"Fabtrk Lot",
			{"source_reference": reference, "length_mm": 5800},
			"name",
		)
		post_issue(
			"ISSUE 3 OF 5800",
			[{"lot": lot, "qty_pieces": 3, "weight_kg": 2060}],
			company=self.company,
		)
		after = self._length_for(reference)
		bare = frappe.db.sql(
			"select sum(length_mm) from `tabFabtrk Lot` where source_reference=%s",
			reference,
		)[0][0]
		self.assertEqual(after, 25400)
		self.assertLess(after, before)
		self.assertNotEqual(after, bare)
		self.assertEqual(flt(self._bin()) - before_bin, 3000)
		weight = frappe.db.sql(
			"select sum(weight_kg) from `tabFabtrk Lot` where source_reference=%s",
			reference,
		)[0][0]
		self.assertEqual(flt(weight), 3000)

	def test_ac4_offcut_and_conservation(self):
		parent_weight = float(weight_from_density(6300, 1500, 10, 7850, 1))
		consumed = float(weight_from_density(4000, 1500, 10, 7850, 1))
		offcut = float(weight_from_density(2300, 1500, 10, 7850, 1))
		posted = post_receipt(
			"CUT PARENT",
			[
				{
					"item_code": self.item,
					"warehouse": self.warehouse,
					"lots": [
						{
							"length_mm": 6300,
							"width_mm": 1500,
							"qty_pieces": 1,
							"weight_kg": parent_weight,
							"weight_basis": "Density",
							"weight_basis_source": "Fabtrk Settings 7850",
						}
					],
				}
			],
			company=self.company,
		)
		parent = posted["lines"][0]["lot"]
		post_issue(
			"CUT 4000",
			[
				{
					"lot": parent,
					"qty_pieces": 1,
					"consumed": {"length_mm": 4000, "width_mm": 1500, "qty_pieces": 1, "weight_kg": consumed},
					"offcut": {"length_mm": 2300, "width_mm": 1500, "qty_pieces": 1, "weight_kg": offcut},
				}
			],
			company=self.company,
		)
		remnant = frappe.get_doc("Fabtrk Lot", {"parent_lot": parent, "lot_type": "Offcut"})
		self.assertEqual(remnant.warehouse, warehouse_name("Offcuts"))
		self.assertEqual(flt(remnant.length_mm), 2300)
		self.assertEqual(flt(remnant.width_mm), 1500)
		self.assertEqual(remnant.weight_basis, "Density")
		parent_doc = frappe.get_doc("Fabtrk Lot", parent)
		self.assertTrue(frappe.db.exists("Fabtrk Lot", parent))
		self.assertEqual(flt(parent_doc.qty_pieces), 0)
		self.assertEqual(parent_doc.status, "Consumed")
		self.assertAlmostEqual(consumed + offcut, parent_weight, places=3)

	def test_ac5_over_issue_is_atomic(self):
		self._receipt("INV OVER")
		lot = frappe.db.get_value("Fabtrk Lot", {"source_reference": "INV OVER", "length_mm": 5800}, "name")
		pieces_before = flt(frappe.db.get_value("Fabtrk Lot", lot, "qty_pieces"))
		with self.assertRaises(frappe.ValidationError) as caught:
			post_issue("ISSUE TOO MANY", [{"lot": lot, "qty_pieces": 8, "weight_kg": 5493.33}], company=self.company)
		self.assertIn("6", str(caught.exception))
		self.assertFalse(frappe.db.exists("Stock Entry", {"fabtrk_reference": "ISSUE TOO MANY"}))
		self.assertEqual(flt(frappe.db.get_value("Fabtrk Lot", lot, "qty_pieces")), pieces_before)

	def test_ac6_duplicate_reference_does_not_double(self):
		first = self._receipt("INV DUP")
		bin_before = flt(self._bin())
		second = self._receipt("INV DUP")
		self.assertEqual(second["document_name"], first["document_name"])
		self.assertEqual(second["duplicate"], 1)
		self.assertEqual(flt(self._bin()), bin_before)
		self.assertEqual(frappe.db.count("Stock Entry", {"fabtrk_reference": "INV DUP"}), 1)

	def test_ac7_weight_deviation(self):
		calculated = float(weight_from_density(5800, 1500, 10, 7850, 1))
		with self.assertRaises(frappe.ValidationError) as blocked:
			self._receipt("INV BLOCK", weight_a=calculated * 1.12, pieces_a=1, length_a=5800, skip_second=True)
		self.assertIn("calculated", str(blocked.exception))
		self.assertIn("Weighment", str(blocked.exception))
		self.assertFalse(frappe.db.exists("Stock Entry", {"fabtrk_reference": "INV BLOCK"}))
		warned = self._receipt("INV WARN", weight_a=calculated * 1.06, pieces_a=1, length_a=5800, skip_second=True)
		self.assertTrue(warned["warnings"])
		self.assertTrue(frappe.db.exists("Stock Entry", warned["document_name"]))

	def test_ac11_batch_flag_is_rejected(self):
		item = frappe.get_doc("Item", self.item)
		item.has_batch_no = 1
		with self.assertRaises(frappe.ValidationError) as caught:
			item.save()
		self.assertIn("has_batch_no", str(caught.exception))

	def test_ac12_dry_run_writes_nothing(self):
		before = frappe.db.count("Fabtrk Lot")
		result = post_receipt(
			"INV DRY",
			[
				{
					"item_code": self.item,
					"warehouse": self.warehouse,
					"lots": [
						{
							"length_mm": 5800,
							"width_mm": 1500,
							"qty_pieces": 1,
							"weight_kg": 686.7,
							"weight_basis": "Weighment",
						}
					],
				}
			],
			dry_run=1,
			company=self.company,
		)
		self.assertEqual(result["dry_run"], 1)
		self.assertIsNone(result["document_name"])
		self.assertEqual(result["lines"][0]["qty_pieces"], 1)
		self.assertEqual(frappe.db.count("Fabtrk Lot"), before)
		self.assertFalse(frappe.db.exists("Stock Entry", {"fabtrk_reference": "INV DRY"}))

	def test_permissions(self):
		viewer = self._user("Fabtrk Stock Viewer")
		storekeeper = self._user("Fabtrk Stock Storekeeper")
		frappe.set_user(viewer)
		self.assertTrue(frappe.has_permission("Fabtrk Lot", "read"))
		self.assertFalse(frappe.has_permission("Fabtrk Lot", "write"))
		self.assertFalse(frappe.has_permission("Stock Entry", "create"))
		frappe.set_user(storekeeper)
		self.assertTrue(frappe.has_permission("Stock Entry", "submit"))
		self.assertFalse(frappe.has_permission("Stock Entry", "cancel"))
		self.assertFalse(frappe.has_permission("Item", "write"))
		self.assertFalse(
			frappe.db.get_value(
				"DocPerm",
				{"parent": "Fabtrk Lot", "role": "Fabtrk Stock Storekeeper", "permlevel": 1},
				"read",
			)
		)
		frappe.set_user("Administrator")

	def test_cancel_restores_lot_and_keeps_history(self):
		before = flt(self._bin())
		posted = self._receipt("INV CANCEL", skip_second=True, weight_a=686.7, pieces_a=1, length_a=5800)
		doc = frappe.get_doc("Stock Entry", posted["document_name"])
		doc.cancel()
		lot = frappe.get_doc("Fabtrk Lot", posted["lines"][0]["lot"])
		self.assertEqual(flt(lot.qty_pieces), 0)
		self.assertEqual(lot.status, "Consumed")
		self.assertEqual(frappe.db.count("Fabtrk Lot Movement", {"lot": lot.name}), 2)
		self.assertEqual(flt(self._bin()), before)

	def test_drift_is_zero_after_receipt(self):
		self._receipt("INV DRIFT")
		rows = [row for row in reconcile_rows() if row["item_code"] == self.item and row["warehouse"] == self.warehouse]
		self.assertTrue(rows)
		self.assertAlmostEqual(rows[0]["drift_kg"], 0, places=2)

	def _receipt(self, reference, weight_a=4120, pieces_a=6, length_a=5800, skip_second=False):
		lots = [
			{
				"length_mm": length_a,
				"width_mm": 1500,
				"qty_pieces": pieces_a,
				"weight_kg": weight_a,
				"weight_basis": "Weighment",
			}
		]
		if not skip_second:
			lots.append(
				{
					"length_mm": 8000,
					"width_mm": 1500,
					"qty_pieces": 1,
					"weight_kg": 940,
					"weight_basis": "Weighment",
				}
			)
		return post_receipt(
			reference,
			[{"item_code": self.item, "warehouse": self.warehouse, "lots": lots}],
			company=self.company,
		)

	def _bin(self):
		return frappe.db.get_value("Bin", {"item_code": self.item, "warehouse": self.warehouse}, "actual_qty") or 0

	def _length_for(self, reference):
		total = frappe.db.sql(
			"select sum(length_mm * qty_pieces) from `tabFabtrk Lot` where source_reference=%s",
			reference,
		)[0][0]
		return flt(total)

	def _user(self, role):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": f"{frappe.scrub(role)}-{frappe.generate_hash(length=6)}@example.com",
				"first_name": role,
				"enabled": 1,
				"send_welcome_email": 0,
				"user_type": "System User",
				"roles": [{"role": role}],
			}
		).insert(ignore_permissions=True)
		return user.name
