

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
		max-width: 100%;
		min-width: 100%;
		height: 100%;
		display: block;
		place-content: unset;
		margin: 0;
	}
	.summary-container{
		display: grid;
		grid-template-columns: repeat(1, 1fr) !important;
		place-items: center;
		gap: 20px;
	}
	@media (min-width: 768px){
		.summary-container{
			grid-template-columns: repeat(2, 1fr) !important;
		}
	}
	.report-summary .summary-value .summary-container {
		padding: 20px;
	}
	.summary-section{
		width: 90%;
		background: #fff;
		padding: 20px;
		border-radius: 10px;
		text-align: center;
		transition: all 0.2s ease;
		border: 2px solid #eef0f4;
	}
	.section-content-count p{
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
	.report-summary {
		background-color: none;
		border-radius: 0;
		border-bottom: 0;
		margin: 0;
		padding: 0;
		display: block;
		flex-wrap: unset;
		align-items: unset;
		justify-content: unset;
		gap: 0px;
	}
</style>`).appendTo("head");
