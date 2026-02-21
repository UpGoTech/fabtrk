// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt


// # this code for multi select filter filed
frappe.query_reports["FT Drawing Report 2"] = {

	onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("is_active", 1);

		// Add Buttons
		report.page.add_inner_button("Download Drawings", function () {
			download_csv(report);
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
                value = String(value).replace(/"/g, '""'); 
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

