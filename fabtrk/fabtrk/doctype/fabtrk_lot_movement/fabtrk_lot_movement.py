import frappe
from frappe.model.document import Document


class FabtrkLotMovement(Document):
	def before_save(self):
		if not self.is_new():
			frappe.throw("Fabtrk Lot Movement cannot be edited")
		if not self.reference:
			frappe.throw("Reference is required")

	def on_trash(self):
		frappe.throw("Fabtrk Lot Movement cannot be deleted")
