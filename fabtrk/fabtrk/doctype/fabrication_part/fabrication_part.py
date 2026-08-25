import frappe
from frappe import _
from frappe.model.document import Document


class FabricationPart(Document):
	def before_insert(self):
		self.sync_from_drawing()
		if not self.revised_in and self.drawing:
			self.revised_in = frappe.db.get_value("Fabrication Drawing", self.drawing, "current_revision")

	def before_validate(self):
		self.sync_from_drawing()

	def validate(self):
		if not self.drawing:
			frappe.throw(_("Drawing is required"))
		if not self.qty or self.qty <= 0:
			frappe.throw(_("Part qty must be greater than 0"))
		self.clear_unused_dimensions()
		self.validate_unique_piece_mark()
		self.validate_unique_line_no()

	def sync_from_drawing(self):
		if not self.drawing:
			return
		values = frappe.db.get_value("Fabrication Drawing", self.drawing, ["project", "drawing_no"])
		if not values:
			frappe.throw(_("Drawing {0} not found").format(self.drawing))
		self.project, self.drawing_no = values

	def clear_unused_dimensions(self):
		if self.dimension_type == "1D":
			self.width = None
			self.diameter = None
		elif self.dimension_type == "2D":
			self.diameter = None
		elif self.dimension_type == "Disc":
			self.length = None
			self.width = None

	def validate_unique_piece_mark(self):
		filters = {"drawing": self.drawing, "piece_mark": self.piece_mark}
		if not self.is_new():
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Fabrication Part", filters):
			frappe.throw(
				_("Piece mark {0} already exists on drawing {1}").format(self.piece_mark, self.drawing)
			)

	def validate_unique_line_no(self):
		filters = {"drawing": self.drawing, "line_no": self.line_no}
		if not self.is_new():
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Fabrication Part", filters):
			frappe.throw(_("Line No {0} already exists on drawing {1}").format(self.line_no, self.drawing))
