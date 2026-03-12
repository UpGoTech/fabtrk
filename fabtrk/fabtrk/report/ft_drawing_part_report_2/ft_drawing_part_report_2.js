
// frappe.query_reports["FT Drawing Part Report 2"] = {

// 	onload(report) {
// 		frappe.query_report.set_filter_value("project_number", []);
// 		frappe.query_report.set_filter_value("drawing_number", []);
// 		frappe.query_report.set_filter_value("item", []);
// 		frappe.query_report.set_filter_value("is_active", 1);

// 		// Add download item details button to summary table
// 		report.page.add_inner_button("Download Item Excel", function () {
// 			let filters = report.get_values();

// 			let params = new URLSearchParams({
// 				filters: JSON.stringify(filters)
// 			});

// 			// ✅ window.location.href — sabse reliable Frappe binary download ke liye
// 			window.location.href = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_excel?" + params.toString();
// 		});

// 		// Add download full report button to both summary and detail tables in Excel with two different sheets for detail and summary
// 		report.page.add_inner_button("Download Full Report", function () {

// 			frappe.call({
// 				method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_all_details_for_export",
// 				args: { filters: report.get_values() },
// 				callback: function (r) {
// 					if (r.message) {
// 						const link = document.createElement("a");
// 						link.href = r.message;
// 						link.download = "FT_Drawing_Part_Report.xlsx";
// 						document.body.appendChild(link);
// 						link.click();
// 						document.body.removeChild(link);
// 					}
// 				}
// 			});

// 		});

// 		setTimeout(() => {
// 			frappe.query_report.refresh();
// 		}, 100);
// 	},

// 	filters: [

// 		// ---------------- PROJECT ----------------
// 		{
// 			fieldname: "project_number",
// 			label: "Project Number",
// 			fieldtype: "MultiSelectList",
// 			get_data: function (txt) {
// 				return frappe.db.get_link_options("FT Project", txt);
// 			},
// 			on_change() {
// 				frappe.query_report.set_filter_value("drawing_number", []);
// 				frappe.query_report.set_filter_value("item", []);
// 				frappe.query_report.refresh();

// 				clear_item_details();
// 			}
// 		},

// 		{
// 			fieldname: "drawing_number",
// 			label: "Drawing Number",
// 			fieldtype: "MultiSelectList",

// 			get_data: function (txt) {

// 				let projects = frappe.query_report.get_filter_value("project_number") || [];
// 				let filters = [];

// 				if (txt) {
// 					filters.push(["name", "like", "%" + txt + "%"]);
// 				}

// 				if (projects.length) {
// 					filters.push(["project_number", "in", projects]);
// 				}

// 				return frappe.call({
// 					method: "frappe.client.get_list",
// 					args: {
// 						doctype: "FT Add Drawing",
// 						fields: ["name"],
// 						filters: filters,
// 					}
// 				}).then(r => {

// 					let result = (r.message || []).map(d => ({
// 						value: d.name,
// 						label: d.name,
// 						description: ""
// 					}));

// 					// Add Select All on top
// 					if (result.length) {
// 						result.unshift({
// 							value: "__all",
// 							label: "Select All",
// 							description: ""
// 						});
// 					}

// 					return result;
// 				});
// 			},

// 			on_change() {

// 				let selected = frappe.query_report.get_filter_value("drawing_number") || [];

// 				// 🔁 If Select All clicked
// 				if (selected.includes("__all")) {

// 					let projects = frappe.query_report.get_filter_value("project_number") || [];
// 					let filters = [];

// 					if (projects.length) {
// 						filters.push(["project_number", "in", projects]);
// 					}

// 					frappe.call({
// 						method: "frappe.client.get_list",
// 						args: {
// 							doctype: "FT Add Drawing",
// 							fields: ["name"],
// 							filters: filters,
// 						}
// 					}).then(r => {

// 						let all_ids = (r.message || []).map(d => d.name);

// 						// 🔁 Toggle Logic
// 						if (selected.length - 1 === all_ids.length) {
// 							// All already selected → unselect all
// 							frappe.query_report.set_filter_value("drawing_number", []);
// 						} else {
// 							// Select all
// 							frappe.query_report.set_filter_value("drawing_number", all_ids);
// 						}

// 						frappe.query_report.refresh();
// 					});

// 					return;
// 				}

// 				// Normal selection refresh
// 				frappe.query_report.refresh();
// 			}
// 		},


// 		// ---------------- ITEM ----------------
// 		{
// 			fieldname: "item",
// 			label: "Drawing Parts",
// 			fieldtype: "MultiSelectList",

// 			get_data: function (txt) {

// 				let projects = frappe.query_report.get_filter_value("project_number") || [];
// 				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];
// 				let stock_types = frappe.query_report.get_filter_value("stock_rm_type") || [];

// 				// ---------------- CASE 1 ----------------
// 				// Nothing selected → show all items
// 				if (!projects.length && !drawings.length) {

// 					let filters = [["computed_name", "like", "%" + txt + "%"]];

// 					if (stock_types.length) {
// 						filters.push(["stock_rm_type", "in", stock_types]);
// 					}

// 					return frappe.call({
// 						method: "frappe.client.get_list",
// 						args: {
// 							doctype: "FT Stock RM List",
// 							fields: ["name", "computed_name"],
// 							filters: filters
// 						}
// 					}).then(r => {
// 						return (r.message || []).map(d => ({
// 							value: d.name,
// 							label: d.computed_name,
// 							description: ""
// 						}));
// 					});
// 				}

// 				// ---------------- CASE 2 ----------------
// 				// Project selected but no drawing
// 				if (projects.length && !drawings.length) {

// 					return frappe.call({
// 						method: "frappe.client.get_list",
// 						args: {
// 							doctype: "FT Drawing Parts",
// 							fields: ["item_id"],
// 							filters: [["project_number", "in", projects]]
// 						}
// 					}).then(r => {

// 						let unique_items = [...new Set((r.message || []).map(d => d.item_id))];
// 						if (!unique_items.length) return [];

// 						let filters = [
// 							["name", "in", unique_items],
// 							["computed_name", "like", "%" + txt + "%"]
// 						];

