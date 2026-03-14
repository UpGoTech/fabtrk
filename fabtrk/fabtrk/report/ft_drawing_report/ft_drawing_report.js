// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Drawing Report"] = {
	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("is_active", 1);

		report.page.add_inner_button("Download Excel", function () {

			let filters = report.get_values();

			let url =
				"/api/method/fabtrk.fabtrk.report.ft_po_drawing_report.ft_po_drawing_report.download_excel"
				+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

			window.location.href = url;

		});

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
				frappe.query_report.refresh();
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
						doctype: "FT Add Drawing",
						filters: filters,
						fields: ["name", "drawing_number"]
					}
				}).then(r => {

					let unique = {};
					let result = [];

					(r.message || []).forEach(d => {

						if (!unique[d.drawing_number]) {

							unique[d.drawing_number] = true;

							result.push({
								value: d.name,
								label: d.drawing_number,
								description: ""
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

	formatter: function (value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (data && data.project_number === "TOTAL") {
			if (column.id === "_index") {
				value = "";   // SR No hide
			}

			value = `<span style="font-weight:bold;background:#f2f2f2">${value}</span>`;

		}

		return value;
	}

};


$(`<style>
.datatable .dt-cell--col-2,
.datatable .dt-cell--col-3,
.datatable .dt-cell--col-4,
.datatable .dt-cell--col-5,
.datatable .dt-cell--col-6 {
    text-align:center !important;
}

.datatable .dt-cell--col-0 .dt-cell__content{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
}

.summary-container{
	display:grid;
	grid-template-columns:repeat(4,1fr);
	gap:20px;
	width:100%;
}

.summary-section{
	background:#fff;
	padding:20px;
	border-radius:10px;
	text-align:center;
	border:2px solid #eef0f4;
}

.section-content-count p{
	font-size:14px;
	color:#555;
}

.section-content-count span{
	font-size:18px;
	font-weight:600;
}

</style>`).appendTo("head");
