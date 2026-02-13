// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Drawing Part Report"] = {
	onload(report) {
		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("drawing_part", []);
		frappe.query_report.set_filter_value("is_active", 1);

		setTimeout(() => {
			frappe.query_report.refresh();
		}, 100);
	},

	filters: [
		{
			fieldname: "project_number",
			label: "Project Number",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options("FT Project", txt);
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_number", []);
				frappe.query_report.set_filter_value("drawing_part", []);
				setTimeout(() => frappe.query_report.refresh(), 100);
			}
		},
		{
			fieldname: "drawing_number",
			label: "Drawing Number",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				let projects = frappe.query_report.get_filter_value("project_number") || [];
				let filters = {};
				if (projects.length) filters.project_number = ["in", projects];
				return frappe.db.get_link_options("Add Drawing", txt, filters);
			},
			on_change() {
				frappe.query_report.set_filter_value("drawing_part", []);
				setTimeout(() => frappe.query_report.refresh(), 100);
			}
		},
		{
			fieldname: "drawing_part",
			label: "Drawing Part",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				let drawings = frappe.query_report.get_filter_value("drawing_number") || [];
				let filters = {};
				if (drawings.length) filters.drawing_number = ["in", drawings];
				return frappe.db.get_link_options("Drawing Part", txt, filters);
			},
			on_change() {
				setTimeout(() => frappe.query_report.refresh(), 100);
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
        // Delegate event on datatable wrapper for all buttons with class view-btn
        $(report.wrapper).off('click', '.view-btn').on('click', '.view-btn', function() {
            let drawing_part = $(this).data('drawing-part');
            let project = $(this).data('project');

            // For example, open the DocType form for Drawing Part in a new window
            let route = frappe.router.url('Form', 'Drawing Part', drawing_part);
            window.open(route, '_blank');
        });
    }
};



