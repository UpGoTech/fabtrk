from fabtrk.stock_reports import availability_rows


def execute(filters=None):
	columns = [
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Grade", "fieldname": "grade", "fieldtype": "Data", "width": 90},
		{"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
		{"label": "Division", "fieldname": "division", "fieldtype": "Data", "width": 100},
		{"label": "Stock Group", "fieldname": "stock_group", "fieldtype": "Data", "width": 120},
		{"label": "Pieces", "fieldname": "qty_pieces", "fieldtype": "Float", "width": 80},
		{"label": "MT", "fieldname": "weight_mt", "fieldtype": "Float", "width": 90},
	]
	return columns, availability_rows(filters)
