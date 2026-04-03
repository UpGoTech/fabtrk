// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt


frappe.query_reports["FT Drawings"] = {
	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("po_serial_no", []);
		frappe.query_report.set_filter_value("is_active", 1);

		report.page.add_inner_button("Drawing Excel", function () {

			let filters = report.get_values();

			let url = "/api/method/fabtrk.fabtrk.report.ft_drawings.ft_drawings.download_drawing_excel"
				+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

			window.location.href = url;
		});

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	after_datatable_render(datatable) {
		render_custom_summary_2();

		function hide_total_serial() {
			$(".datatable .dt-body .dt-row").each(function () {
				if ($(this).text().includes("TOTAL")) {
					$(this).find(".dt-cell").first()
						.find(".dt-cell__content")
						.css("visibility", "hidden");
				}
			});
		}

		setTimeout(hide_total_serial, 200);
		setTimeout(hide_total_serial, 500);
		setTimeout(hide_total_serial, 1000);
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
						fields: ["name", "project_name", "description"],
						limit: 0    // ✅ sare projects lao
					}
				}).then(r => {
					let result = (r.message || []).map(d => ({
						value: d.name,
						label: d.name,
						description: d.description || ""
					}));

					if (txt) {
						result = result.filter(item =>
							item.label.toLowerCase().includes(txt.toLowerCase())
						);
					}

					return result;
				});
			},

			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);
			}
		},

		// // ---------------- DRAWING ----------------
		// {
		// 	fieldname: "drawing_number",
		// 	label: "Drawing Number",
		// 	fieldtype: "MultiSelectList",

		// 	get_data: function (txt) {

		// 		let projects = frappe.query_report.get_filter_value("project_number");
		// 		let filters = {};

		// 		if (projects && projects.length > 0) {
		// 			filters.project_number = ["in", projects];
		// 		}

		// 		return frappe.call({
		// 			method: "frappe.client.get_list",
		// 			args: {
		// 				doctype: "FT Add Drawing",
		// 				filters: filters,
		// 				fields: ["drawing_number"],
		// 				limit: 0    // ✅ KEY FIX - sare drawing numbers lao (default 20 tha)
		// 			}
		// 		}).then(r => {
		// 			let unique_map = {};
		// 			let result = [];

		// 			(r.message || []).forEach(d => {
		// 				let val = d.drawing_number;
		// 				if (val && !unique_map[val]) {
		// 					unique_map[val] = true;
		// 					result.push({
		// 						value: val,
		// 						label: val,
		// 						description: ""
		// 					});
		// 				}
		// 			});

		// 			// txt se search filter
		// 			if (txt) {
		// 				result = result.filter(item =>
		// 					item.label.toLowerCase().includes(txt.toLowerCase())
		// 				);
		// 			}

		// 			return result;
		// 		});
		// 	},

		// 	on_change() {
		// 		frappe.query_report.set_filter_value("po_serial_no", []);
		// 		frappe.query_report.refresh();
		// 	}
		// },

		// // ---------------- PO SERIAL NO ----------------
		// {
		// 	fieldname: "po_serial_no",
		// 	label: "PO Serial No",
		// 	fieldtype: "MultiSelectList",

		// 	get_data: function (txt) {

		// 		let projects = frappe.query_report.get_filter_value("project_number");
		// 		let drawings = frappe.query_report.get_filter_value("drawing_number");

		// 		let filters = {};

		// 		if (projects && projects.length > 0) {
		// 			filters.project_number = ["in", projects];
		// 		}

		// 		if (drawings && drawings.length > 0) {
		// 			filters.drawing_number = ["in", drawings];
		// 		}

		// 		return frappe.call({
		// 			method: "frappe.client.get_list",
		// 			args: {
		// 				doctype: "FT Po Drawing",
		// 				filters: filters,
		// 				fields: ["po_serial_no"],
		// 				limit: 0    // ✅ sare po serial numbers lao
		// 			}
		// 		}).then(r => {
		// 			let unique_map = {};
		// 			let result = [];

		// 			(r.message || []).forEach(d => {
		// 				let val = d.po_serial_no;
		// 				if (val && !unique_map[val]) {
		// 					unique_map[val] = true;
		// 					result.push({
		// 						value: val,
		// 						label: val,
		// 						description: ""
		// 					});
		// 				}
		// 			});

		// 			// txt se search filter
		// 			if (txt) {
		// 				result = result.filter(item =>
		// 					item.label.toLowerCase().includes(txt.toLowerCase())
		// 				);
		// 			}

		// 			// Numeric sort
		// 			result.sort((a, b) => {
		// 				let na = parseInt(a.value), nb = parseInt(b.value);
		// 				if (!isNaN(na) && !isNaN(nb)) return na - nb;
		// 				return a.value.localeCompare(b.value);
		// 			});

		// 			return result;
		// 		});
		// 	},

		// 	on_change() {
		// 		frappe.query_report.refresh();
		// 	}
		// },

		// ---------------- DRAWING ----------------
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {
				let projects = frappe.query_report.get_filter_value("project_number");

				return frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawings.ft_drawings.get_drawing_numbers",
					args: {
						project_number: JSON.stringify(projects || []),
						txt: txt || ""
					}
				}).then(r => r.message || []);
			},

			on_change() {
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
			}
		},

		// ---------------- PO SERIAL NO ----------------
		{
			fieldname: "po_serial_no",
			label: "PO Serial No",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {
				let projects = frappe.query_report.get_filter_value("project_number");
				let drawings = frappe.query_report.get_filter_value("drawing_number");

				return frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawings.ft_drawings.get_po_serial_numbers",
					args: {
						project_number: JSON.stringify(projects || []),
						drawing_number: JSON.stringify(drawings || []),
						txt: txt || ""
					}
				}).then(r => r.message || []);
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
				frappe.query_report.set_filter_value("po_serial_no", []);
				frappe.query_report.refresh();
			}
		}
	],

	formatter: function (value, row, column, data, default_formatter) {

		if (data && data.project_name === "TOTAL") {
			if (column.id === "_index") {
				// ✅ Empty span with visibility hidden
				return `<span style="visibility:hidden;">0</span>`;
			}
			value = default_formatter(value, row, column, data);
			return `<span style="font-weight:bold;background:#f2f2f2">${value}</span>`;
		}

		return default_formatter(value, row, column, data);
	}
};

