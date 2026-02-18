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

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Add Drawing",
						filters: filters,
						fields: ["name", "drawing_number"],
						// limit_page_length: 500
					}
				}).then(r => {

					let unique_map = {};
					let result = [];

					(r.message || []).forEach(d => {
						if (!unique_map[d.drawing_number]) {
							unique_map[d.drawing_number] = true;

							result.push({
								value: d.drawing_number,
								label: d.drawing_number,       // sirf value show karega
								description: ""                // undefined hatane ke liye
							});
						}
					});

					return result;
				});
			},
			on_change() {
				frappe.query_report.refresh();
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



$(`<style>
	.report-summary .summary-item{
		max-width: 100% !important;
		min-width: 100% !important;
		height: 200px !important;
	}
	.summary-container{
		display: grid;
		grid-template-columns: repeat(2, 1fr) !important;
		grid-gap: 60px;
	}
	.report-summary .summary-value .summary-container {
		padding: 25px;
	}
	.summary-section{
		background: #fff;
		padding: 25px;
		border-radius: 10px;
		text-align: center;
		transition: all 0.2s ease;
		border: 2px solid #eef0f4;
	}
	.section-content-count{
		margin-bottom: 10px;
	}
	.section-content-count h3{
		font-size: 14px;
		font-weight: 400;
		color: #525252;
	}
	.section-content-count span{
		font-size: 16px;
		font-weight: 600;
		line-height: 20px;
		padding-top: 12px;
		padding-bottom: 5px;
		color: #000;
	}
	/* REMOVE DEFAULT FRAPPE OVERFLOW CUT */
	.report-summary .summary-value,
	.report-summary .summary-value div {
		overflow: visible !important;
	}
	.report-summary{
		display: grid;
		justify-content: start;
	}
</style>`).appendTo("head");