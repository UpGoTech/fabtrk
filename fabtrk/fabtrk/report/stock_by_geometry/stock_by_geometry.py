from fabtrk.stock_reports import geometry_rows


def execute(filters=None):
	columns = [
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Grade", "fieldname": "grade", "fieldtype": "Data", "width": 90},
		{"label": "Length (mm)", "fieldname": "length_mm", "fieldtype": "Float", "width": 110},
		{"label": "Width (mm)", "fieldname": "width_mm", "fieldtype": "Float", "width": 110},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": "Pieces", "fieldname": "qty_pieces", "fieldtype": "Float", "width": 80},
		{"label": "Kg", "fieldname": "weight_kg", "fieldtype": "Float", "width": 100},
		{"label": "MT", "fieldname": "weight_mt", "fieldtype": "Float", "width": 90},
		{"label": "Total Length (mm)", "fieldname": "total_length_mm", "fieldtype": "Float", "width": 140},
	]
	return columns, geometry_rows(filters)
