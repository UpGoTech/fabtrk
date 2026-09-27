from fabtrk.stock_reports import offcut_rows


def execute(filters=None):
	columns = [
		{"label": "Lot", "fieldname": "lot", "fieldtype": "Link", "options": "Fabtrk Lot", "width": 160},
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Grade", "fieldname": "grade", "fieldtype": "Data", "width": 90},
		{"label": "Length (mm)", "fieldname": "length_mm", "fieldtype": "Float", "width": 110},
		{"label": "Width (mm)", "fieldname": "width_mm", "fieldtype": "Float", "width": 110},
		{"label": "Pieces", "fieldname": "qty_pieces", "fieldtype": "Float", "width": 80},
		{"label": "MT", "fieldname": "weight_mt", "fieldtype": "Float", "width": 90},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
	]
	return columns, offcut_rows(filters)
