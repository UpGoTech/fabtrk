
frappe.query_reports["FT Drawing Part Report 2"] = {

	onload(report) {
		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("po_no", []);
		frappe.query_report.set_filter_value("item", []);
		frappe.query_report.set_filter_value("is_active", 1);


		// Add download item details button to summary table - Header button
		report.page.add_inner_button("Download Summary", function () {
			let filters = report.get_values();

			let params = new URLSearchParams({
				filters: JSON.stringify(filters)
			});

			// ✅ window.location.href — sabse reliable Frappe binary download ke liye
			window.location.href = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.download_item_excel?" + params.toString();
		});

		// DOWNLOAD FULL REPORT BUTTON - Header button
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


		// SAVE SNAPSHOT BUTTON - Header button
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

					Promise.all(promises).then(results => {

						// Kitne actually save hue aur kitne same the
						let saved_count = 0;
						let no_change_count = 0;

						results.forEach(r => {
							if (r.message && r.message.status === "success") {
								if (r.message.msg && r.message.msg.includes("same")) {
									no_change_count++;
								} else {
									saved_count++;
								}
							}
						});

						// Sab same hain — koi change nahi
						if (no_change_count === rows_to_save.length) {
							frappe.msgprint({
								title: "No Changes Found",
								message: `⚠️ No changes were found in the data, so the snapshot was not saved. The previous snapshot remains unchanged.`,
								indicator: "orange"
							});
						}
						// Kuch save hue, kuch same the
						else if (saved_count > 0 && no_change_count > 0) {
							frappe.show_alert({
								message: `✅ ${saved_count} rows saved | ⏭️ ${no_change_count} No Chnages in the row`,
								indicator: "blue"
							});
						}
						// Sab save ho gaye
						else if (saved_count > 0) {
							frappe.show_alert({
								message: `✅ ${saved_count} rows saved successfully!`,
								indicator: "green"
							});
						}
					});
				}
			);
		});

		// COMPARE SNAPSHOT BUTTON - Header button
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

				let export_data = unique_results.map(r => r.message);

				frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.export_compare_snapshot_excel",
					args: {
						snapshot_data: JSON.stringify(export_data)
					},
					callback: function (res) {
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
				let is_active = frappe.query_report.get_filter_value("is_active");
				let filters = [];

				if (txt) {
					filters.push(["name", "like", "%" + txt + "%"]);
				}

				if (is_active) {
					filters.push(["is_active", "=", 1]);
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "FT Project",
						fields: ["name", "description"],
						filters: filters,
						limit_page_length: 0
					}
				}).then(r => {
					return (r.message || []).map(d => ({
						value: d.name,
						label: d.name,
						description: d.description || ""
					}));
				});
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("po_no", []);
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
				let is_active = frappe.query_report.get_filter_value("is_active");

				let get_project_names = () => {
					if (projects.length) {
						return Promise.resolve(projects);
					} else if (is_active) {
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Project",
								fields: ["name"],
								filters: [["is_active", "=", 1]],
								limit_page_length: 0
							}
						}).then(r => (r.message || []).map(d => d.name));
					} else {
						return Promise.resolve([]);
					}
				};

				return get_project_names().then(project_names => {
					let filters = [];
					if (txt) filters.push(["name", "like", "%" + txt + "%"]);
					if (project_names.length) filters.push(["project_number", "in", project_names]);
					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Add Drawing",
							fields: ["name"],
							filters: filters,
							limit_page_length: 0
						}
					}).then(r => {
						let result = (r.message || []).map(d => ({
							value: d.name,
							label: d.name,
							description: ""
						}));
						if (result.length) {
							result.unshift({ value: "__all", label: "Select All", description: "" });
						}
						return result;
					});
				});
			},
			on_change() {
				let selected = frappe.query_report.get_filter_value("drawing_number") || [];

				if (selected.includes("__all")) {
					let projects = frappe.query_report.get_filter_value("project_number") || [];
					let is_active = frappe.query_report.get_filter_value("is_active");

					let get_project_names = () => {
						if (projects.length) {
							return Promise.resolve(projects);
						} else if (is_active) {
							return frappe.call({
								method: "frappe.client.get_list",
								args: {
									doctype: "FT Project",
									fields: ["name"],
									filters: [["is_active", "=", 1]],
									limit_page_length: 0
								}
							}).then(r => (r.message || []).map(d => d.name));
						} else {
							return Promise.resolve([]);
						}
					};

					get_project_names().then(project_names => {
						let filters = [];
						if (project_names.length) filters.push(["project_number", "in", project_names]);
						frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Add Drawing",
								fields: ["name"],
								filters: filters,
								limit_page_length: 0
							}
						}).then(r => {
							let all_ids = (r.message || []).map(d => d.name);
							if (selected.length - 1 === all_ids.length) {
								frappe.query_report.set_filter_value("drawing_number", []);
							} else {
								frappe.query_report.set_filter_value("drawing_number", all_ids);
							}
							frappe.query_report.set_filter_value("po_no", []);
							frappe.query_report.refresh();
						});
					});
					return;
				}

				frappe.query_report.set_filter_value("po_no", []);
				frappe.query_report.refresh();
			}
		},

		// ---------------- PO NUMBER ----------------
		{
			fieldname: "po_no",
			label: "PO Number",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];
				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let is_active = frappe.query_report.get_filter_value("is_active");

				let get_active_projects = () => {
					if (projects.length) {
						return Promise.resolve(projects);
					} else if (is_active) {
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Project",
								fields: ["name"],
								filters: [["is_active", "=", 1]],
								limit_page_length: 0
							}
						}).then(r => (r.message || []).map(d => d.name));
					} else {
						return Promise.resolve([]);
					}
				};

				// CASE 1: Drawing selected — sirf unke PO Numbers
				if (drawings.length) {
					let filters = [["drawing_number", "in", drawings]];
					if (txt) filters.push(["po_no", "like", "%" + txt + "%"]);

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Drawing Parts",
							fields: ["po_no"],
							filters: filters,
							limit_page_length: 0
						}
					}).then(r => {
						let unique = {};
						(r.message || []).forEach(d => {
							if (d.po_no && !unique[d.po_no]) unique[d.po_no] = true;
						});
						return Object.keys(unique).map(po => ({
							value: po,
							label: po,
							description: ""
						}));
					});
				}

				// CASE 2: Project / is_active se filter
				return get_active_projects().then(project_names => {
					let filters = [];
					if (txt) filters.push(["po_no", "like", "%" + txt + "%"]);
					if (project_names.length) filters.push(["project_number", "in", project_names]);

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Drawing Parts",
							fields: ["po_no"],
							filters: filters,
							limit_page_length: 0
						}
					}).then(r => {
						let unique = {};
						(r.message || []).forEach(d => {
							if (d.po_no && !unique[d.po_no]) unique[d.po_no] = true;
						});
						return Object.keys(unique).map(po => ({
							value: po,
							label: po,
							description: ""
						}));
					});
				});
			},
			on_change() {
				frappe.query_report.refresh();
				clear_item_details();
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
				let is_active = frappe.query_report.get_filter_value("is_active");

				let get_active_projects = () => {
					if (projects.length) {
						return Promise.resolve(projects);
					} else if (is_active) {
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Project",
								fields: ["name"],
								filters: [["is_active", "=", 1]],
								limit_page_length: 0
							}
						}).then(r => (r.message || []).map(d => d.name));
					} else {
						return Promise.resolve([]);
					}
				};

				let get_items_from_drawings = (drawing_names) => {
					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Drawing Parts",
							fields: ["item_id"],
							filters: [["drawing_number", "in", drawing_names]],
							limit_page_length: 0
						}
					}).then(r => {
						let unique_items = [...new Set(
							(r.message || []).map(d => d.item_id).filter(Boolean)
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
						}).then(res => (res.message || []).map(d => ({
							value: d.name,
							label: d.computed_name,
							description: ""
						})));
					});
				};

				if (drawings.length) {
					return get_items_from_drawings(drawings);
				}

				return get_active_projects().then(project_names => {
					if (!project_names.length) {
						let filters = [["computed_name", "like", "%" + txt + "%"]];
						if (stock_types.length) filters.push(["stock_rm_type", "in", stock_types]);
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Stock RM List",
								fields: ["name", "computed_name"],
								filters: filters,
								limit_page_length: 0
							}
						}).then(r => (r.message || []).map(d => ({
							value: d.name,
							label: d.computed_name,
							description: ""
						})));
					}

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Add Drawing",
							fields: ["name"],
							filters: [["project_number", "in", project_names]],
							limit_page_length: 0
						}
					}).then(r => {
						let drawing_names = (r.message || []).map(d => d.name);
						if (!drawing_names.length) return [];
						return get_items_from_drawings(drawing_names);
					});
				});
			},
			on_change() {
				clear_item_details();
				frappe.query_report.refresh();
			}
		},

		// ----------------- Section Type ----------------
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
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("po_no", []);
				frappe.query_report.set_filter_value("item", []);
				frappe.query_report.refresh();
				clear_item_details();
			}
		}

	],

	after_datatable_render(report) {
		// ── VIEW BUTTON CLICK ──
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
										<button class="btn btn-xs btn-primary nesting-export">
											Nesting data export
										</button>
										<!-- ✅ UPDATED: Nesting Report button with class + data attrs -->
										<button class="btn btn-xs btn-primary nesting-report-btn"
											data-item="${item}"
											data-project="${project}"
											data-item-name="${r.message.item_name}">
											Nesting Report
										</button>
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
					}
				});
			});

		//Excel Dynamic button click
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

		// ── Nesting 
		$(document).off("click", ".nesting-export")
			.on("click", ".nesting-export", function () {

				let item_name = $(".summary-download").data("item");
				let project_name = $(".summary-download").data("project");

				let filters = {
					item: item_name,
					project: project_name
				};

				let url = "/api/method/fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.export_nesting_json"
					+ "?filters=" + encodeURIComponent(JSON.stringify(filters));

				window.location.href = url;

			});

		// Nesting Report button click handler
		$(document).off("click", ".nesting-report-btn")
			.on("click", ".nesting-report-btn", function () {
				let item_name = $(this).data("item");
				let project_name = $(this).data("project");
				let display_name = $(this).data("item-name") || item_name;
				show_nesting_report_modal(item_name, project_name, display_name);
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
	},
};

