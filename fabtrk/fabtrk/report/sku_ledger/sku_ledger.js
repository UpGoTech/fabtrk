frappe.query_reports["SKU Ledger"] = {
	filters: [
		{fieldname: "item_code", label: "Item", fieldtype: "Link", options: "Item", reqd: 1},
	],
};
