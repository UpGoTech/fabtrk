import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt


class FabricationDrawing(Document):
	def validate(self):
		self.validate_qty()
		self.validate_unique_drawing_no()
		self.set_current_revision()

	def validate_qty(self):
		if self.qty is None or flt(self.qty) <= 0:
			frappe.throw(_("Drawing qty must be greater than 0"))
		if flt(self.qty) != cint(self.qty):
			frappe.throw(_("Drawing qty must be a whole number"))
		self.qty = cint(self.qty)

	def validate_unique_drawing_no(self):
		filters = {"project": self.project, "drawing_no": self.drawing_no}
		if not self.is_new():
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Fabrication Drawing", filters):
			frappe.throw(
				_("Drawing No {0} already exists on project {1}").format(self.drawing_no, self.project)
			)

	def set_current_revision(self):
		current = [row for row in self.revisions if row.is_current]
		if len(current) > 1:
			frappe.throw(_("Exactly one drawing revision can be current"))
		if self.revisions and not current:
			frappe.throw(_("Mark one drawing revision as current"))
		self.current_revision = current[0].revision if current else None

	def on_trash(self):
		if frappe.db.exists("Fabrication Part", {"drawing": self.name}):
			frappe.throw(_("Cannot delete a drawing that has parts"))