// 						if (stock_types.length) {
// 							filters.push(["stock_rm_type", "in", stock_types]);
// 						}

// 						return frappe.call({
// 							method: "frappe.client.get_list",
// 							args: {
// 								doctype: "FT Stock RM List",
// 								fields: ["name", "computed_name"],
// 								filters: filters
// 							}
// 						}).then(res => {
// 							return (res.message || []).map(d => ({
// 								value: d.name,
// 								label: d.computed_name,
// 								description: ""
// 							}));
// 						});

// 					});
// 				}


// 				// ---------------- CASE 3 ----------------
// 				// Drawing selected
// 				if (drawings.length) {

// 					// Step 1: Get FT Add Drawing document names
// 					return frappe.call({
// 						method: "frappe.client.get_list",
// 						args: {
// 							doctype: "FT Add Drawing",
// 							fields: ["name"],
// 							// filters: [
// 							// 	["drawing_number", "in", drawings]
// 							// ],
// 							filters: [
// 								["name", "in", drawings]
// 							],
// 							limit_page_length: 0
// 						}
// 					}).then(res => {

// 						let drawing_docnames = (res.message || []).map(d => d.name);
// 						if (!drawing_docnames.length) return [];

// 						// Step 2: Get item_id from Drawing Parts using correct link
// 						return frappe.call({
// 							method: "frappe.client.get_list",
// 							args: {
// 								doctype: "FT Drawing Parts",
// 								fields: ["item_id"],
// 								filters: [
// 									["drawing_number", "in", drawing_docnames]
// 								],
// 								limit_page_length: 0
// 							}
// 						}).then(r => {

// 							let unique_items = [...new Set(
// 								(r.message || [])
// 									.map(d => d.item_id)
// 									.filter(Boolean)
// 							)];

// 							if (!unique_items.length) return [];

// 							let filters = [
// 								["name", "in", unique_items],
// 								["computed_name", "like", "%" + txt + "%"]
// 							];

// 							if (stock_types.length) {
// 								filters.push(["stock_rm_type", "in", stock_types]);
// 							}

// 							return frappe.call({
// 								method: "frappe.client.get_list",
// 								args: {
// 									doctype: "FT Stock RM List",
// 									fields: ["name", "computed_name"],
// 									filters: filters,
// 									limit_page_length: 0
// 								}
// 							}).then(res2 => {
// 								return (res2.message || []).map(d => ({
// 									value: d.name,
// 									label: d.computed_name,
// 									description: ""
// 								}));
// 							});

// 						});

// 					});
// 				}
// 			},

// 			on_change() {
// 				clear_item_details();   // 👈 ADD THIS
// 				frappe.query_report.refresh();
// 			}
// 		},

// 		// ----------------- Section Type 
// 		{
// 			fieldname: "stock_rm_type",
// 			label: "Section Type",
// 			fieldtype: "MultiSelectList",
// 			get_data: function (txt) {
// 				return frappe.db.get_link_options("FT Section Type", txt);
// 			},
// 			on_change() {
// 				frappe.query_report.refresh();
// 				clear_item_details();
// 			}
// 		},

// 		// ---------------- IS ACTIVE ----------------
// 		{
// 			fieldname: "is_active",
// 			label: "Is Active",
// 			fieldtype: "Check",
// 			default: 1,
// 			on_change() {
// 				frappe.query_report.refresh();
// 				clear_item_details();
// 			}
// 		}

// 	],

// 	after_datatable_render(report) {
// 		$(report.wrapper)
// 			.off("click", ".view-btn")
// 			.on("click", ".view-btn", function () {

// 				// Remove active from all buttons
// 				$(".view-btn").removeClass("active-detail");

// 				// Add active to clicked button
// 				$(this).addClass("active-detail");


// 				let project = $(this).data("project");
// 				let item = $(this).data("item");

// 				// ✅ GET SELECTED DRAWING
// 				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

// 				if (!project || !item) {
// 					frappe.msgprint("No Data");
// 					return;
// 				}

// 				frappe.call({
// 					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_item_details",
// 					args: {
// 						project: project,
// 						item: item,
// 						// drawing_number: drawing_number  
// 						drawing_numbers: drawings.length ? JSON.stringify(drawings) : null
// 					},
// 					callback: function (r) {

// 						if (!r.message || !r.message.data || !r.message.data.length) {

// 							frappe.msgprint("No Details Found");
// 							return;
// 						}

// 						$("#item-detail-container").remove();

// 						let rows = "";
// 						let totalWeight = 0;

// 						r.message.data.forEach(d => {
// 							// Skip backend Total row from calculation
// 							// let is_total_row = String(d.drawing_number).toLowerCase().includes("total");
// 							let is_total_row = String(d.project_number).toLowerCase().includes("total");

// 							// Qty / Length / Width → 2 digit format
// 							let qty = d.quantity !== undefined && d.quantity !== "" ? String(d.quantity).padStart(2, '0') : "";
// 							let length = d.lenght !== undefined && d.lenght !== "" ? String(d.lenght).padStart(2, '0') : "";
// 							let width = d.width !== undefined && d.width !== "" ? String(d.width).padStart(2, '0') : "";

// 							// Weight → 3 decimal format
// 							let single_weight = d.single_weight !== undefined && d.single_weight !== "" ? parseFloat(d.single_weight).toFixed(3) : "";
// 							let total_weight = d.total_weight !== undefined && d.total_weight !== "" ? parseFloat(String(d.total_weight).replace(/<[^>]+>/g, '')).toFixed(3) : "";

// 							let row_style = "";
// 							let total_weight_style = "text-align:center;";

// 							if (is_total_row) {
// 								row_style = "background-color:#f8f9fa; font-weight:600;";
// 								total_weight_style = "text-align:center; color:#000; font-weight:700; font-size:15px;";
// 							}


// 							// is_total_row check ke baad row build karte waqt:

// 							let action_buttons = "";

