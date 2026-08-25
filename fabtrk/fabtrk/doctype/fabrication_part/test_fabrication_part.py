import frappe
from frappe.tests import IntegrationTestCase

from fabtrk.fabtrk.doctype.fabrication_drawing.test_fabrication_drawing import make_drawing, make_part

IGNORE_TEST_RECORD_DEPENDENCIES = ["Project", "Item", "UOM"]


class TestFabricationPart(IntegrationTestCase):
	def test_unique_piece_mark_and_line_no(self):
		drawing = make_drawing()
		make_part(drawing, "B1", 1)
		self.assertRaises(frappe.ValidationError, make_part, drawing, "B1", 2)
		self.assertRaises(frappe.ValidationError, make_part, drawing, "C-12", 1)

	def test_project_fetched_from_drawing(self):
		drawing = make_drawing()
		part = make_part(drawing, "B1", 1)
		self.assertEqual(part.project, drawing.project)
		self.assertEqual(part.drawing_no, drawing.drawing_no)
		self.assertEqual(part.revised_in, "R0")

	def test_qty_must_be_positive(self):
		drawing = make_drawing()
		doc = frappe.get_doc(
			{
				"doctype": "Fabrication Part",
				"drawing": drawing.name,
				"piece_mark": "B1",
				"line_no": 1,
				"qty": 0,
			}
		)
		self.assertRaises(frappe.ValidationError, doc.insert)
