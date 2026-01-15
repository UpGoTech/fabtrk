// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt




frappe.query_reports["FT Project Report"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Link",
			options: "FT Year",
			on_change() {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "FT Project",
			on_change() {
				frappe.query_report.refresh();
			}
		}
	],

	// formatter(value, row, column, data, default_formatter) {
	//     if (column.fieldname === "view") {
	//         return `<button class="btn btn-xs btn-primary view-btn"
	//                 data-month="${data.month_raw}">
	//                 View
	//             </button>`;
	//     }
	//     return default_formatter(value, row, column, data);
	// },
	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "view") {
			console.log("MONTH ID 👉", data.month_id);
			return `
            <button class="btn btn-xs btn-primary view-btn"
                data-month="${data.month_id}">
                View
            </button>`;
		}
		return default_formatter(value, row, column, data);
	}
	,

	onload() {
		if (!$("#details_area").length) {
			$('<div id="details_area" style="margin-top:20px;"></div>')
				.appendTo(frappe.query_report.page.main);
		}

		$(document).on("click", ".view-btn", function () {
			refresh_project_details($(this).data("month"));
		});
	}
};

// function refresh_project_details(month = null) {
// 	frappe.call({
// 		method: "testapp.testapp.report.individual_project_report.individual_project_report.get_month_details",
// 		args: {
// 			year: frappe.query_report.get_filter_value("year"),
// 			project: frappe.query_report.get_filter_value("project"),
// 			month: month
// 		},
// 		callback(r) {
// 			if (r.message?.length) {
// 				render_details(r.message);
// 			} else {
// 				$("#details_area").html("<b>No data found</b>");
// 			}
// 		}
// 	});
// }
function refresh_project_details(month) {
	frappe.call({
		method: "fabtrk.fabtrk.report.ft_project_report.ft_project_report.get_month_details",
		args: {
			year: frappe.query_report.get_filter_value("year"),
			project: frappe.query_report.get_filter_value("project"),
			month: month
		},
		callback(r) {
			if (r.message && r.message.length) {
				render_details(r.message);
			} else {
				$("#details_area").html("<b>No data found</b>");
			}
		}
	});
}


function render_details(data) {
	let html = `
        <div style="display:flex;justify-content:space-between">
            <h4>Project Details</h4>
            <button id="close_details" class="btn btn-xs btn-danger">Close</button>
        </div>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Target (Kg)</th>
                    <th>Achieved (Kg)</th>
                    <th>Balance</th>
                    <th>Invoice</th>
                    <th>Attach</th>
                </tr>
            </thead>
            <tbody>
    `;

	data.forEach(d => {
		let attach = d.attachment
			? `<a href="${d.attachment}" target="_blank">Open</a>`
			: "-";

		html += `
            <tr>
                <td>${d.project}</td>
                <td>${d.target || 0}</td>
                <td>${d.achieved || 0}</td>
                <td>${d.balance || 0}</td>
                <td>${d.invoice_no || ""}</td>
                <td>${attach}</td>
            </tr>`;
	});

	html += "</tbody></table>";
	$("#details_area").html(html).show();

	$("#close_details").on("click", () => $("#details_area").hide());
}

