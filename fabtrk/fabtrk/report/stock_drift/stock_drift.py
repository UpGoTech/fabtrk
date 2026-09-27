from fabtrk.stock_reports import reconcile_rows


def execute(filters=None):
	columns = [
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
		{"label": "Lot kg", "fieldname": "lot_kg", "fieldtype": "Float", "width": 110},
		{"label": "Bin kg", "fieldname": "bin_kg", "fieldtype": "Float", "width": 110},
		{"label": "Drift kg", "fieldname": "drift_kg", "fieldtype": "Float", "width": 110},
	]
	return columns, reconcile_rows()
