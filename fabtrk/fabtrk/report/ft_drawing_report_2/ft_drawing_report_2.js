// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt

// frappe.query_reports["FT Drawing Report 2"] = {

// 	onload(report) {

// 		frappe.query_report.set_filter_value("project_number", "");
// 		frappe.query_report.set_filter_value("drawing_number", "");

// 		setTimeout(() => {
// 			frappe.query_report.refresh();
// 		}, 100);
// 	},

// 	filters: [
// 		{
// 			fieldname: "project_number",
// 			label: "Project Number",
// 			fieldtype: "Link",
// 			options: "FT Project",
// 			on_change() {
// 				frappe.query_report.set_filter_value("drawing_number", "");
// 				setTimeout(() => {
// 					frappe.query_report.refresh();
// 				}, 100);
// 			}
// 		},
// 		{
// 			fieldname: "drawing_number",
// 			label: "Drawing Number",
// 			fieldtype: "Link",
// 			options: "Add Drawing",
// 			get_query() {
// 				return {
// 					filters: {
// 						project_number: frappe.query_report.get_filter_value("project_number")
// 					}
// 				};
// 			}
// 		}
// 	],

// 	after_datatable_render(report) {

// 		// Hide unwanted columns
// 		const unwanted_columns = [
// 			"drawing_part",
// 			"position_number",
// 			"single_weight"
// 		];

// 		unwanted_columns.forEach(field => {
// 			let col = report.datatable.getColumnIndex(field);
// 			if (col !== -1) {
// 				report.datatable.hideColumn(field);
// 			}
// 		});
// 	}
// };








// # this code for multi select filter filed
frappe.query_reports["FT Drawing Report 2"] = {

	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("is_active", 1);

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	filters: [
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Project", txt);
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);
			}
		},
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number");

				let filters = {};

				if (projects && projects.length > 0) {
					filters.project_number = ["in", projects];
				}

				return frappe.db.get_link_options("Add Drawing", txt, filters);
				// return frappe.call({
				// 	method: "frappe.client.get_list",
				// 	args: {
				// 		doctype: "Add Drawing",
				// 		filters: filters,
				// 		fields: ["name", "drawing_number"],
				// 		// limit_page_length: 20
				// 	}
				// }).then(r => {
				// 	return (r.message || []).map(d => {
				// 		return {
				// 			value: d.name,                // 👈 actual ID (backend ke liye)
				// 			description: d.drawing_number // 👈 jo user ko dikhana hai
				// 		};
				// 	});
				// });

			},
			on_change() {
				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);
			}
		},
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check",
			default: 1,
			on_change() {
				frappe.query_report.refresh();
			}
		}
	],

	after_datatable_render(report) {

		const unwanted_columns = [
			"drawing_part",
			"position_number",
			"single_weight"
		];

		unwanted_columns.forEach(field => {
			let col = report.datatable.getColumnIndex(field);
			if (col !== -1) {
				report.datatable.hideColumn(field);
			}
		});
	}
};



