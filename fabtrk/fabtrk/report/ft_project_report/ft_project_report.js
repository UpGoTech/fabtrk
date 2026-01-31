// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt



frappe.query_reports["FT Project Report"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Link",
			options: "FT Year",
			on_change() {
				frappe.query_report.refresh();
				$("#details_area").html("");
			}
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "FT Project",
			on_change() {
				frappe.query_report.refresh();
				$("#details_area").html("");
			}
		}
	],

	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "view") {
			return `<button class="btn btn-xs btn-primary view-btn" data-month="${data.month_id}">View</button>`;
		}

		if (["target", "achieved", "balance"].includes(column.fieldname)) {
			value = value ? value.toLocaleString() : 0;
		}

		// New Achieved % color logic
		if (column.fieldname === "achieved_percent") {
			let cls = "text-danger"; // <50%
			if (value == 100) cls = "text-info";
			else if (value >= 75) cls = "text-success";
			else if (value >= 50) cls = "text-warning";
			value = `<span class="${cls}">${value}%</span>`;
		}

		return default_formatter(value, row, column, data);
	},
	
	onload(report) {
		// ✅ 1️⃣ TOP BUTTON (Fabtrk Workspace)
		report.page.add_inner_button(__("Go to Fabtrk Workspace"), () => {
			frappe.set_route("Workspaces", "Fabtrk");
		});

		if (!$("#details_area").length) {
			$('<div id="details_area" style="margin-top:20px;"></div>').appendTo(frappe.query_report.page.main);
		}

		$(document).on("click", ".view-btn", function () {
			refresh_project_details($(this).data("month"));
		});
	},

};

function fmt(num) {
	return num ? num.toLocaleString() : 0;
}


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
				// month_display ko pass kar rahe hain
				render_details(r.message, r.message[0].month_display || month);
			} else {
				$("#details_area").html("<b>No data found</b>");
			}
		}
	});
}


function render_details(data, month_display) {
	let html = `
        <div style="display:flex;justify-content:space-between">
            <h4>Monthly Project Details - ${month_display}</h4>
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
                    <th>Achieved %</th>

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
		let attach = d.attach_file ? `<a href="${d.attach_file}" target="_blank">Open</a>` : "-";

		let perc = d.target_weight ? ((d.achieved_weight / d.target_weight) * 100).toFixed(2) : 0;

		// Bootstrap class logic
		let cls = "text-danger"; // <50%
		if (perc == 100) cls = "text-info";
		else if (perc >= 75) cls = "text-success";
		else if (perc >= 50) cls = "text-warning";

		html += `
            <tr>
                <td>${d.project_number}</td>
                <td>${d.project_name || ""}</td>
                <td>${d.customer_name || ""}</td>
                <td>${d.description || ""}</td>

                <td>${fmt(d.target_weight)}</td>
                <td>${fmt(d.achieved_weight)}</td>
                <td>${fmt(d.balance_weight)}</td>
                <td class="${cls}">${perc}%</td>

                <td>${d.achievement_type || ""}</td>

                <td>${d.invoice_no || ""}</td>
                <td>${fmt(d.invoice_weight)}</td>
                <td>${fmt(d.invoice_amount)}</td>
                <td>${attach}</td>
            </tr>`;
	});

	html += "</tbody></table>";

	$("#details_area").html(html).show();

	$("#close_details").on("click", () => $("#details_area").hide());
}


