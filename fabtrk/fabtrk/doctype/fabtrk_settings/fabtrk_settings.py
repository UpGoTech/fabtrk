import frappe
from frappe.model.document import Document


class FabtrkSettings(Document):
	def validate(self):
		previous = self.get_doc_before_save()
		if not previous or previous.allow_negative_stock == self.allow_negative_stock:
			return
		roles = set(frappe.get_roles())
		if frappe.session.user == "Administrator" or "Fabtrk Stock Owner" in roles or "System Manager" in roles:
			return
		frappe.throw("Only Fabtrk Stock Owner can change allow negative stock")