// // ---------------- CUSTOM SUMMARY CARDS ----------------
function render_custom_summary_2() {

	$(".ft-custom-summary-2").remove();

	let report_data = frappe.query_report.data || [];
	if (!report_data || report_data.length === 0) return;

	let data_rows = report_data.filter(d => d.project_name !== "TOTAL");

	// TOTAL row se project_total_weight lo
	let total_row = report_data.find(d => d.project_name === "TOTAL");
	let total_weight_per_project = total_row ? (total_row.project_total_weight || 0) : 0;

	// Total Projects
	let total_projects = new Set(data_rows.map(d => d.project_name).filter(Boolean)).size;

	// Total No of Line Items (rows with po_serial_no)
	let total_lines = data_rows.filter(d => d.po_serial_no).length;

	// Total Unique Drawings
	let total_drawings = new Set(data_rows.map(d => d.drawing_id).filter(Boolean)).size;

	// Total Weight of Line Items (rows with po_serial_no)
	let total_weight_line_items = data_rows
		.filter(d => d.po_serial_no)
		.reduce((sum, d) => sum + (d.total_weight || 0), 0);

	// Drawing Balance for Customer
	let drawing_balance = total_weight_per_project - total_weight_line_items;

	function fmt(num) {
		return num.toLocaleString("en-IN", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
	}

	let html = `
	<div class="ft-custom-summary-2">
		<div class="ft-card-2">
			<p class="ft-card-label-2">Total Projects</p>
			<span class="ft-card-value-2">${total_projects}</span>
			<p class="ft-card-label-2" style="margin-top:12px;">Total Weight as per Project(Kg)</p>
			<span class="ft-card-value-2">${fmt(total_weight_per_project)}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Project Total No of Line Items</p>
			<span class="ft-card-value-2">${total_lines}</span>
			<p class="ft-card-label-2" style="margin-top:12px;">Total Weight of Line Items Assign to Project(Kg)</p>
			<span class="ft-card-value-2">${fmt(total_weight_line_items)}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Total No of Unique Drawings</p>
			<span class="ft-card-value-2">${total_drawings}</span>
		</div>
		<div class="ft-card-2">
			<p class="ft-card-label-2">Drawing Balance for Customer(Kg)</p>
			<span class="ft-card-value-2">${fmt(drawing_balance)}</span>
		</div>
	</div>`;

	$(".report-wrapper").prepend(html);
}


// ---------------- STYLE ----------------
$(`<style>

/*   -------------------CARD*/
.ft-custom-summary-2 {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 20px;
	width: 100%;
	padding: 20px 0px;
}

@media (max-width: 768px) {
	.ft-custom-summary-2 {
		grid-template-columns: repeat(1, 1fr) !important;
	}
	.datatable .dt-scrollable {
		overflow-x: auto !important;
		-webkit-overflow-scrolling: touch;
	}
}

.ft-card-2 {
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

.ft-card-label-2 {
	font-size: 14px;
	color: #555;
	margin: 0 0 4px 0;
	text-align: center;
	width: 100%;
}

.ft-card-value-2 {
	font-size: 16px;
	font-weight: 600;
	color: #000;
	display: block;
	text-align: center;
	width: 100%;
}
/*   -------------------CARD*/

.report-wrapper,
.datatable,
.datatable-container {
	width: 100% !important;
}


.datatable table {
	width: 100% !important;
	table-layout: auto !important;
}

.datatable .dt-cell {
	white-space: nowrap !important;
}

.datatable .dt-cell__content {
	text-align: center !important;
	justify-content: center !important;
	overflow: visible !important;
	text-overflow: unset !important;
}


.datatable .dt-row {
	width: 100% !important;
}


/* ✅ TOTAL row — serial number hide karo permanently */
.datatable .dt-body .dt-row:last-child .dt-cell:first-child .dt-cell__content {
    visibility: hidden !important;
    pointer-events: none !important;
}
</style>`).appendTo("head");

