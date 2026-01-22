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
				$("#details_area").html("");   // 🔥 clear old view data
			}
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "FT Project",
			on_change() {
				frappe.query_report.refresh();
				$("#details_area").html("");   // 🔥 clear old view data
			}
		}
	],
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

function refresh_project_details(month) {
	console.log("YEAR 👉", frappe.query_report.get_filter_value("year"));
	console.log("MONTH 👉", month); // FT Monthly Target.name

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
            <h4>Monthly Project Details</h4>
            <button id="close_details" class="btn btn-xs btn-danger">Close</button>
        </div>

        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Project No</th>
                    <th>Project Name</th>
                    <th>Customer</th>
                    <th>Description</th>

                    <th>Target (Kg)</th>
                    <th>Achieved (Kg)</th>
                    <th>Balance (Kg)</th>

                    <th>Achievement Type</th>

                    <th>Invoice No</th>
                    <th>Invoice Weight</th>
                    <th>Invoice Amount</th>
                    <th>Attachment</th>
                </tr>
            </thead>
            <tbody>
    `;

	data.forEach(d => {
		let attach = d.attach_file
			? `<a href="${d.attach_file}" target="_blank">Open</a>`
			: "-";

		html += `
            <tr>
                <td>${d.project_number}</td>
                <td>${d.project_name || ""}</td>
                <td>${d.customer_name || ""}</td>
                <td>${d.description || ""}</td>

                <td>${d.target_weight || 0}</td>
                <td>${d.achieved_weight || 0}</td>
                <td>${d.balance_weight || 0}</td>

				<td>${d.target_weight ? ((d.achieved_weight / d.target_weight) * 100).toFixed(2) : 0}%</td>

                <td>${d.achievement_type || ""}</td>

                <td>${d.invoice_no || ""}</td>
                <td>${d.invoice_weight || ""}</td>
                <td>${d.invoice_amount || ""}</td>
                <td>${attach}</td>
            </tr>`;
	});

	html += "</tbody></table>";

	$("#details_area").html(html).show();

	$("#close_details").on("click", () => $("#details_area").hide());
}
