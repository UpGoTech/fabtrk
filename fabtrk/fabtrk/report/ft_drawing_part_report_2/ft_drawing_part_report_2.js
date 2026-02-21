

frappe.query_reports["FT Drawing Part Report 2"] = {

	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("item", []);
		frappe.query_report.set_filter_value("is_active", 1);

		// Add Buttons
		report.page.add_inner_button("Download Summary", function () {
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
			}
		},

		// ---------------- DRAWING ----------------
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let filters = {};

				if (projects.length) {
					filters.project_number = ["in", projects];
				}

				return frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Add Drawing",
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
			}
		},

		// ---------------- ITEM ----------------
		{
			fieldname: "item",
			label: "Drawing Part",
			fieldtype: "MultiSelectList",

			get_data: function (txt) {

				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

				// ---------------- CASE 1 ----------------
				// Nothing selected → show all items
				if (!projects.length && !drawings.length) {

					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "FT Stock RM List",
							fields: ["name", "computed_name"],
							filters: [["computed_name", "like", "%" + txt + "%"]]
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
							doctype: "Drawing Parts",
							fields: ["item"],
							filters: [["project_number", "in", projects]]
						}
					}).then(r => {

						let unique_items = [...new Set((r.message || []).map(d => d.item))];
						if (!unique_items.length) return [];

						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "FT Stock RM List",
								fields: ["name", "computed_name"],
								filters: [
									["name", "in", unique_items],
									["computed_name", "like", "%" + txt + "%"]
								]
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
				// Drawing selected → PROPER FIX
				if (drawings.length) {

					// Step 1: Get Add Drawing document names
					return frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Add Drawing",
							fields: ["name"],
							filters: [
								["drawing_number", "in", drawings]
							]
						}
					}).then(res => {

						let drawing_names = (res.message || []).map(d => d.name);
						if (!drawing_names.length) return [];

						// Step 2: Get items from Drawing Parts
						return frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "Drawing Parts",
								fields: ["item"],
								filters: [
									["drawing_number", "in", drawing_names]
								]
							}
						}).then(r => {

							let unique_items = [...new Set((r.message || []).map(d => d.item))];
							if (!unique_items.length) return [];

							return frappe.call({
								method: "frappe.client.get_list",
								args: {
									doctype: "FT Stock RM List",
									fields: ["name", "computed_name"],
									filters: [
										["name", "in", unique_items],
										["computed_name", "like", "%" + txt + "%"]
									]
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
			}
		},

		// ----------------- Section Type 
		{
			fieldname: "stock_rm_type",
			label: "Stock Rm Type",
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("FT Section Type", txt);
			},
			on_change() {
				frappe.query_report.refresh();
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
			}
		}

	],

	after_datatable_render(report) {

		$(report.wrapper)
			.off("click", ".view-btn")
			.on("click", ".view-btn", function () {

				let project = $(this).data("project");
				let item = $(this).data("item");

				if (!project || !item) {
					frappe.msgprint("No Data");
					return;
				}

				frappe.call({
					method: "fabtrk.fabtrk.report.ft_drawing_part_report_2.ft_drawing_part_report_2.get_item_details",
					args: {
						project: project,
						item: item
					},
					callback: function (r) {

						// if (!r.message || !r.message.length) {
						if (!r.message || !r.message.data || !r.message.data.length) {

							frappe.msgprint("No Details Found");
							return;
						}

						$("#item-detail-container").remove();

						let rows = "";
						let totalWeight = 0;

						// r.message.forEach(d => {
						r.message.data.forEach(d => {

							rows += `
								<tr>
									<td>${d.drawing_number}</td>
									<td>${d.quantity}</td>
									<td>${d.lenght}</td>
									<td>${d.width}</td>
									<td>${d.single_weight}</td>
									<td>${d.total_weight}</td>
								</tr>
							`;

							totalWeight += parseFloat(d.total_weight) || 0; 
						});

						let html = `
							<div id="item-detail-container"
								style="margin-top:20px; padding:20px; border:1px solid #ddd;">

								<div style="display:flex;justify-content:space-between;align-items:center;">
									<h4>Item Details - ${r.message.item_name}</h4>
									<div style="display:flex; gap:20px;">
										<button class="btn btn-xs btn-primary summary-download">
											Summary
										</button>
										<button class="btn btn-xs btn-danger close-view">
											Close
										</button>
									</div>
								</div>

								<table class="table table-bordered" style="margin-top:15px;">
									<tr>
										<th>Drawing</th>
										<th>Qty</th>
										<th>Length</th>
										<th>Width</th>
										<th>Single Weight</th>
										<th>Total Weight</th>
									</tr>
									${rows}
								</table>
							</div>
						`;

						$(report.wrapper).find(".datatable").after(html);

						$(".close-view").on("click", function () {
							$("#item-detail-container").remove();
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
// simple CSV download for the main summary table (without details)
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
// download both summary and detail tables in one CSV with clear separation and titles for each section
function download_full_report(report) {

    let rows = [];

    rows.push("Main Summary Table");
    // rows.push("");

    // Remove unwanted columns (like View button)
    let valid_columns = report.columns.filter(col => 
        col.fieldname && col.fieldname !== "view"
    );

    // Header row
    let headers = valid_columns.map(col => col.label);
    rows.push(headers.join(","));

    // Data rows (already filter based)
    report.data.forEach(row => {
        let rowData = valid_columns.map(col => {
            let value = row[col.fieldname] || "";
            return `"${String(value).replace(/"/g, '""')}"`;
        });
        rows.push(rowData.join(","));
    });

    rows.push("");
    // rows.push("");

    // ========================
    // Detail Table
    // ========================

    let detailTitle = $("#item-detail-container h4").text().trim();
    if (detailTitle) {
        rows.push(detailTitle);
        // rows.push("");
    }

    $("#item-detail-container table tr").each(function () {
        let cols = [];
        $(this).find("th, td").each(function () {
            cols.push(`"${$(this).text().trim().replace(/"/g, '""')}"`);
        });
        if (cols.length) {
            rows.push(cols.join(","));
        }
    });

    let csvContent = rows.join("\n");

    let blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    let url = URL.createObjectURL(blob);

    let link = document.createElement("a");
    link.href = url;
    link.download = "full_report.csv";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

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
	@media (min-width: 768px) and (max-width: 1023px) {
		.summary-container{
			grid-template-columns: repeat(2, 1fr) !important;
		}
	}
	@media (min-width: 1024px) {
		.summary-container{
			grid-template-columns: repeat(3, 1fr) !important;
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
</style>`).appendTo("head");


















