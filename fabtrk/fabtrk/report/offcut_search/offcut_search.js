frappe.query_reports["Offcut Search"] = {
	filters: [
		{fieldname: "min_length_mm", label: "Min Length (mm)", fieldtype: "Float", default: 0},
		{fieldname: "min_width_mm", label: "Min Width (mm)", fieldtype: "Float", default: 0},
		{fieldname: "item_code", label: "Item", fieldtype: "Link", options: "Item"},
		{fieldname: "grade", label: "Grade", fieldtype: "Data"},
		{fieldname: "warehouse", label: "Warehouse", fieldtype: "Link", options: "Warehouse"},
	],
};
