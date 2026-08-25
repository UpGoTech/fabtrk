import frappe


def calculate_order_value(doc, method=None):
	qty = doc.get("custom_order_qty_kg") or 0
	rate = doc.get("custom_rate_per_kg") or 0
	doc.custom_order_value = float(qty) * float(rate)
