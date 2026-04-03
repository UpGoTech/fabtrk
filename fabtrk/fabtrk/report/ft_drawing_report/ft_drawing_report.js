// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Drawing Report"] = {
	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("is_active", 1);

		// Excel Button
		report.page.add_inner_button("Download Excel", function () {

			let filters = report.get_values();

			let url =
				"/api/method/fabtrk.fabtrk.report.ft_drawing_report.ft_drawing_report.download_drawing_excel"
				+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

			window.location.href = url;

		});

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	after_datatable_render(datatable) {
		render_custom_summary();
	},

	filters: [

		// ---------------- PROJECT ----------------
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let is_active = frappe.query_report.get_filter_value("is_active");

				let filters = {};

				if (is_active) {
					filters.is_active = 1;
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "FT Project",
						filters: filters,
						fields: ["name", "project_name", "description"]
					}
				}).then(r => {

					return (r.message || []).map(d => {
						return {
							value: d.name,
							// label: d.name + (d.project_name ? " - " + d.project_name : ""),
							label: d.name,
							description: d.description || ""
						};
					});

				});
			},

			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.refresh();
				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);
			}
		},

		// ---------------- DRAWING ----------------
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

		// ---------------- ACTIVE ----------------
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check",
			default: 1,

			on_change() {

				frappe.query_report.set_filter_value("project_number", []);
				frappe.query_report.set_filter_value("drawing_number", []);

				frappe.query_report.refresh();
			}
		}

	],

	formatter: function (value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (data && data.project_number === "TOTAL") {

			if (column.id === "_index") {
				value = "";
			}

			value = `<span style="font-weight:bold;background:#f2f2f2">${value}</span>`;
		}

		return value;
	}
};

// ---------------- CUSTOM SUMMARY CARDS ----------------
function render_custom_summary() {

	// Remove old summary if exists
	$(".ft-custom-summary").remove();

	let report_data = frappe.query_report.data || [];

	if (!report_data || report_data.length === 0) return;

	// ---------------- CALCULATIONS ----------------
	let data_rows = report_data.filter(d => d.project_number !== "TOTAL");

	// Total Projects
	let total_projects = new Set(data_rows.map(d => d.project_number).filter(Boolean)).size;

	// Total No of Line Items (rows with po_serial_no)
	let total_lines = data_rows.filter(d => d.po_serial_no).length;

	// Total Unique Drawings
	let total_drawings = new Set(data_rows.map(d => d.drawing_number).filter(Boolean)).size;

	// Total Weight as per Project (sum of all total_weight per project)
	let project_weight_map = {};
	data_rows.forEach(d => {
		if (d.project_number) {
			project_weight_map[d.project_number] = (project_weight_map[d.project_number] || 0) + (d.total_weight || 0);
		}
	});
	let total_weight_per_project = Object.values(project_weight_map).reduce((a, b) => a + b, 0);

	// Total Weight of Line Items Assign to Project (rows with po_serial_no)
	let total_weight_line_items = data_rows
		.filter(d => d.po_serial_no)
		.reduce((sum, d) => sum + (d.total_weight || 0), 0);

	// Drawing Balance for Customer
	let drawing_balance = total_weight_per_project - total_weight_line_items;

	// ---------------- FORMAT NUMBER ----------------
	function fmt(num) {
		return num.toLocaleString("en-IN", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
	}

	// ---------------- CARDS HTML ----------------
	let html = `
	<div class="ft-custom-summary">
		<div class="ft-card">
			<p class="ft-card-label">Total Projects</p>
			<span class="ft-card-value">${total_projects}</span>
			<p class="ft-card-label" style="margin-top:12px;">Total Weight as per Project(Kg)</p>
			<span class="ft-card-value">${fmt(total_weight_per_project)}</span>
		</div>
		<div class="ft-card">
			<p class="ft-card-label">Project Total No of Line Items</p>
			<span class="ft-card-value">${total_lines}</span>
			<p class="ft-card-label" style="margin-top:12px;">Total Weight of Line Items Assign to Project(Kg)</p>
			<span class="ft-card-value">${fmt(total_weight_line_items)}</span>
		</div>
		<div class="ft-card">
			<p class="ft-card-label">Total No of Unique Drawings</p>
			<span class="ft-card-value">${total_drawings}</span>
		</div>
		<div class="ft-card">
			<p class="ft-card-label">Drawing Balance for Customer(Kg)</p>
			<span class="ft-card-value">${fmt(drawing_balance)}</span>
		</div>
	</div>`;

	// Inject above the datatable
	$(".report-wrapper").prepend(html);
}


// ---------------- STYLE ----------------

$(`<style>

.ft-custom-summary {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 20px;
	width: 100%;
	padding: 20px 0px;
}
@media (max-width: 768px) {
    .ft-custom-summary {
        grid-template-columns: repeat(1, 1fr) !important;
    }

    /* Scroll horizontal for table wrapper on small screens */
    .datatable .dt-scrollable {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch; /* smooth scrolling on iOS */
    }
}

.ft-card {
	background: #fff;
	padding: 20px;
	border-radius: 10px;
	text-align: center;
	border: 2px solid #eef0f4;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.ft-card-label {
	font-size: 14px;
	color: #555;
	margin: 0 0 4px 0;
	// text-align: center;
	// width: 100%;
}

.ft-card-value {
	font-size: 16px;
	font-weight: 600;
	color: #000;
	display: block;
	// text-align: center;
	// width: 100%;
}

.datatable .dt-cell__content {
	text-align: center !important;
	justify-content: center !important;
}

.datatable .dt-cell--col-0 .dt-cell__content {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
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
	font-size:16px;
	font-weight:600;
}

</style>`).appendTo("head");

