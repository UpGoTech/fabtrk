// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt

// frappe.query_reports["FT Transaction"] = {
// 	"filters": [

// 	]
// };




frappe.query_reports["FT Transaction"] = {
	onload(report) {
		frappe.query_report.set_filter_value("project_number", "");
		frappe.query_report.set_filter_value("stages", "");
	},

	filters: [
		// ---------------- PROJECT ----------------
		{
			fieldname: "project_number",
			label: "Project",
			fieldtype: "Link",
			options: "FT Project Stages",
			on_change() {
				frappe.query_report.set_filter_value("stages", "");
				frappe.query_report.refresh();
			}
		},

		// ---------------- STAGES ----------------
		{
			fieldname: "stages",
			label: "Stages",
			fieldtype: "Link",
			options: "FT Stages Master",
			on_change() {
				frappe.query_report.refresh();
			}
		}
	],

	// ── Click on Project or Stage header → set filter & refresh ──
	after_datatable_render(report) {
		// Project cell click → filter set karo
		$(report.wrapper)
			.off("click", ".project-link")
			.on("click", ".project-link", function () {
				let project = $(this).data("project");
				if (project) {
					frappe.query_report.set_filter_value("project_number", project);
					frappe.query_report.refresh();
				}
			});

		// Stage cell click → filter set karo
		$(report.wrapper)
			.off("click", ".stage-link")
			.on("click", ".stage-link", function () {
				let stage = $(this).data("stage");
				if (stage) {
					frappe.query_report.set_filter_value("stages", stage);
					frappe.query_report.refresh();
				}
			});
	},

	// formatter(value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);

	// 	// TOTAL row bold styling
	// 	if (data && data.is_total) {
	// 		return `<span style="font-weight:700; background:#f0f4ff;">${value}</span>`;
	// 	}

	// 	// Project column — clickable link style
	// 	if (column.fieldname === "project_number" && data && data.project_number) {
	// 		return `<span class="project-link" data-project="${data.project_number}"
	// 					style="color:#1F4E79; font-weight:600; cursor:pointer;
	// 				">
	// 					${data.project_number}
	// 				</span>`;
	// 	}

	// 	// Stage column — clickable link style
	// 	if (column.fieldname === "stage" && data && data.stage) {
	// 		return `<span class="stage-link" data-stage="${data.stage}"
	// 					style="color:#0c5c70; font-weight:600; cursor:pointer;
	// 				">
	// 					${data.stage}
	// 				</span>`;
	// 	}

	// 	// Balance column — color coding
	// 	if (column.fieldname === "balance" && data) {
	// 		let val = parseFloat(data.balance || 0);
	// 		let color = val > 0 ? "#1a7abf" : val < 0 ? "#c00000" : "#555";
	// 		return `<span style="font-weight:700; color:${color};">${val}</span>`;
	// 	}

	// 	// Available column styling
	// 	if (column.fieldname === "available" && data) {
	// 		return `<span style="font-weight:600; color:#155724;">${value}</span>`;
	// 	}

	// 	return value;
	// }
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// TOTAL row bold styling
		if (data && data.is_total) {
			return `<span style="font-weight:700; background:#f0f4ff;">${value}</span>`;
		}

		// Project column — clickable link style
		if (column.fieldname === "project_number" && data && data.project_number) {
			return `<span class="project-link" data-project="${data.project_number}"
                    style="cursor:pointer;">
                    ${data.project_number}
                </span>`;
		}

		// Stage column — clickable link style
		if (column.fieldname === "stage" && data && data.stage) {
			return `<span class="stage-link" data-stage="${data.stage}"
                    style="cursor:pointer;">
                    ${data.stage}
                </span>`;
		}

		return value;
	}
};