// 							if (!is_total_row) {
// 								action_buttons = `
// 										<td style="text-align:center;">
// 											<div style="display:flex; gap:6px; justify-content:center;">
// 												<button class="btn btn-xs btn-success row-import-btn"
// 													style="min-width:60px;"
// 													data-project="${d.project_number || ''}"
// 													data-drawing="${d.drawing_number || ''}"
// 													data-position="${d.position_no || ''}"
// 													data-item="${item}">
// 													Import (show drawings)
// 												</button>
// 												<button class="btn btn-xs btn-warning row-export-btn"
// 													style="min-width:60px;"
// 													data-project="${d.project_number || ''}"
// 													data-drawing="${d.drawing_number || ''}"
// 													data-position="${d.position_no || ''}"    
// 													data-item="${item}">
// 													Export DXL/DWG
// 												</button>
// 											</div>
// 										</td>
// 									`;
// 							} else {
// 								action_buttons = `<td></td>`;
// 							}


// 							rows += `
// 								<tr style="${row_style}">
// 									<td style="text-align:center;">${d.serial_no || ""}</td>
// 								 	<td>${d.project_number || ""}</td>
//         							<td>${d.po_serial_no || ""}</td>
// 									<td>${d.drawing_number}</td>
// 									<td style="text-align:center;">${d.position_no || ""}</td>
// 									<td style="text-align:center;">${d.part_no || ""}</td>
// 									<td style="text-align:center;">${d.entry_count || ""}</td>
// 									<td style="${total_weight_style}">${qty}</td>
// 									<td style="${total_weight_style}">${length}</td>
// 									<td style="${total_weight_style}">${width}</td>
// 									<td style="text-align:center;">${single_weight}</td>
// 									<td style="${total_weight_style}">${total_weight}</td>

// 									${action_buttons}
// 								</tr>
// 							`;

// 							// Total calculation (skip backend total row)
// 							if (!is_total_row) {
// 								totalWeight += parseFloat(
// 									String(d.total_weight).replace(/<[^>]+>/g, '')
// 								) || 0;
// 							}

// 						});


// 						let html = `
// 							<div id="item-detail-container"
// 								style="margin-top:20px; padding:20px; border:1px solid #ddd;">

// 								<div style="display:flex;justify-content:space-between;align-items:center;">
// 									<h4>Item Details - ${r.message.item_name}</h4>
// 									<div style="display:flex; gap:20px;">
// 										<button class="btn btn-xs btn-primary summary-download" data-item="${item}"
// 											data-project="${project}">
// 											Download List
// 										</button>
// 										<button class="btn btn-xs btn-danger close-view">
// 											Close
// 										</button>
// 									</div>
// 								</div>

// 								<table class="table table-bordered" style="margin-top:15px;">
// 									<tr>
// 										<th style="text-align:center;">Sr No</th>
// 										<th >Project No</th>
// 										<th >Po Serial No</th>
// 										<th >Drawing</th>
// 										<th style="text-align: center;">Position No</th>
// 										<th style="text-align: center;">Part No</th>
// 										<th style="text-align:center;">Entry Count</th>
// 										<th style="text-align: center;">Qty</th>
// 										<th style="text-align: center;">Length</th>
// 										<th style="text-align: center;">Width</th>
// 										<th style="text-align: center;">Single Weight</th>
// 										<th style="text-align: center;">Total Weight</th>

// 										<th style="text-align: center;">Actions</th>
// 									</tr>
// 									${rows}
// 								</table>
// 							</div>
// 						`;

// 						$(report.wrapper).find(".datatable").after(html);

// 						// Import button click
// 						$(document).off("click", ".row-import-btn")
// 							.on("click", ".row-import-btn", function () {
// 								let project = $(this).data("project");
// 								let drawing = $(this).data("drawing");
// 								let position = $(this).data("position");
// 								let item_id = $(this).data("item");

// 								frappe.call({
// 									method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.import_row_data",
// 									args: {
// 										project: project,
// 										drawing_number: drawing,
// 										position_no: position,
// 										item: item_id
// 									},
// 									callback: function (r) {
// 										if (r.message && r.message.status === "success") {
// 											frappe.show_alert({
// 												message: r.message.msg || "Import successful",
// 												indicator: "green"
// 											});
// 										} else {
// 											frappe.show_alert({
// 												message: (r.message && r.message.msg) || "Import failed",
// 												indicator: "red"
// 											});
// 										}
// 									}
// 								});
// 							});

// 						// Export button click
// 						$(document).off("click", ".row-export-btn")
// 							.on("click", ".row-export-btn", function () {
// 								let project = $(this).data("project");
// 								let drawing = $(this).data("drawing");
// 								let position = $(this).data("position");
// 								let item_id = $(this).data("item");

// 								let params = new URLSearchParams({
// 									project: project,
// 									drawing_number: drawing,
// 									position_no: position,
// 									item: item_id
// 								});

// 								window.location.href =
// 									"/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.export_row_excel?"
// 									+ params.toString();
// 							});



// 						$(".close-view").on("click", function () {
// 							$("#item-detail-container").remove();
// 							$(".view-btn").removeClass("active-detail");
// 						});
// 					}
// 				});
// 			});


// 		// Dynamic button click
// 		$(document).off("click", ".summary-download")
// 			.on("click", ".summary-download", function () {

// 				let item_name = $(this).data("item");
// 				let project_name = $(this).data("project");

// 				let filters = {
// 					item: item_name,
// 					project: project_name
// 				};

// 				let url = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_details_excel"
// 					+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

// 				// window.open(url);
// 				window.location.href = url;
// 			});



// 		// ///////////save compaire button
// 		$(document).off("click", ".save-btn")
// 			.on("click", ".save-btn", function () {

// 				let data = $(this).data();

// 				frappe.call({
// 					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.save_row_data",
// 					args: {
// 						sr_no: data.srno,
// 						project: data.project,
// 						item_name: data.itemname,
// 						item_count: data.itemcount,
// 						quantity: data.qty,
// 						lenght: data.length,
// 						width: data.width,
// 						total_weight: data.weight
// 					},
// 					callback: function (r) {
// 						frappe.msgprint(r.message.msg || "Saved");
// 					}
// 				});

// 			});
// 		$(document).off("click", ".compare-btn")
// 			.on("click", ".compare-btn", function () {

// 				let data = $(this).data();

// 				frappe.call({
// 					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.compare_row_data",
// 					args: {
// 						sr_no: data.srno,
// 						project: data.project,
// 						item_name: data.itemname,
// 						item_count: data.itemcount,
// 						quantity: data.qty,
// 						lenght: data.length,
// 						width: data.width,
// 						total_weight: data.weight
// 					},
// 					callback: function (r) {

