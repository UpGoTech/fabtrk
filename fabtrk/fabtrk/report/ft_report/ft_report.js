// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt


// ================= GLOBAL =================
let CURRENT_YEAR = "";
let CURRENT_MONTH = "";

frappe.query_reports["FT Report"] = {
	"filters": [

		{
			fieldname: "year",
			label: "Year",
			fieldtype: "Int",
			reqd: 1,
			on_change: function () {
				let year = frappe.query_report.get_filter_value("year");
				$("#drilldown-container").html("");

				if (year) {
					CURRENT_YEAR = year;
					frappe.query_report.refresh();
					setTimeout(() => {
						load_month_data(year);
					}, 300);
				}
			}
		}
	],

	onload: function (report) {
		if (!$("#drilldown-container").length) {
			report.page.wrapper.append(
				`<div id="drilldown-container" style="margin-top:20px;"></div>`
			);
		}

		$(document).on("click", ".view-month", function () {
			let month = $(this).data("month");
			CURRENT_MONTH = month;
			load_project_data(CURRENT_YEAR, month);
		});

		$(document).on("click", ".view-project", function () {
			let project = $(this).data("project");
			load_project_entries(CURRENT_YEAR, CURRENT_MONTH, project);
		});
	}
};

// ================= LOAD MONTH DATA =================
function load_month_data(year) {
	frappe.call({
		method: "testapp.testapp.report.show_all_date_related_to_project_entry.show_all_date_related_to_project_entry.get_month_data",
		args: { year },
		callback(r) {
			render_month_table(r.message || [], year);
		}
	});
}

// ================= LOAD PROJECT DATA =================
function load_project_data(year, month) {
	frappe.call({
		method: "testapp.testapp.report.show_all_date_related_to_project_entry.show_all_date_related_to_project_entry.get_project_data",
		args: { year, month },
		callback(r) {
			render_project_table(r.message || [], month);
		}
	});
}

// ================= LOAD PROJECT ENTRIES =================
function load_project_entries(year, month, project) {
	frappe.call({
		method: "testapp.testapp.report.show_all_date_related_to_project_entry.show_all_date_related_to_project_entry.get_project_entries",
		args: { year, month, project },
		callback(r) {
			render_project_entry_table(r.message || [], project);
		}
	});
}

// ================= RENDER MONTH TABLE =================
function render_month_table(data, year) {

	let html = `
        <hr>
        <h4>Month Details - ${year}</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Target (MT)</th>
                    <th>Achieved (MT)</th>
                    <th>Balance</th>
                    <th>%</th>
                    <th>Entry</th>
                    <th>View</th>
                </tr>
            </thead>
            <tbody>
    `;

	data.forEach(d => {
		html += `
            <tr>
                <td>${d.month}</td>
                <td>${d.target || 0}</td>
                <td>${d.achieved || 0}</td>
                <td>${d.balance || 0}</td>
                <td>${(d.percent || 0).toFixed(1)}%</td>
                <td>${d.entry || 0}</td>
                <td>
                    <button class="btn btn-xs btn-secondary view-month"
                        data-month="${d.month}">
                        View
                    </button>
                </td>
            </tr>
        `;
	});

	html += `
            </tbody>
        </table>
        <div id="project-table-container"></div>
    `;

	$("#drilldown-container").html(html);
}

// ================= RENDER PROJECT TABLE =================
function render_project_table(data, month) {

	let html = `
        <h4>Project Details - ${month}</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Target (MT)</th>
                    <th>Achieved (MT)</th>
                    <th>Balance</th>
                    <th>No. of Entry</th>
                    <th>View</th>
                </tr>
            </thead>
            <tbody>
    `;

	data.forEach(d => {
		html += `
            <tr>
                <td>${d.project}</td>
                <td>${d.project_target || 0}</td>
                <td>${d.achieved || 0}</td>
                <td>${d.balance || 0}</td>
                <td>${d.entry_count || 0}</td>
                <td>
                    <button class="btn btn-xs btn-primary view-project"
                        data-project="${d.project}">
                        View
                    </button>
                </td>
            </tr>
        `;
	});

	html += `</tbody></table>
             <div id="project-entry-container"></div>`;

	$("#project-table-container").html(html);
}

// ================= RENDER PROJECT ENTRY TABLE =================
function render_project_entry_table(data, project) {

	let html = `
        <h5 style="margin-top:15px;">Project Entries - ${project}</h5>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Project</th>
                    <th>Description</th>
                    <th>Customer</th>
                    <th>Target</th>
                    <th>Achieved</th>
                    <th>Balance</th>
                </tr>
            </thead>
            <tbody>
    `;

	data.forEach(d => {
		html += `
            <tr>
                <td>${frappe.datetime.str_to_user(d.date)}</td>
                <td>${d.project}</td>
                <td>${d.project_description || ""}</td>
                <td>${d.customer || ""}</td>
                <td>${d.project_target || 0}</td>
                <td>${d.achieved || 0}</td>
                <td>${d.balance || 0}</td>
            </tr>
        `;
	});

	html += `</tbody></table>`;

	$("#project-entry-container").html(html);
}
