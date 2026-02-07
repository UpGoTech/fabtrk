// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt


frappe.query_reports["FT Drawing Report"] = {
	onload(report) {
		// page refresh / first load pe filters clear karo
		frappe.query_report.set_filter_value("project_number", "");
		frappe.query_report.set_filter_value("drawing_number", "");
		frappe.query_report.set_filter_value("item", "");

		// optional: table bhi reset
		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);

		hide_view_table();
	},
	

	filters: [
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "Link",
			options: "FT Project",
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", "");
				frappe.query_report.set_filter_value("item", "");

				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);

				hide_view_table();
			}
		},
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "Link",
			options: "Add Drawing",
			get_query() {
				return {
					filters: {
						project_number: frappe.query_report.get_filter_value("project_number")
					}
				};
			},
			// on_change() {
			// 	frappe.query_report.refresh();
			// 	hide_view_table();
			// }
			on_change() {
				frappe.query_report.set_filter_value("item", "");

				setTimeout(() => {
					frappe.query_report.refresh();
				}, 100);

				hide_view_table();
			}

		},
		{
			fieldname: "item",
			label: "Drawing Part",
			fieldtype: "Link",
			options: "FT Stock RM List",
			on_change() {
				frappe.query_report.refresh();
				hide_view_table();
			}
		}
	],

	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "view" && data?.drawing_number) {
			return `
				<button class="btn btn-xs btn-primary view-drawing"
					data-drawing="${data.drawing_number}">
					View
				</button>
			`;
		}
		return default_formatter(value, row, column, data);
	},

	after_datatable_render(report) {
		$(".view-drawing").off("click").on("click", function () {
			let drawing = $(this).data("drawing");

			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Add Drawing",
					name: drawing
				},
				callback(r) {
					if (!r.message) return;

					let d = r.message;

					let html = `
						<div id="drawing-detail-container" style="margin-top:30px;">
							<div style="display:flex;justify-content:space-between;align-items:center;">
								<h4>Drawing Details</h4>
								<button class="btn btn-xs btn-danger close-view">
									Close
								</button>
							</div>

							<table class="table table-bordered" style="margin-top:10px;">
								<tr>
									<th>Project Number</th>
									<th>Drawing Number</th>
									<th>Quantity</th>
									<th>Unit Weight</th>
									<th>Total Weight</th>
								</tr>
								<tr>
									<td>${d.project_number || ""}</td>
									<td>${d.name}</td>
									<td>${d.quantity || 0}</td>
									<td>${d.unit_weight || 0}</td>
									<td>${d.total_weight || 0}</td>
								</tr>								
							</table>
						</div>
					`;

					hide_view_table();
					$(".datatable").after(html);

					$(".close-view").on("click", function () {
						hide_view_table();
					});
				}
			});
		});
	},


};

// ---------- COMMON FUNCTION ----------
function hide_view_table() {
	$("#drawing-detail-container").remove();
}
