from fabtrk.stock_reports import sku_ledger


def execute(filters=None):
	filters = filters or {}
	if not filters.get("item_code"):
		return [], []
	columns = [
		{"label": "Row", "fieldname": "row_type", "fieldtype": "Data", "width": 100},
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Length (mm)", "fieldname": "length_mm", "fieldtype": "Float", "width": 110},
		{"label": "Width (mm)", "fieldname": "width_mm", "fieldtype": "Float", "width": 110},
		{"label": "Pieces", "fieldname": "qty_pieces", "fieldtype": "Float", "width": 80},
		{"label": "Kg", "fieldname": "weight_kg", "fieldtype": "Float", "width": 100},
		{"label": "MT", "fieldname": "weight_mt", "fieldtype": "Float", "width": 90},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": "Lot", "fieldname": "lot", "fieldtype": "Link", "options": "Fabtrk Lot", "width": 160},
		{"label": "Voucher", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 160},
		{"label": "Reference", "fieldname": "reference", "fieldtype": "Data", "width": 160},
	]
	return columns, sku_ledger(filters.get("item_code"))