// 						if (!r.message) {
// 							frappe.msgprint("Server se response nahi aaya");
// 							return;
// 						}

// 						// ✅ Saved data not found
// 						if (r.message.status === "error") {
// 							frappe.msgprint({
// 								title: "Compare Result",
// 								message: `<b style="color:red;">⚠️ ${r.message.msg}</b><br><br>
// 									Click the <b>Save</b> button first, then the clothes. This text`,
// 								indicator: "red"
// 							});
// 							return;
// 						}

// 						let diff = r.message.difference;

// 						// ✅ No difference found
// 						if (!diff || !Object.keys(diff).length) {
// 							frappe.msgprint({
// 								title: "Compare Result",
// 								message: `<div style="text-align:center; padding:10px;">
// 									<span style="color:green; font-size:20px;">✅</span><br>
// 									<b style="color:green;">No Difference Found</b><br>
// 									Saved data aur current data same hai.
// 								</div>`,
// 								indicator: "green"
// 							});
// 							return;
// 						}

// 						// ✅ Show differences
// 						// Field labels for display
// 						let field_labels = {
// 							"total_entries": "Total Entries",
// 							"total_qty": "Total Qty",
// 							"total_length": "Total Length",
// 							"total_width": "Total Width",
// 							"total_weight": "Total Weight"
// 						};

// 						let html = `
// 							<table class="table table-bordered" style="margin-top:10px;">
// 								<thead>
// 									<tr style="background:#2F75B5; color:#fff;">
// 										<th>Field</th>
// 										<th>Saved Value</th>
// 										<th>Current Value</th>
// 										<th>Difference</th>
// 									</tr>
// 								</thead>
// 								<tbody>
// 						`;

// 						Object.keys(diff).forEach(f => {
// 							let saved_val = parseFloat(diff[f].saved || 0);
// 							let current_val = parseFloat(diff[f].current || 0);
// 							let difference = (current_val - saved_val).toFixed(3);
// 							let diff_color = difference > 0 ? "green" : "red";
// 							let diff_sign = difference > 0 ? "+" : "";

// 							html += `
// 								<tr>
// 									<td><b>${field_labels[f] || f}</b></td>
// 									<td style="color:#e65c00; text-align:center;">${saved_val}</td>
// 									<td style="color:#1a7abf; text-align:center;">${current_val}</td>
// 									<td style="color:${diff_color}; text-align:center; font-weight:bold;">
// 										${diff_sign}${difference}
// 									</td>
// 								</tr>
// 							`;
// 						});

// 						html += `</tbody></table>`;

// 						frappe.msgprint({
// 							title: `📊 Compare: ${data.itemname}`,
// 							message: html,
// 							wide: true,
// 							indicator: "orange"
// 						});
// 					}
// 				});
// 			});
// 		// ///////////save compaire utton


// 		setTimeout(() => {

// 			// Loop all rows
// 			$(report.wrapper).find(".datatable .dt-row").each(function () {

// 				let project_cell = $(this).find(".dt-cell").eq(1);

// 				if (project_cell.text().trim() === "TOTAL") {

// 					// Hide row number cell
// 					$(this).find(".dt-cell").eq(0).html("");

// 					// Optional: make TOTAL bold
// 					$(this).css("font-weight", "600");
// 				}
// 			});

// 		}, 100);
// 	}
// };

// // table refresh
// function clear_item_details() {
// 	$("#item-detail-container").remove();
// 	$(".view-btn").removeClass("active-detail");
// }


// // download current item details in Excel
// function download_item_details(item_name, project_name) {

// 	let filters = {
// 		item: item_name,
// 		project: project_name
// 	};

// 	let url = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_details_excel"
// 		+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

// 	let link = document.createElement("a");
// 	link.href = url;
// 	link.download = "Item_Details.xlsx";
// 	document.body.appendChild(link);
// 	link.click();
// 	document.body.removeChild(link);
// }

// // download full report both summary and detail tables in Excel with two defferent sheet for detail and summary
// function download_full_report(report) {
// 	if (!report.data || !report.data.length) {
// 		frappe.msgprint("No data to export");
// 		return;
// 	}

// 	if (!window.XLSX) {
// 		frappe.msgprint("Excel library loading... try again");
// 		return;
// 	}

// 	// SHEET 1 → SUMMARY TABLE
// 	let summary_data = [];

// 	let valid_columns = report.columns.filter(col =>
// 		col.fieldname && col.fieldname !== "view"
// 	);

// 	// Header row
// 	summary_data.push(valid_columns.map(col => col.label));

// 	// Data rows
// 	report.data.forEach(row => {
// 		summary_data.push(
// 			valid_columns.map(col => row[col.fieldname] ?? "")
// 		);
// 	});

// 	let summary_ws = XLSX.utils.aoa_to_sheet(summary_data);


// 	// SHEET 2 → ALL DETAILS

// 	let detail_data = [];
// 	detail_data.push([
// 		"Project",
// 		"Item",
// 		"Drawing",
// 		"Qty",
// 		"Length",
// 		"Width",
// 		"Single Weight",
// 		"Total Weight"
// 	]);

// 	let filters = frappe.query_report.get_filter_values();

// 	frappe.call({
// 		method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_all_details_for_export",
// 		args: {
// 			filters: filters
// 		},
// 		async: false,
// 		callback: function (r) {

// 			(r.message || []).forEach(d => {
// 				detail_data.push([
// 					d.project,
// 					d.item_id,
// 					d.drawing_number,
// 					d.quantity,
// 					d.lenght,
// 					d.width,
// 					d.single_weight,
// 					d.total_weight
// 				]);
// 			});
// 		}
// 	});

// 	let detail_ws = XLSX.utils.aoa_to_sheet(detail_data);

// 	// CREATE WORKBOOK

// 	let wb = XLSX.utils.book_new();
// 	XLSX.utils.book_append_sheet(wb, summary_ws, "Summary");
// 	XLSX.utils.book_append_sheet(wb, detail_ws, "Details");

// 	XLSX.writeFile(wb, "FT_Drawing_Part_Report.xlsx");
// }

