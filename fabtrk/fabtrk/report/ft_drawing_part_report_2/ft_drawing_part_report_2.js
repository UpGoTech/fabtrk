frappe.query_reports["FT Drawing Part Report 2"] = {

	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("item", []);
		frappe.query_report.set_filter_value("is_active", 1);

		// Add Buttons
		report.page.add_inner_button("Download Drawing Parts", function () {
			download_csv(report);
		});

		report.page.add_inner_button("Download Full Report", function () {
			download_full_report(report);
		});

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	filters: [

		// ---------------- PROJECT ----------------
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Project", txt);
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("item", []);
				frappe.query_report.refresh();

				clear_item_details();
			}
		},

		// ---------------- DRAWING ----------------
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let filters = [];

				// Search filter (IMPORTANT)
				if (txt) {
					filters.push(["drawing_number", "like", "%" + txt + "%"]);
				}

				if (projects.length) {
					filters.push(["project_number", "in", projects]);
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "FT Add Drawing",
						fields: ["name", "drawing_number"],
						filters: filters,
					}
				}).then(r => {

					let unique = {};
					let result = [];

					(r.message || []).forEach(d => {
						if (d.drawing_number && !unique[d.drawing_number]) {
							unique[d.drawing_number] = true;

							result.push({
								value: d.drawing_number,
								label: d.drawing_number,
								description: ""
							});
						}
					});

					return result;
				});
			},

			on_change() {
				frappe.query_report.set_filter_value("item", []);
				frappe.query_report.refresh();

				clear_item_details();
			}
		},



		// ---------------- ITEM ----------------
		// {
		// 	fieldname: "item",
		// 	label: "Drawing Part",
		// 	fieldtype: "MultiSelectList",

		// 	get_data: function (txt) {

		// 		let projects = frappe.query_report.get_filter_value("project_number") || [];
		// 		let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

		// 		// ---------------- CASE 1 ----------------
		// 		// Nothing selected → show all items
		// 		if (!projects.length && !drawings.length) {

		// 			return frappe.call({
		// 				method: "frappe.client.get_list",
		// 				args: {
		// 					doctype: "FT Stock RM List",
		// 					fields: ["name", "computed_name"],
		// 					filters: [["computed_name", "like", "%" + txt + "%"]]
		// 				}
		// 			}).then(r => {
		// 				return (r.message || []).map(d => ({
		// 					value: d.name,
		// 					label: d.computed_name,
		// 					description: ""
		// 				}));
		// 			});
		// 		}

		// 		// ---------------- CASE 2 ----------------
		// 		// Project selected but no drawing
		// 		if (projects.length && !drawings.length) {

		// 			return frappe.call({
		// 				method: "frappe.client.get_list",
		// 				args: {
		// 					doctype: "FT Drawing Parts",
		// 					fields: ["item"],
		// 					filters: [["project_number", "in", projects]]
		// 				}
		// 			}).then(r => {

		// 				let unique_items = [...new Set((r.message || []).map(d => d.item))];
		// 				if (!unique_items.length) return [];

		// 				return frappe.call({
		// 					method: "frappe.client.get_list",
		// 					args: {
		// 						doctype: "FT Stock RM List",
		// 						fields: ["name", "computed_name"],
		// 						filters: [
		// 							["name", "in", unique_items],
		// 							["computed_name", "like", "%" + txt + "%"]
		// 						]
		// 					}
		// 				}).then(res => {
		// 					return (res.message || []).map(d => ({
		// 						value: d.name,
		// 						label: d.computed_name,
		// 						description: ""
		// 					}));
		// 				});

		// 			});
		// 		}

		// 		// ---------------- CASE 3 ----------------
		// 		// Drawing selected → PROPER FIX
		// 		if (drawings.length) {

		// 			// Step 1: Get FT Add Drawing document names
		// 			return frappe.call({
		// 				method: "frappe.client.get_list",
		// 				args: {
		// 					doctype: "FT Add Drawing",
		// 					fields: ["name"],
		// 					filters: [
		// 						["drawing_number", "in", drawings]
		// 					]
		// 				}
		// 			}).then(res => {

		// 				let drawing_names = (res.message || []).map(d => d.name);
		// 				if (!drawing_names.length) return [];

		// 				// Step 2: Get items from FT Drawing Parts
		// 				return frappe.call({
		// 					method: "frappe.client.get_list",
		// 					args: {
		// 						doctype: "FT Drawing Parts",
		// 						fields: ["item"],
		// 						filters: [
		// 							["drawing_number", "in", drawing_names]
		// 						]
		// 					}
		// 				}).then(r => {

		// 					let unique_items = [...new Set((r.message || []).map(d => d.item))];
		// 					if (!unique_items.length) return [];

		// 					return frappe.call({
		// 						method: "frappe.client.get_list",
		// 						args: {
		// 							doctype: "FT Stock RM List",
		// 							fields: ["name", "computed_name"],
		// 							filters: [
		// 								["name", "in", unique_items],
		// 								["computed_name", "like", "%" + txt + "%"]
		// 							]
		// 						}
		// 					}).then(res2 => {
		// 						return (res2.message || []).map(d => ({
		// 							value: d.name,
		// 							label: d.computed_name,
		// 							description: ""
		// 						}));
		// 					});

		// 				});

		// 			});
		// 		}
		// 	}
		// },


		// ---------------- ITEM ----------------
		{
			fieldname: "item",
			label: "Drawing Parts",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];
				let stock_types = frappe.query_report.get_filter_value("stock_rm_type") || [];

				// ---------------- CASE 1 ----------------
				// Nothing selected → show all items
				if (!projects.length && !drawings.length) {

					let filters = [["computed_name", "like", "%" + txt + "%"]];

					if (stock_types.length) {
						filters.push(["stock_rm_type", "in", stock_types]);
					}

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Stock RM List",
							fields: ["name", "computed_name"],
							filters: filters
						}
					}).then(r => {
						return (r.message || []).map(d => ({
							value: d.name,
							label: d.computed_name,
							description: ""
						}));
					});
				}

				// ---------------- CASE 2 ----------------
				// Project selected but no drawing
				if (projects.length && !drawings.length) {

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Drawing Parts",
							fields: ["item"],
							filters: [["project_number", "in", projects]]
						}
					}).then(r => {

						let unique_items = [...new Set((r.message || []).map(d => d.item))];
						if (!unique_items.length) return [];

						let filters = [
							["name", "in", unique_items],
							["computed_name", "like", "%" + txt + "%"]
						];

						if (stock_types.length) {
							filters.push(["stock_rm_type", "in", stock_types]);
						}

						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Stock RM List",
								fields: ["name", "computed_name"],
								filters: filters
							}
						}).then(res => {
							return (res.message || []).map(d => ({
								value: d.name,
								label: d.computed_name,
								description: ""
							}));
						});

					});
				}

				// ---------------- CASE 3 ----------------
				// Drawing selected
				if (drawings.length) {

					// Step 1: Get FT Add Drawing document names
					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Add Drawing",
							fields: ["name"],
							filters: [
								["drawing_number", "in", drawings]
							]
						}
					}).then(res => {

						let drawing_names = (res.message || []).map(d => d.name);
						if (!drawing_names.length) return [];

						// Step 2: Get items from FT Drawing Parts
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Drawing Parts",
								fields: ["item"],
								filters: [
									["drawing_number", "in", drawing_names]
								]
							}
						}).then(r => {

							let unique_items = [...new Set((r.message || []).map(d => d.item))];
							if (!unique_items.length) return [];

							let filters = [
								["name", "in", unique_items],
								["computed_name", "like", "%" + txt + "%"]
							];

							if (stock_types.length) {
								filters.push(["stock_rm_type", "in", stock_types]);
							}

							return frappe.call({
								method: "frappe.client.get_list",
								args: {
									doctype: "FT Stock RM List",
									fields: ["name", "computed_name"],
									filters: filters
								}
							}).then(res2 => {
								return (res2.message || []).map(d => ({
									value: d.name,
									label: d.computed_name,
									description: ""
								}));
							});

						});

					});
				}
			},

			on_change() {
				clear_item_details();   // 👈 ADD THIS
				frappe.query_report.refresh();
			}
		},

		// ----------------- Section Type 
		{
			fieldname: "stock_rm_type",
			label: "Section Type",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Section Type", txt);
			},
			on_change() {
				frappe.query_report.refresh();
				clear_item_details();
			}
		},

		// ---------------- IS ACTIVE ----------------
		{
			fieldname: "is_active",
			label: "Is Active",
			fieldtype: "Check",
			default: 1,
			on_change() {
				frappe.query_report.refresh();
				clear_item_details();
			}
		}

	],

	after_datatable_render(report) {

		$(report.wrapper)
			.off("click", ".view-btn")
			.on("click", ".view-btn", function () {

				// Remove active from all buttons
				$(".view-btn").removeClass("active-detail");

				// Add active to clicked button
				$(this).addClass("active-detail");


				let project = $(this).data("project");
				let item = $(this).data("item");

				// ✅ GET SELECTED DRAWING
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

				// // If only 1 drawing selected → pass it
				// let drawing_number = drawings.length === 1 ? drawings[0] : null;

				if (!project || !item) {
					frappe.msgprint("No Data");
					return;
				}

				frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_item_details",
					args: {
						project: project,
						item: item,
						// drawing_number: drawing_number  
						drawing_numbers: drawings.length ? JSON.stringify(drawings) : null
					},
					callback: function (r) {

						if (!r.message || !r.message.data || !r.message.data.length) {

							frappe.msgprint("No Details Found");
							return;
						}

						$("#item-detail-container").remove();

						let rows = "";
						let totalWeight = 0;

						r.message.data.forEach(d => {
							// Skip backend Total row from calculation
							let is_total_row = String(d.drawing_number).toLowerCase().includes("total");

							// Qty / Length / Width → 2 digit format
							let qty = d.quantity !== undefined && d.quantity !== "" ? String(d.quantity).padStart(2, '0') : "";
							let length = d.lenght !== undefined && d.lenght !== "" ? String(d.lenght).padStart(2, '0') : "";
							let width = d.width !== undefined && d.width !== "" ? String(d.width).padStart(2, '0') : "";

							// Weight → 3 decimal format
							let single_weight = d.single_weight !== undefined && d.single_weight !== "" ? parseFloat(d.single_weight).toFixed(3) : "";
							let total_weight = d.total_weight !== undefined && d.total_weight !== "" ? parseFloat(String(d.total_weight).replace(/<[^>]+>/g, '')).toFixed(3) : "";

							let row_style = "";
							let total_weight_style = "text-align:center;";

							if (is_total_row) {
								row_style = "background-color:#f8f9fa; font-weight:600;";
								total_weight_style = "text-align:center; color:#000; font-weight:700; font-size:15px;";
							}

							rows += `
								<tr style="${row_style}">
									<td>${d.drawing_number}</td>
									<td style="text-align:center;">${d.position_no || ""}</td>
									<td style="text-align:center;">${qty}</td>
									<td style="text-align:center;">${length}</td>
									<td style="text-align:center;">${width}</td>
									<td style="text-align:center;">${single_weight}</td>
									<td style="${total_weight_style}">${total_weight}</td>
								</tr>
							`;

							// Total calculation (skip backend total row)
							if (!is_total_row) {
								totalWeight += parseFloat(
									String(d.total_weight).replace(/<[^>]+>/g, '')
								) || 0;
							}
						});


						let html = `
							<div id="item-detail-container"
								style="margin-top:20px; padding:20px; border:1px solid #ddd;">

								<div style="display:flex;justify-content:space-between;align-items:center;">
									<h4>Item Details - ${r.message.item_name}</h4>
									<div style="display:flex; gap:20px;">
										<button class="btn btn-xs btn-primary summary-download">
											Download List
										</button>
										<button class="btn btn-xs btn-danger close-view">
											Close
										</button>
									</div>
								</div>

								<table class="table table-bordered" style="margin-top:15px;">
									<tr>
										<th >Drawing</th>
										<th style="text-align: center;">Position No</th>
										<th style="text-align: center;">Qty</th>
										<th style="text-align: center;">Length</th>
										<th style="text-align: center;">Width</th>
										<th style="text-align: center;">Single Weight</th>
										<th style="text-align: center;">Total Weight</th>
									</tr>
									${rows}
								</table>
							</div>
						`;

						$(report.wrapper).find(".datatable").after(html);

						$(".close-view").on("click", function () {
							$("#item-detail-container").remove();
							$(".view-btn").removeClass("active-detail");
						});
						// only summary table download
						$(".summary-download").on("click", function () {

							let rows = [];

							// Get Title
							let title = $("#item-detail-container h4").text().trim();
							title = title.replace(/"/g, '""');

							// Add title as first row
							// rows.push(""); // blank line before title
							rows.push(`"${title}"`);
							// rows.push(""); // blank line after title

							// Now extract table
							$("#item-detail-container table tr").each(function () {

								let cols = [];

								$(this).find("th, td").each(function () {
									let text = $(this).text().trim();
									text = text.replace(/"/g, '""');
									cols.push(`"${text}"`);
								});

								rows.push(cols.join(","));
							});

							if (!rows.length) {
								frappe.msgprint("No data to export");
								return;
							}

							let csv_content = rows.join("\n");

							let blob = new Blob([csv_content], { type: "text/csv;charset=utf-8;" });
							let url = URL.createObjectURL(blob);

							let link = document.createElement("a");
							link.href = url;

							// Clean filename (replace spaces & special chars)
							let clean_name = title.replace(/[^a-z0-9]/gi, "_").toLowerCase();

							link.download = `${clean_name}.csv`;

							document.body.appendChild(link);
							link.click();
							document.body.removeChild(link);
						});
					}
				});
			});
	}
};