// table refresh
function clear_item_details() {
	$("#item-detail-container").remove();
	$(".view-btn").removeClass("active-detail");
}

// EXCEL download current item details in Excel
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

// EXCEL download full report both summary and detail tables in Excel with two defferent sheet for detail and summary
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


// ── Nesting Report Modal ──
// ✅ NEW FUNCTION: Nesting Report Modal
// "Nesting Report" button click karne par ye open hota hai

function show_nesting_report_modal(item, project, item_display_name) {

	$("#nesting-report-modal-overlay").remove();

	let modal_html = `
	<div id="nesting-report-modal-overlay" style="
		position:fixed; top:0; left:0; width:100%; height:100%;
		background:rgba(0,0,0,0.55); z-index:9999;
		display:flex; align-items:center; justify-content:center;">
 
		<div style="
			background:#fff; border-radius:10px; padding:28px;
			width:740px; max-width:95vw; max-height:92vh;
			overflow-y:auto; box-shadow:0 12px 48px rgba(0,0,0,0.35);
			position:relative;">
 
			<!-- Header -->
			<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:22px;">
				<h4 style="margin:0; color:#1a1a2e; font-size:16px;">
					🔩 Nesting Report &nbsp;—&nbsp;
					<span style="color:#4361ee;">${item_display_name}</span>
				</h4>
				<button id="close-nesting-modal" style="
					background:#e63946; color:#fff; border:none;
					border-radius:5px; padding:5px 14px; cursor:pointer; font-size:14px; font-weight:600;">
					✕ Close
				</button>
			</div>
 
			<!-- STEP 1: Upload Result JSON -->
			<div style="
				background:#f0f4ff; border:1px solid #c8d3f5;
				border-radius:8px; padding:16px; margin-bottom:16px;">
 
				<p style="font-weight:700; color:#2d3a8c; margin-bottom:6px; font-size:14px;">
					📂 Step 1 — Nesting Center ka Result JSON upload karo
				</p>
				<p style="font-size:12px; color:#666; margin-bottom:10px;">
					Nesting Center mein JSON load karke Run karo, phir result/output JSON file yahan upload karo
				</p>
				<div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
					<input type="file" id="nesting-result-json" accept=".json"
						style="border:1px solid #bbb; padding:5px 8px; border-radius:5px;
						font-size:13px; flex:1; min-width:200px; background:#fff;">
					<button id="parse-nesting-json" style="
						background:#4361ee; color:#fff; border:none; border-radius:5px;
						padding:7px 16px; cursor:pointer; font-size:13px; font-weight:600; white-space:nowrap;">
						📊 Parse & Show
					</button>
				</div>
			</div>
 
			<!-- Stats Cards -->
			<div id="nesting-stats-area" style="display:none;
				background:#fff; border:2px solid #4361ee;
				border-radius:8px; padding:18px; margin-bottom:16px;">
 
				<p style="font-weight:700; color:#4361ee; font-size:14px; margin-bottom:14px;">
					✅ Nesting Results
				</p>
 
				<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:14px;">
					<div style="background:#e8f4fd; border-radius:8px; padding:14px; text-align:center;">
						<div style="font-size:11px; color:#666; margin-bottom:4px; text-transform:uppercase; letter-spacing:.5px;">Sheets</div>
						<div id="stat-sheets" style="font-size:28px; font-weight:800; color:#1a73e8;">—</div>
					</div>
					<div style="background:#e8fdf4; border-radius:8px; padding:14px; text-align:center;">
						<div style="font-size:11px; color:#666; margin-bottom:4px; text-transform:uppercase; letter-spacing:.5px;">Nested Parts</div>
						<div id="stat-nested-parts" style="font-size:28px; font-weight:800; color:#0f9d58;">—</div>
					</div>
					<div style="background:#fdecea; border-radius:8px; padding:14px; text-align:center;">
						<div style="font-size:11px; color:#666; margin-bottom:4px; text-transform:uppercase; letter-spacing:.5px;">Scrap</div>
						<div id="stat-scrap" style="font-size:28px; font-weight:800; color:#e63946;">—</div>
					</div>
				</div>
 
				<!-- Per-Sheet Breakdown Table -->
				<div id="sheet-breakdown" style="display:none;">
					<p style="font-weight:600; color:#333; margin-bottom:8px; font-size:13px;">Per Sheet Breakdown:</p>
					<table class="table table-bordered table-sm" style="font-size:13px;">
						<thead style="background:#f0f4ff;">
							<tr>
								<th style="text-align:center; width:40px;">#</th>
								<th>Sheet Name</th>
								<th style="text-align:center;">Scrap %</th>
								<th style="text-align:center;">Parts</th>
							</tr>
						</thead>
						<tbody id="sheet-breakdown-rows"></tbody>
					</table>
				</div>
			</div>
 
			<!-- Manual Entry (toggle) -->
			<div id="manual-stats-area" style="display:none;
				background:#fffbf0; border:1px dashed #f0a500;
				border-radius:8px; padding:16px; margin-bottom:16px;">
 
				<p style="font-weight:700; color:#b45309; margin-bottom:10px; font-size:13px;">
					✏️ Manually stats enter karo:
				</p>
				<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px;">
					<div>
						<label style="font-size:12px; color:#555; display:block; margin-bottom:3px;">Sheets</label>
						<input type="text" id="manual-sheets" class="form-control form-control-sm" placeholder="3">
					</div>
					<div>
						<label style="font-size:12px; color:#555; display:block; margin-bottom:3px;">Nested Parts</label>
						<input type="text" id="manual-nested-parts" class="form-control form-control-sm" placeholder="3/6">
					</div>
					<div>
						<label style="font-size:12px; color:#555; display:block; margin-bottom:3px;">Scrap %</label>
						<input type="text" id="manual-scrap" class="form-control form-control-sm" placeholder="17.51%">
					</div>
				</div>
				<button id="apply-manual-stats" style="
					margin-top:12px; background:#f59e0b; color:#fff; border:none;
					border-radius:5px; padding:6px 18px; cursor:pointer; font-size:13px; font-weight:600;">
					✅ Apply
				</button>
			</div>
 
			<!-- STEP 2: Upload PDF Report -->
			<div style="
				background:#f0fff4; border:1px solid #a3d9a5;
				border-radius:8px; padding:16px; margin-bottom:14px;">
 
				<p style="font-weight:700; color:#155724; margin-bottom:6px; font-size:14px;">
					📄 Step 2 — Nesting Center PDF Report upload karo
				</p>
				<p style="font-size:12px; color:#666; margin-bottom:10px;">
					Nesting Center → Run complete → "Report" button dabao → PDF download karo → yahan upload karo
				</p>
				<input type="file" id="nesting-pdf-upload" accept=".pdf"
					style="border:1px solid #bbb; padding:5px 8px; border-radius:5px;
					font-size:13px; width:100%; background:#fff;">
 
				<div id="pdf-viewer-area" style="margin-top:14px; display:none;">
					<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
						<span style="font-weight:600; color:#155724; font-size:13px;">📋 PDF Report Preview:</span>
						<a id="pdf-download-link" href="#" download="Nesting_Report.pdf" style="
							background:#198754; color:#fff; border:none; border-radius:5px;
							padding:5px 14px; font-size:13px; font-weight:600; text-decoration:none;">
							⬇ Download PDF
						</a>
					</div>
					<iframe id="nesting-pdf-frame"
						style="width:100%; height:480px; border:1px solid #ccc; border-radius:6px;">
					</iframe>
				</div>
			</div>
		</div>
	</div>
	`;

	$("body").append(modal_html);

	// Close on overlay click or close button
	$("#close-nesting-modal").on("click", function () {
		$("#nesting-report-modal-overlay").remove();
	});
	$("#nesting-report-modal-overlay").on("click", function (e) {
		if (e.target.id === "nesting-report-modal-overlay") {
			$("#nesting-report-modal-overlay").remove();
		}
	});

	// Toggle manual entry
	$("#toggle-manual-entry").on("click", function () {
		$("#manual-stats-area").toggle();
	});

	// Parse JSON button
	$("#parse-nesting-json").on("click", function () {
		let file = document.getElementById("nesting-result-json").files[0];
		if (!file) { frappe.msgprint("Pehle JSON file select karo!"); return; }

		let reader = new FileReader();
		reader.onload = function (e) {
			try {
				let json = JSON.parse(e.target.result);
				parse_nesting_result_json(json);
			} catch (err) {
				frappe.msgprint("JSON parse karne mein error aaya. Manually enter karo.");
				$("#manual-stats-area").show();
				console.error("JSON parse error:", err);
			}
		};
		reader.readAsText(file);
	});

	// Apply manual stats
	$("#apply-manual-stats").on("click", function () {
		$("#stat-sheets").text($("#manual-sheets").val() || "—");
		$("#stat-nested-parts").text($("#manual-nested-parts").val() || "—");
		$("#stat-scrap").text($("#manual-scrap").val() || "—");
		$("#nesting-stats-area").show();
		$("#manual-stats-area").hide();
		frappe.show_alert({ message: "Stats apply ho gaye!", indicator: "green" });
	});

	// PDF upload
	$("#nesting-pdf-upload").on("change", function () {
		let file = this.files[0];
		if (!file) return;
		let url = URL.createObjectURL(file);
		$("#nesting-pdf-frame").attr("src", url);
		$("#pdf-download-link").attr("href", url);
		$("#pdf-viewer-area").show();
		frappe.show_alert({ message: "PDF load ho gaya!", indicator: "green" });
	});
}

