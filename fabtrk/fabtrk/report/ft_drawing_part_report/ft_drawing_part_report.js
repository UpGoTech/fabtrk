// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["FT Drawing Part Report"] = {

    onload(report) {

		frappe.query_report.set_filter_value("project_number", []);
		frappe.query_report.set_filter_value("drawing_number", []);
		frappe.query_report.set_filter_value("item", []);
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
            get_data: function (txt) {
                return frappe.db.get_link_options("FT Project", txt);
            }
        },
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
                return frappe.db.get_link_options("Add Drawing", txt, filters);
            }
        }, 
        {
            fieldname: "item",
            label: "Drawing Part",
            fieldtype: "MultiSelectList",
            get_data: function (txt) {

                let drawings = frappe.query_report.get_filter_value("drawing_number") || [];

                // CASE 1: No drawing selected → show all parts
                if (!drawings.length) {
                    return frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "FT Stock RM List",
                            fields: ["name", "computed_name"],
                            filters: [
                                ["computed_name", "like", "%" + txt + "%"]
                            ],
                            // limit_page_length: 50
                        }
                    }).then(r => {
                        return (r.message || []).map(d => ({
                            value: d.name,
                            label: `${d.computed_name}`,
                            description: "",
                        }));
                    });
                }

                // CASE 2: Drawing selected → show only its parts
                return frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Drawing Parts",
                        fields: ["item"],
                        filters: [
                            ["drawing_number", "in", drawings]
                        ],
                        // limit_page_length: 200
                    }
                }).then(r => {

                    let unique_items = [...new Set((r.message || []).map(d => d.item))];

                    if (!unique_items.length) {
                        return [];
                    }

                    return frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "FT Stock RM List",
                            fields: ["name", "computed_name"],
                            filters: [
                                ["name", "in", unique_items],
                                ["computed_name", "like", "%" + txt + "%"]
                            ],
                            // limit_page_length: 50
                        }
                    }).then(res => {
                        return (res.message || []).map(d => ({
                            value: d.name,
                            label: `${d.computed_name}`,
                            description: "",
                        }));
                    });

                });
            }
        },
        {
            fieldname: "is_active",
            label: "Is Active",
            fieldtype: "Check",
            default: 1
        }
    ],

    after_datatable_render(report) {

        $(report.wrapper)
            .off("click", ".view-btn")
            .on("click", ".view-btn", function () {

                let drawing_id = $(this).data("drawing-id");

                if (!drawing_id) {
                    frappe.msgprint("Drawing not found");
                    return;
                }

                frappe.call({
                    method: "fabtrk.fabtrk.report.ft_drawing_part_report.ft_drawing_part_report.get_drawing_part_details",
                    args: { drawing_id: drawing_id },
                    callback: function (r) {

                        if (!r.message || !r.message.length) {
                            frappe.msgprint("No Drawing Parts Found");
                            return;
                        }

                        $("#drawing-detail-container").remove();

                        let rows = "";

                        r.message.forEach(d => {
                            rows += `
                                <tr>
                                    <td>${d.position_no || ""}</td>
                                    <td>${d.drawing_number || ""}</td>
                                    <td>${d.item_name || ""}</td>
                                    <td>${d.quantity || 0}</td>
                                    <td>${d.single_weight || 0}</td>
                                    <td>${d.lenght || ""}</td>
                                    <td>${d.breath || ""}</td>
                                    <td>${d.total_weight || 0}</td>
                                </tr>
                            `;
                        });

                        let html = `
                            <div id="drawing-detail-container" 
                                style="margin-top:20px; padding:20px; border:1px solid #ddd; ">

                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <h4>Drawing Part Details</h4>
                                    <button class="btn btn-xs btn-danger close-view">
                                        Close
                                    </button>
                                </div>

                                <table class="table table-bordered" style="margin-top:15px;">
                                    <tr>
                                        <th>Position No.</th>
                                        <th>Drawing Number</th>
                                        <th>Item</th>
                                        <th>Quantity</th>
                                        <th>Single Weight</th>
                                        <th>Length</th>
                                        <th>Breadth</th>
                                        <th>Total Weight</th>
                                    </tr>
                                    ${rows}
                                </table>
                            </div>
                        `;

                        $(report.wrapper).find(".datatable").after(html);

                        $(".close-view").on("click", function () {
                            $("#drawing-detail-container").remove();
                        });

                    }
                });

            });
    }
};