// table refresh
function clear_item_details() {
	$("#item-detail-container").remove();
	$(".view-btn").removeClass("active-detail");
}

function download_csv(report) {

	if (!report.data || !report.data.length) {
		frappe.msgprint("No data to export");
		return;
	}

	let columns = report.columns
		.filter(col => col.fieldname !== "view") // remove View button column
		.map(col => `"${col.label}"`);

	let rows = report.data.map(row => {
		return report.columns
			.filter(col => col.fieldname !== "view")
			.map(col => {
				let value = row[col.fieldname] ?? "";
				value = String(value).replace(/"/g, '""'); // escape quotes
				return `"${value}"`;
			}).join(",");
	});

	let csv_content = columns.join(",") + "\n" + rows.join("\n");

	let blob = new Blob([csv_content], { type: "text/csv;charset=utf-8;" });
	let url = URL.createObjectURL(blob);

	let link = document.createElement("a");
	link.href = url;
	link.download = "FT_Drawing_Part_Report.csv";
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}
// download both summary and detail tables in Excel with two defferent sheet for detail and summary
function download_full_report(report) {

	if (!report.data || !report.data.length) {
		frappe.msgprint("No data to export");
		return;
	}

	if (!window.XLSX) {
		frappe.msgprint("Excel library loading... try again");
		return;
	}

	// -----------------------
	// SHEET 1 → SUMMARY TABLE
	// -----------------------

	let summary_data = [];

	let valid_columns = report.columns.filter(col =>
		col.fieldname && col.fieldname !== "view"
	);

	// Header row
	summary_data.push(valid_columns.map(col => col.label));

	// Data rows
	report.data.forEach(row => {
		summary_data.push(
			valid_columns.map(col => row[col.fieldname] ?? "")
		);
	});

	let summary_ws = XLSX.utils.aoa_to_sheet(summary_data);


	// -----------------------
	// SHEET 2 → ALL DETAILS
	// -----------------------

	let detail_data = [];
	detail_data.push([
		"Project",
		"Item",
		"Drawing",
		"Qty",
		"Length",
		"Width",
		"Single Weight",
		"Total Weight"
	]);

	let filters = frappe.query_report.get_filter_values();

	frappe.call({
		method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_all_details_for_export",
		args: {
			filters: filters
		},
		async: false,
		callback: function (r) {

			(r.message || []).forEach(d => {
				detail_data.push([
					d.project,
					d.item_name,
					d.drawing_number,
					d.quantity,
					d.lenght,
					d.width,
					d.single_weight,
					d.total_weight
				]);
			});
		}
	});

	let detail_ws = XLSX.utils.aoa_to_sheet(detail_data);

	// -----------------------
	// CREATE WORKBOOK
	// -----------------------

	let wb = XLSX.utils.book_new();
	XLSX.utils.book_append_sheet(wb, summary_ws, "Summary");
	XLSX.utils.book_append_sheet(wb, detail_ws, "Details");

	XLSX.writeFile(wb, "FT_Drawing_Part_Report.xlsx");
}
if (!window.XLSX) {
	let script = document.createElement("script");
	script.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
	document.head.appendChild(script);
}

$(`<style>
	.datatable {
    width: 100% !important;
}

.datatable .dt-scrollable {
    overflow-x: auto !important;
}

.datatable-wrapper {
    width: 100% !important;
}

.report-wrapper {
    max-width: 100% !important;
}
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
		// place-items: center;
		gap: 20px;
	}
	@media (min-width: 768px) and (max-width: 1023px) {
		.summary-container{
			grid-template-columns: repeat(2, 1fr) !important;
		}
	}
	@media (min-width: 1024px) {
		.summary-container{
			grid-template-columns: repeat(5, 1fr) !important;
		}
	}
	.report-summary .summary-value .summary-container {
		padding: 20px;
	}
	.summary-section{
		width: 100%;
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
	.table{
		width: 100% !important;
	}
	/* button view active color*/
	.view-btn.active-detail {
		background-color: #0c5c70 !important;
		color: #fff !important;
		border-color: #0c5c70  !important;
		box-shadow: 0 0 0 2px rgba(21, 54, 102, 0.25);
	}
</style>`).appendTo("head");