// if (!window.XLSX) {
// 	let script = document.createElement("script");
// 	script.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
// 	document.head.appendChild(script);
// }



// $(`<style>

// .datatable .dt-scrollable {
//     overflow-x: auto !important;
// }

// .datatable-wrapper {
//     width: 100% !important;
// 	overflow-x: auto;
// }

// .report-wrapper {
//     max-width: 100% !important;
// }

// .report-summary .summary-item{
// 		max-width: 100%;
// 		min-width: 100%;
// 		height: 100%;
// 		display: block;
// 		place-content: unset;
// 		margin: 0;
// 	}
// 	.summary-container{
// 		display: grid;
// 		grid-template-columns: repeat(1, 1fr) !important;
// 		// place-items: center;
// 		gap: 20px;
// 	}
// 	@media (min-width: 768px) and (max-width: 1023px) {
// 		.summary-container{
// 			grid-template-columns: repeat(2, 1fr) !important;
// 		}
// 	}
// 	@media (min-width: 1024px) {
// 		.summary-container{
// 			grid-template-columns: repeat(5, 1fr) !important;
// 		}
// 	}
// 	.report-summary .summary-value .summary-container {
// 		padding: 20px;
// 	}
// 	.summary-section{
// 		width: 100%;
// 		background: #fff;
// 		padding: 20px;
// 		border-radius: 10px;
// 		text-align: center;
// 		transition: all 0.2s ease;
// 		border: 2px solid #eef0f4;
// 	}
// 	.section-content-count p{
// 		font-size: 14px;
// 		font-weight: 400;
// 		color: #525252;
// 	}
// 	.section-content-count span{
// 		font-size: 16px;
// 		font-weight: 600;
// 		line-height: 20px;
// 		padding-top: 12px;
// 		padding-bottom: 5px;
// 		color: #000;
// 	}
// 	.report-summary {
// 		background-color: none;
// 		border-radius: 0;
// 		border-bottom: 0;
// 		margin: 0;
// 		padding: 0;
// 		display: block;
// 		flex-wrap: unset;
// 		align-items: unset;
// 		justify-content: unset;
// 		gap: 0px;
// 	}
// 	.table{
// 		width: 100% !important;
// 	}
// 	/* button view active color*/
// 	.view-btn.active-detail {
// 		background-color: #0c5c70 !important;
// 		color: #fff !important;
// 		border-color: #0c5c70  !important;
// 		box-shadow: 0 0 0 2px rgba(21, 54, 102, 0.25);
// 	}


// /* ===== FIX ROW NUMBER COLUMN ===== */

// .datatable .dt-cell--col-0 {
//     min-width: 50px !important;
//     width: 50px !important;
//     max-width: 50px !important;
//     text-align: center !important;
// }

// .datatable .dt-row .dt-cell {
//     white-space: nowrap !important;
// }
// .datatable .dt-cell__content--header-0, .datatable .dt-cell__content--col-0{
// 	padding: 0 !important;
// }
// </style>`).appendTo("head");

















