import frappe
from frappe.tests import IntegrationTestCase

IGNORE_TEST_RECORD_DEPENDENCIES = ["Project"]


def _company():
	return frappe.db.get_single_value("Global Defaults", "default_company") or frappe.get_all(
		"Company", pluck="name", limit=1
	)[0]


def make_project():
	return frappe.get_doc(
		{
			"doctype": "Project",
			"project_name": f"_Test Fab {frappe.generate_hash(length=6)}",
			"status": "Open",
			"company": _company(),
		}
	).insert()


def make_drawing(project=None, drawing_no="101", revision="R0"):
	project = project or make_project()
	drawing = frappe.get_doc(
		{
			"doctype": "Fabrication Drawing",
			"project": project.name,
			"drawing_no": drawing_no,
			"description": "Test drawing",
			"qty": 10,
			"status": "Issued",
			"revisions": [{"revision": revision, "is_current": 1}],
		}
	).insert()
	return drawing


def make_part(drawing, piece_mark="B1", line_no=1, **kwargs):
	doc = frappe.get_doc(
		{
			"doctype": "Fabrication Part",
			"drawing": drawing.name,
			"piece_mark": piece_mark,
			"line_no": line_no,
			"source": kwargs.get("source", "Fabricate"),
			"qty": kwargs.get("qty", 1),
			"dimension_type": kwargs.get("dimension_type", "1D"),
		}
	)
	doc.insert()
	return doc


class TestFabricationDrawing(IntegrationTestCase):
	def test_unique_drawing_no_per_project(self):
		project = make_project()
		make_drawing(project, "101")
		duplicate = frappe.get_doc(
			{
				"doctype": "Fabrication Drawing",
				"project": project.name,
				"drawing_no": "101",
				"qty": 1,
			}
		)
		self.assertRaises(frappe.ValidationError, duplicate.insert)

	def test_current_revision_exactly_one(self):
		project = make_project()
		drawing = frappe.get_doc(
			{
				"doctype": "Fabrication Drawing",
				"project": project.name,
				"drawing_no": "200",
				"qty": 1,
				"revisions": [
					{"revision": "R0", "is_current": 1},
					{"revision": "R1", "is_current": 1},
				],
			}
		)
		self.assertRaises(frappe.ValidationError, drawing.insert)

		drawing = frappe.get_doc(
			{
				"doctype": "Fabrication Drawing",
				"project": project.name,
				"drawing_no": "201",
				"qty": 1,
				"revisions": [{"revision": "R0", "is_current": 0}],
			}
		)
		self.assertRaises(frappe.ValidationError, drawing.insert)

		drawing = make_drawing(project, "202", "R0")
		self.assertEqual(drawing.current_revision, "R0")

	def test_new_revision_does_not_change_parts(self):
		drawing = make_drawing()
		part = make_part(drawing, "B1", 1)
		self.assertEqual(part.revised_in, "R0")
		self.assertEqual(part.on_hold, 0)

		drawing.append("revisions", {"revision": "R1", "is_current": 1})
		drawing.revisions[0].is_current = 0
		drawing.save()

		part.reload()
		self.assertEqual(part.revised_in, "R0")
		self.assertEqual(part.on_hold, 0)
		self.assertEqual(len(part.history), 0)

	def test_cannot_delete_drawing_with_parts(self):
		drawing = make_drawing()
		make_part(drawing, "B1", 1)
		self.assertRaises(frappe.ValidationError, drawing.delete)

	def test_qty_must_be_positive_whole_number(self):
		project = make_project()
		for qty in (0, -1, 1.5):
			doc = frappe.get_doc(
				{
					"doctype": "Fabrication Drawing",
					"project": project.name,
					"drawing_no": f"Q{qty}",
					"qty": qty,
				}
			)
			self.assertRaises(frappe.ValidationError, doc.insert)

		drawing = make_drawing(project, "Q10")
		self.assertEqual(drawing.qty, 10)

	def test_description_and_system_tags(self):
		drawing = make_drawing()
		self.assertEqual(drawing.description, "Test drawing")
		self.assertFalse(frappe.db.exists("DocType", "Fabrication Tag"))
		self.assertFalse(frappe.db.exists("DocType", "Fabrication Drawing Tag"))
		drawing.add_tag("Phase 1")
		self.assertTrue(
			frappe.db.exists(
				"Tag Link",
				{
					"document_type": "Fabrication Drawing",
					"document_name": drawing.name,
					"tag": "Phase 1",
				},
			)
		)

	def test_drawing_register_path(self):
		project = make_project()
		drawing = frappe.get_doc(
			{
				"doctype": "Fabrication Drawing",
				"project": project.name,
				"drawing_no": "101",
				"description": "Base plate GA",
				"qty": 10,
				"status": "Issued",
				"priority": "High",
				"po_weight": 1250.5,
				"revisions": [{"revision": "R0", "is_current": 1}],
			}
		).insert()
		self.assertEqual(drawing.qty, 10)
		self.assertEqual(drawing.description, "Base plate GA")
		self.assertEqual(drawing.po_weight, 1250.5)
		drawing.add_tag("Phase 1")
		self.assertTrue(
			frappe.db.exists(
				"Tag Link",
				{
					"document_type": "Fabrication Drawing",
					"document_name": drawing.name,
					"tag": "Phase 1",
				},
			)
		)

		make_part(drawing, "B1", 1, dimension_type="1D")
		make_part(drawing, "C-12", 2, source="Bought Out")
		make_part(drawing, "PL1", 3, dimension_type="2D")
		make_part(drawing, "DC1", 4, dimension_type="Disc")
		self.assertEqual(frappe.db.count("Fabrication Part", {"drawing": drawing.name}), 4)
