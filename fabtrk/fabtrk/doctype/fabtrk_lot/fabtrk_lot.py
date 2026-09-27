from decimal import Decimal

import frappe
from frappe.model.document import Document


class FabtrkLot(Document):
	def before_save(self):
		from fabtrk.lots import stock_group_for_warehouse

		self.stock_group = stock_group_for_warehouse(self.warehouse)
		qty = Decimal(str(self.qty_pieces or 0))
		weight = Decimal(str(self.weight_kg or 0))
		self.kg_per_piece = float(weight / qty) if qty else 0
		if self.flags.from_voucher:
			return
		previous = self.get_doc_before_save()
		if previous and (
			float(previous.qty_pieces or 0) != float(self.qty_pieces or 0)
			or float(previous.weight_kg or 0) != float(self.weight_kg or 0)
		):
			frappe.throw("Quantity and weight on a lot change only from a voucher")
		if self.is_new():
			frappe.throw("Lots are created from stock vouchers")
