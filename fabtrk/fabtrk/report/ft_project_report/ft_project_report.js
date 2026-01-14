// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Project Report"] = {
	"filters": [
		// {
		// 	fieldname: "project_name",
		// 	label: "Project Name",
		// 	fieldtype: "Link",
		// 	options: "FT Project"
		// },
		{
			fieldname: "project_name",
			label: "Project",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Project", txt);
			}
		}

		,
		{
			fieldname: "status",
			label: "Status",
			fieldtype: "Select",
			options: "\nOrder Received\nMaterial Planning\nWIP\nCompleted\nCancelled"
		},
		{
			fieldname: "project_type",
			label: "Project Type",
			fieldtype: "Link",
			options: "FT Project Type"
		},
		{
			fieldname: "customer",
			label: "Customer",
			fieldtype: "Link",
			options: "FT Customer"
		},
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check"
		},
		{
			fieldname: "from_date",
			label: "Expected Start Date From",
			fieldtype: "Date"
		},
		{
			fieldname: "to_date",
			label: "Expected End Date To",
			fieldtype: "Date"
		}
	]


};