frappe.query_reports["FT Drawing Part Report 2"] = {

	onload(report) {
		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("item", []);
		frappe.query_report.set_filter_value("is_active", 1);

		// Add download item details button to summary table
		report.page.add_inner_button("Download Item Excel", function () {
			let filters = report.get_values();

			let params = new URLSearchParams({
				filters: JSON.stringify(filters)
			});

			// ✅ window.location.href — sabse reliable Frappe binary download ke liye
			window.location.href = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_excel?" + params.toString();
		});

		// Add download full report button to both summary and detail tables in Excel with two different sheets for detail and summary
		report.page.add_inner_button("Download Full Report", function () {

			frappe.call({
				method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_all_details_for_export",
				args: { filters: report.get_values() },
				callback: function (r) {
					if (r.message) {
						const link = document.createElement("a");
						link.href = r.message;
						link.download = "FT_Drawing_Part_Report.xlsx";
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
					}
				}
			});

		});




		// ///////////save compaire button
		report.page.add_inner_button("💾 Save Snapshot", function () {
			let report_data = frappe.query_report.data || [];

			// Filter out TOTAL row
			let rows_to_save = report_data.filter(d =>
				d.project_name && d.project_name !== "TOTAL" && d.item_id
			);

			if (!rows_to_save.length) {
				frappe.msgprint("Koi data nahi hai save karne ke liye");
				return;
			}

			frappe.confirm(
				`Kya aap ${rows_to_save.length} rows ka snapshot save karna chahte ho?`,
				function () {
					let promises = rows_to_save.map((row, i) => {
						return frappe.call({
							method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.save_row_data",
							args: {
								sr_no: i + 1,
								project: row.project_name,
								item_name: row.item_name,
								item_count: row.item_count,
								quantity: row.quantity,
								lenght: row.lenght,
								width: row.width,
								total_weight: row.total_weight
							}
						});
					});

					Promise.all(promises).then(() => {
						frappe.show_alert({
							message: `✅ ${rows_to_save.length} rows saved successfully!`,
							indicator: "green"
						});
					});
				}
			);
		});

		// ✅ COMPARE ALL - Header button
		report.page.add_inner_button("📊 Compare Snapshot", function () {
			let report_data = frappe.query_report.data || [];

			let rows_to_compare = report_data.filter(d =>
				d.project_name && d.project_name !== "TOTAL" && d.item_id
			);

			if (!rows_to_compare.length) {
				frappe.msgprint("Koi data nahi hai compare karne ke liye");
				return;
			}

			// Fetch all compare data
			let promises = rows_to_compare.map(row => {
				return frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.compare_row_data",
					args: {
						sr_no: "",
						project: row.project_name,
						item_name: row.item_name,
						item_count: row.item_count,
						quantity: row.quantity,
						lenght: row.lenght,
						width: row.width,
						total_weight: row.total_weight
					}
				});
			});

			// 	Promise.all(promises).then(results => {

			// 		let field_labels = {
			// 			"total_entries": "Total Entries",
			// 			"total_qty": "Total Qty",
			// 			"total_length": "Total Length",
			// 			"total_width": "Total Width",
			// 			"total_weight": "Total Weight"
			// 		};

			// 		let fields = ["total_entries", "total_qty", "total_length", "total_width", "total_weight"];

			// 		let html = `
			//     <div style="overflow-x:auto;">
			//     <table class="table table-bordered" style="font-size:12px; min-width:900px;">
			//         <thead>
			//             <tr style="background:#1F4E79; color:#fff; text-align:center;">
			//                 <th style="min-width:90px;">Project</th>
			//                 <th style="min-width:200px;">Item</th>
			//                 <th style="min-width:100px;">Field</th>
			// `;

			// 		// Find max revisions count across all rows
			// 		let max_revisions = 0;
			// 		results.forEach(r => {
			// 			if (r.message && r.message.status === "success") {
			// 				max_revisions = Math.max(max_revisions, (r.message.revision_log || []).length);
			// 			}
			// 		});

			// 		// Dynamic revision headers
			// 		for (let i = 0; i < max_revisions; i++) {
			// 			html += `<th style="min-width:130px;">Revision ${i + 1}</th>`;
			// 		}
			// 		html += `<th style="min-width:130px; background:#0c5c70;">Current Value</th>`;
			// 		html += `</tr></thead><tbody>`;

			// 		results.forEach(r => {
			// 			if (!r.message || r.message.status !== "success") return;

			// 			let { revision_log, current, current_timestamp, project, item_name } = r.message;

			// 			// Check if anything changed vs last revision
			// 			let last = revision_log.length ? revision_log[revision_log.length - 1] : null;
			// 			let has_any_diff = fields.some(f =>
			// 				last ? parseFloat(last[f] || 0) !== parseFloat(current[f] || 0) : true
			// 			);

			// 			fields.forEach((f, fi) => {
			// 				let last_val = last ? parseFloat(last[f] || 0) : null;
			// 				let curr_val = parseFloat(current[f] || 0);
			// 				let field_changed = last_val !== null && last_val !== curr_val;

			// 				// Row style - highlight changed rows
			// 				let row_bg = field_changed ? "#fff8e1" : "#fff";

			// 				let row = `<tr style="background:${row_bg};">`;

			// 				// Project & Item - only show on first field row
			// 				if (fi === 0) {
			// 					row += `
			//                 <td rowspan="${fields.length}" style="vertical-align:middle; font-weight:600; text-align:center;">${project}</td>
			//                 <td rowspan="${fields.length}" style="vertical-align:middle; font-size:11px;">${item_name}</td>
			//             `;
			// 				}

			// 				row += `<td style="font-weight:600; text-align:center;">${field_labels[f]}</td>`;

			// 				// Revision columns
			// 				for (let i = 0; i < max_revisions; i++) {
			// 					let rev = revision_log[i];
			// 					if (rev) {
			// 						let val = parseFloat(rev[f] || 0);
			// 						// Check if this revision changed from previous
			// 						let prev_val = i > 0 ? parseFloat(revision_log[i - 1][f] || 0) : null;
			// 						let changed = prev_val !== null && prev_val !== val;
			// 						let cell_color = changed ? "color:#e65c00; font-weight:bold;" : "color:#333;";

			// 						row += `
			//                     <td style="text-align:center; ${cell_color}">
			//                         ${val}
			//                         <br><small style="color:#888; font-size:10px;">${rev.timestamp}</small>
			//                     </td>
			//                 `;
			// 					} else {
			// 						row += `<td style="text-align:center; color:#ccc;">-</td>`;
			// 					}
			// 				}

			// 				// Current value column
			// 				let curr_changed = last_val !== null && last_val !== curr_val;
			// 				let curr_style = curr_changed
			// 					? "color:#1a7abf; font-weight:bold; background:#e8f4fd;"
			// 					: "color:#333;";

			// 				row += `
			//             <td style="text-align:center; ${curr_style}">
			//                 ${curr_val}
			//                 <br><small style="color:#888; font-size:10px;">${current_timestamp}</small>
			//                 ${curr_changed ? '<br><small style="color:green;">▲ Changed</small>' : '<br><small style="color:#aaa;">No Change</small>'}
			//             </td>
			//         `;

			// 				row += `</tr>`;
			// 				html += row;
			// 			});

			// 			// Separator row
			// 			html += `<tr style="background:#f0f0f0;"><td colspan="${max_revisions + 3}" style="padding:3px;"></td></tr>`;
			// 		});

			// 		html += `</tbody></table></div>`;

			// 		frappe.msgprint({
			// 			title: "📊 Revision History - All Items",
			// 			message: html,
			// 			wide: true,
			// 			indicator: "blue"
			// 		});
			// 	});
			Promise.all(promises).then(results => {

				let field_labels = {
					"total_entries": "Total Entries",
					"total_qty": "Total Qty",
					"total_length": "Total Length",
					"total_width": "Total Width",
					"total_weight": "Total Weight"
				};
				let fields = ["total_entries", "total_qty", "total_length", "total_width", "total_weight"];

				// ── Unique items only (duplicate item_name skip karo) ──
				let seen_items = new Set();
				let unique_results = [];
				results.forEach(r => {
					if (r.message && r.message.status === "success") {
						if (!seen_items.has(r.message.item_name)) {
							seen_items.add(r.message.item_name);
							unique_results.push(r);
						}
					}
				});

				// ── Max revisions ──
				let max_revisions = 0;
				unique_results.forEach(r => {
					max_revisions = Math.max(max_revisions, (r.message.revision_log || []).length);
				});

				// ── Table header ──
				let html = `
        <div style="overflow-x:auto;">
        <table class="table table-bordered" style="font-size:12px; min-width:1000px;">
            <thead>
                <tr style="background:#1F4E79; color:#fff; text-align:center;">
                    <th style="min-width:180px;">Projects</th>
                    <th style="min-width:200px;">Item</th>
                    <th style="min-width:80px;">Project Count</th>
                    <th style="min-width:110px;">Field</th>
    `;

				for (let i = 0; i < max_revisions; i++) {
					html += `<th style="min-width:130px;">Revision ${i + 1}</th>`;
				}
				html += `<th style="min-width:140px; background:#0c5c70;">Current Value</th>`;
				html += `</tr></thead><tbody>`;

				// ── Data rows ──
				unique_results.forEach(r => {
					if (!r.message || r.message.status !== "success") return;

					let { revision_log, current, current_timestamp, project, project_count, item_name } = r.message;
					let last = revision_log.length ? revision_log[revision_log.length - 1] : null;

					fields.forEach((f, fi) => {
						let last_val = last ? parseFloat(last[f] || 0) : null;
						let curr_val = parseFloat(current[f] || 0);
						let field_changed = last_val !== null && last_val !== curr_val;
						let row_bg = field_changed ? "#fff8e1" : "#fff";

						let row = `<tr style="background:${row_bg};">`;

						// ── Project, Item, Count — sirf first field row mein ──
						if (fi === 0) {
							row += `
                    <td rowspan="${fields.length}" style="vertical-align:middle; font-weight:600; 
                        text-align:center; font-size:11px; color:#1F4E79;">
                        ${project}
                    </td>
                    <td rowspan="${fields.length}" style="vertical-align:middle; font-size:11px;">
                        ${item_name}
                    </td>
                    <td rowspan="${fields.length}" style="vertical-align:middle; text-align:center; 
                        font-weight:700; font-size:14px; color:#2F75B5;">
                        ${project_count}
                    </td>
                `;
						}

						// Field label
						row += `<td style="font-weight:600; text-align:center;">${field_labels[f]}</td>`;

						// Revision columns
						for (let i = 0; i < max_revisions; i++) {
							let rev = revision_log[i];
							if (rev) {
								let val = parseFloat(rev[f] || 0);
								let prev_val = i > 0 ? parseFloat(revision_log[i - 1][f] || 0) : null;
								let changed = prev_val !== null && prev_val !== val;
								let style = changed ? "color:#e65c00; font-weight:bold;" : "color:#333;";
								row += `
                        <td style="text-align:center; ${style}">
                            ${val}
                            <br><small style="color:#888; font-size:10px;">${rev.timestamp || ""}</small>
                        </td>
                    `;
							} else {
								row += `<td style="text-align:center; color:#ccc;">-</td>`;
							}
						}

						// Current value
						let curr_changed = last_val !== null && last_val !== curr_val;
						let curr_style = curr_changed
							? "color:#1a7abf; font-weight:bold; background:#e8f4fd;"
							: "color:#555;";

						row += `
                <td style="text-align:center; ${curr_style}">
                    ${curr_val}
                    <br><small style="color:#888; font-size:10px;">${current_timestamp}</small>
                    ${curr_changed
								? '<br><small style="color:green; font-weight:bold;">▲ Changed</small>'
								: '<br><small style="color:#aaa;">No Change</small>'}
                </td>
            `;

						row += `</tr>`;
						html += row;
					});

					// Separator
					html += `<tr style="background:#e8edf2; height:6px;">
            <td colspan="${max_revisions + 4}" style="padding:0;"></td>
        </tr>`;
				});

				html += `</tbody></table></div>`;

				// frappe.msgprint({
				// 	title: "📊 Revision History — Grouped by Item",
				// 	message: html,
				// 	wide: true,
				// 	indicator: "blue"
				// });
				// ── Saara data backend ko bhejo Excel ke liye ──
				let export_data = unique_results.map(r => r.message);

				frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.export_compare_snapshot_excel",
					args: {
						snapshot_data: JSON.stringify(export_data)
					},
					callback: function(res) {
						if (res.message) {
							const link = document.createElement("a");
							link.href = res.message;
							link.download = "Compare_Snapshot.xlsx";
							document.body.appendChild(link);
							link.click();
							document.body.removeChild(link);
						}
					}
				});
			});
		});
		// ///////////save compaire utton



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

		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let filters = [];

				if (txt) {
					filters.push(["name", "like", "%" + txt + "%"]);
				}

				if (projects.length) {
					filters.push(["project_number", "in", projects]);
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "FT Add Drawing",
						fields: ["name"],
						filters: filters,
					}
				}).then(r => {

					let result = (r.message || []).map(d => ({
						value: d.name,
						label: d.name,
						description: ""
					}));

					// Add Select All on top
					if (result.length) {
						result.unshift({
							value: "__all",
							label: "Select All",
							description: ""
						});
					}

					return result;
				});
			},

			on_change() {

				let selected = frappe.query_report.get_filter_value("drawing_number") || [];

				// 🔁 If Select All clicked
				if (selected.includes("__all")) {

					let projects = frappe.query_report.get_filter_value("project_number") || [];
					let filters = [];

					if (projects.length) {
						filters.push(["project_number", "in", projects]);
					}

					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Add Drawing",
							fields: ["name"],
							filters: filters,
						}
					}).then(r => {

						let all_ids = (r.message || []).map(d => d.name);

						// 🔁 Toggle Logic
						if (selected.length - 1 === all_ids.length) {
							// All already selected → unselect all
							frappe.query_report.set_filter_value("drawing_number", []);
						} else {
							// Select all
							frappe.query_report.set_filter_value("drawing_number", all_ids);
						}

						frappe.query_report.refresh();
					});

					return;
				}

				// Normal selection refresh
				frappe.query_report.refresh();
			}
		},


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
							fields: ["item_id"],
							filters: [["project_number", "in", projects]]
						}
					}).then(r => {

						let unique_items = [...new Set((r.message || []).map(d => d.item_id))];
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
							// filters: [
							// 	["drawing_number", "in", drawings]
							// ],
							filters: [
								["name", "in", drawings]
							],
							limit_page_length: 0
						}
					}).then(res => {

						let drawing_docnames = (res.message || []).map(d => d.name);
						if (!drawing_docnames.length) return [];

						// Step 2: Get item_id from Drawing Parts using correct link
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Drawing Parts",
								fields: ["item_id"],
								filters: [
									["drawing_number", "in", drawing_docnames]
								],
								limit_page_length: 0
							}
						}).then(r => {

							let unique_items = [...new Set(
								(r.message || [])
									.map(d => d.item_id)
									.filter(Boolean)
							)];

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
									filters: filters,
									limit_page_length: 0
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
							// let is_total_row = String(d.drawing_number).toLowerCase().includes("total");
							let is_total_row = String(d.project_number).toLowerCase().includes("total");

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


							// is_total_row check ke baad row build karte waqt:

							let action_buttons = "";

							if (!is_total_row) {
								action_buttons = `
										<td style="text-align:center;">
											<div style="display:flex; gap:6px; justify-content:center;">
												<button class="btn btn-xs btn-success row-import-btn"
													style="min-width:60px;"
													data-project="${d.project_number || ''}"
													data-drawing="${d.drawing_number || ''}"
													data-position="${d.position_no || ''}"
													data-item="${item}">
													Import (show drawings)
												</button>
												<button class="btn btn-xs btn-warning row-export-btn"
													style="min-width:60px;"
													data-project="${d.project_number || ''}"
													data-drawing="${d.drawing_number || ''}"
													data-position="${d.position_no || ''}"    
													data-item="${item}">
													Export DXL/DWG
												</button>
											</div>
										</td>
									`;
							} else {
								action_buttons = `<td></td>`;
							}


							rows += `
								<tr style="${row_style}">
									<td style="text-align:center;">${d.serial_no || ""}</td>
								 	<td>${d.project_number || ""}</td>
        							<td>${d.po_serial_no || ""}</td>
									<td>${d.drawing_number}</td>
									<td style="text-align:center;">${d.position_no || ""}</td>
									<td style="text-align:center;">${d.part_no || ""}</td>
									<td style="text-align:center;">${d.entry_count || ""}</td>
									<td style="${total_weight_style}">${qty}</td>
									<td style="${total_weight_style}">${length}</td>
									<td style="${total_weight_style}">${width}</td>
									<td style="text-align:center;">${single_weight}</td>
									<td style="${total_weight_style}">${total_weight}</td>

									${action_buttons}
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
										<button class="btn btn-xs btn-primary summary-download" data-item="${item}"
											data-project="${project}">
											Download List
										</button>
										<button class="btn btn-xs btn-danger close-view">
											Close
										</button>
									</div>
								</div>

								<table class="table table-bordered" style="margin-top:15px;">
									<tr>
										<th style="text-align:center;">Sr No</th>
										<th >Project No</th>
										<th >Po Serial No</th>
										<th >Drawing</th>
										<th style="text-align: center;">Position No</th>
										<th style="text-align: center;">Part No</th>
										<th style="text-align:center;">Entry Count</th>
										<th style="text-align: center;">Qty</th>
										<th style="text-align: center;">Length</th>
										<th style="text-align: center;">Width</th>
										<th style="text-align: center;">Single Weight</th>
										<th style="text-align: center;">Total Weight</th>

										<th style="text-align: center;">Actions</th>
									</tr>
									${rows}
								</table>
							</div>
						`;

						$(report.wrapper).find(".datatable").after(html);

						// Import button click
						$(document).off("click", ".row-import-btn")
							.on("click", ".row-import-btn", function () {
								let project = $(this).data("project");
								let drawing = $(this).data("drawing");
								let position = $(this).data("position");
								let item_id = $(this).data("item");

								frappe.call({
									method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.import_row_data",
									args: {
										project: project,
										drawing_number: drawing,
										position_no: position,
										item: item_id
									},
									callback: function (r) {
										if (r.message && r.message.status === "success") {
											frappe.show_alert({
												message: r.message.msg || "Import successful",
												indicator: "green"
											});
										} else {
											frappe.show_alert({
												message: (r.message && r.message.msg) || "Import failed",
												indicator: "red"
											});
										}
									}
								});
							});

						// Export button click
						$(document).off("click", ".row-export-btn")
							.on("click", ".row-export-btn", function () {
								let project = $(this).data("project");
								let drawing = $(this).data("drawing");
								let position = $(this).data("position");
								let item_id = $(this).data("item");

								let params = new URLSearchParams({
									project: project,
									drawing_number: drawing,
									position_no: position,
									item: item_id
								});

								window.location.href =
									"/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.export_row_excel?"
									+ params.toString();
							});



						$(".close-view").on("click", function () {
							$("#item-detail-container").remove();
							$(".view-btn").removeClass("active-detail");
						});
					}
				});
			});


		// Dynamic button click
		$(document).off("click", ".summary-download")
			.on("click", ".summary-download", function () {

				let item_name = $(this).data("item");
				let project_name = $(this).data("project");

				let filters = {
					item: item_name,
					project: project_name
				};

				let url = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_details_excel"
					+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

				// window.open(url);
				window.location.href = url;
			});

		setTimeout(() => {

			// Loop all rows
			$(report.wrapper).find(".datatable .dt-row").each(function () {

				let project_cell = $(this).find(".dt-cell").eq(1);

				if (project_cell.text().trim() === "TOTAL") {

					// Hide row number cell
					$(this).find(".dt-cell").eq(0).html("");

					// Optional: make TOTAL bold
					$(this).css("font-weight", "600");
				}
			});

		}, 100);
	}
};