// ✅ NEW FUNCTION: Nesting Center result JSON parser
//    Multiple output formats handle karta hai

function parse_nesting_result_json(json) {

	let sheets = "—", nested_parts = "—", scrap = "—";
	let layouts = [];

	// Format 1: { Result: { Sheets, NestedParts, TotalParts, Scrap, ... } }
	if (json.Result) {
		let r = json.Result;
		sheets = r.Sheets || r.sheets || "—";
		let np_done = r.NestedParts || r.nested_parts || r.PartsNested || 0;
		let np_total = r.TotalParts || r.total_parts || r.Parts || 0;
		nested_parts = np_total ? `${np_done} / ${np_total}` : String(np_done);
		scrap = r.Scrap !== undefined ? `${parseFloat(r.Scrap).toFixed(2)}%` : "—";
		layouts = r.Layouts || r.layouts || [];
	}
	// Format 2: Flat { Sheets, NestedParts, ... }
	else if (json.Sheets !== undefined || json.sheets !== undefined) {
		sheets = json.Sheets || json.sheets || "—";
		let np_done = json.NestedParts || json.nested_parts || 0;
		let np_total = json.TotalParts || json.total_parts || 0;
		nested_parts = np_total ? `${np_done} / ${np_total}` : String(np_done);
		scrap = json.Scrap !== undefined ? `${parseFloat(json.Scrap).toFixed(2)}%` : "—";
		layouts = json.Layouts || json.layouts || [];
	}
	// Format 3: { Solution: { ... } }
	else if (json.Solution) {
		let s = json.Solution;
		sheets = s.NumberOfSheets || s.Sheets || "—";
		scrap = s.ScrapPercentage !== undefined ? `${parseFloat(s.ScrapPercentage).toFixed(2)}%` : "—";
		layouts = s.Layouts || s.Sheets_list || [];
	}
	else {
		frappe.msgprint("JSON format pehchana nahi gaya. Manually enter karo.");
		$("#manual-stats-area").show();
		return;
	}

	// Apply to stat cards
	$("#stat-sheets").text(sheets);
	$("#stat-nested-parts").text(nested_parts);
	$("#stat-scrap").text(scrap);
	$("#nesting-stats-area").show();

	// Per-sheet breakdown
	if (layouts && layouts.length) {
		let rows_html = "";
		layouts.forEach((layout, idx) => {
			let name = layout.Name || layout.RawPlateName || layout.name || `Sheet ${idx + 1}`;
			let s_pct = layout.Scrap !== undefined
				? `${parseFloat(layout.Scrap).toFixed(2)}%`
				: layout.ScrapPercentage !== undefined
					? `${parseFloat(layout.ScrapPercentage).toFixed(2)}%`
					: "—";
			let parts = layout.Parts || layout.NestedParts || layout.parts || "—";
			rows_html += `
				<tr>
					<td style="text-align:center;">${idx + 1}</td>
					<td>${name}</td>
					<td style="text-align:center;">${s_pct}</td>
					<td style="text-align:center;">${Array.isArray(parts) ? parts.length : parts}</td>
				</tr>`;
		});
		$("#sheet-breakdown-rows").html(rows_html);
		$("#sheet-breakdown").show();
	}

	frappe.show_alert({ message: "Nesting results parse ho gaye!", indicator: "green" });
}

// ── Nesting Report Modal ──
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

	overflow: visible;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    box-sizing: border-box;
}
.section-content-count {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}
.section-content-count p{
	font-size: 13px;
    font-weight: 400;
    color: #525252;
    margin: 0 0 4px 0;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: visible;
    text-align: center;
    width: 100%;
    line-height: 1.5;
}
.section-content-count span{
	font-size: 16px;
	font-weight: 600;
	line-height: 20px;
	padding-top: 4px;
    padding-bottom: 5px;
    color: #000;
    display: block;
    width: 100%;
    text-align: center;
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