// table refresh
function clear_item_details() {
	$("#item-detail-container").remove();
	$(".view-btn").removeClass("active-detail");
}


// download current item details in Excel
function download_item_details(item_name, project_name) {

	let filters = {
		item: item_name,
		project: project_name
	};

	let url = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_details_excel"
		+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

	let link = document.createElement("a");
	link.href = url;
	link.download = "Item_Details.xlsx";
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}

// download full report both summary and detail tables in Excel with two defferent sheet for detail and summary
function download_full_report(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint("No data to export");
		return;
	}

	if (!window.XLSX) {
		frappe.msgprint("Excel library loading... try again");
		return;
	}

	// SHEET 1 → SUMMARY TABLE
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


	// SHEET 2 → ALL DETAILS

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
					d.item_id,
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

	// CREATE WORKBOOK

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

.datatable .dt-scrollable {
    overflow-x: auto !important;
}

.datatable-wrapper {
    width: 100% !important;
	overflow-x: auto;
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


/* ===== FIX ROW NUMBER COLUMN ===== */

.datatable .dt-cell--col-0 {
    min-width: 50px !important;
    width: 50px !important;
    max-width: 50px !important;
    text-align: center !important;
}

.datatable .dt-row .dt-cell {
    white-space: nowrap !important;
}
.datatable .dt-cell__content--header-0, .datatable .dt-cell__content--col-0{
	padding: 0 !important;
}
</style>`).appendTo("head");













