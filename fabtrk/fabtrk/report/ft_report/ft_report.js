// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt


frappe.query_reports["FT Report"] = {
    filters: [
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Link",
            options: "FT Year"
        }
    ],

    // formatter: function (value, row, column, data, default_formatter) {
    //     if (column.fieldname === "view") {
    //         return `<a href="/app/query-report/FT Project Report?year=${data.year}">
    //                     View
    //                 </a>`;
    //     }
    //     return default_formatter(value, row, column, data);
    // }

    onload: function (report) {
        // Event delegation (VERY IMPORTANT)
        report.page.wrapper.on("click", ".view-details", function () {
            const year = $(this).data("year");
            const $row = $(this).closest("tr");

            // Toggle
            if ($row.next().hasClass("detail-row")) {
                $row.next().remove();
                return;
            }

            frappe.call({
                method: "fabtrk.fabtrk.report.ft_report.ft_report.get_year_wise_project_data",
                args: { year },
                callback: function (r) {
                    let html = `
                        <tr class="detail-row">
                            <td colspan="5">
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Project No</th>
                                            <th>Project Name</th>
                                            <th>Customer</th>
                                            <th>Achieved Weight</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;

                    if (r.message && r.message.length) {
                        r.message.forEach(row => {
                            html += `
                                <tr>
                                    <td>${row.project_number || ""}</td>
                                    <td>${row.project_name || ""}</td>
                                    <td>${row.customer_name || ""}</td>
                                    <td>${row.total_weight_for_project_achieve || 0}</td>
                                </tr>
                            `;
                        });
                    } else {
                        html += `
                            <tr>
                                <td colspan="4" class="text-center text-muted">
                                    No Data Found
                                </td>
                            </tr>
                        `;
                    }

                    html += `
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    `;

                    $row.after(html);
                }
            });
        });
    },

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "view") {
            return `
                <button class="btn btn-xs btn-primary view-details"
                    data-year="${data.year}">
                    View
                </button>
            `;
        }
        return value;
    }
};
window.show_details = function (year, btn) {
    const $row = $(btn).closest("tr");

    // Toggle behavior
    if ($row.next().hasClass("detail-row")) {
        $row.next().remove();
        return;
    }

    frappe.call({
        method: "fabtrk.fabtrk.report.ft_report.ft_report.get_year_wise_project_data",
        args: { year },
        callback: function (r) {
            let html = `
                <tr class="detail-row">
                    <td colspan="5">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Project No</th>
                                    <th>Project Name</th>
                                    <th>Customer</th>
                                    <th>Achieved Weight</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            if (r.message && r.message.length) {
                r.message.forEach(row => {
                    html += `
                        <tr>
                            <td>${row.project_number || ""}</td>
                            <td>${row.project_name || ""}</td>
                            <td>${row.customer_name || ""}</td>
                            <td>${row.total_weight_for_project_achieve || 0}</td>
                        </tr>
                    `;
                });
            } else {
                html += `
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            No Data Found
                        </td>
                    </tr>
                `;
            }

            html += `
                            </tbody>
                        </table>
                    </td>
                </tr>
            `;

            $row.after(html);
        }
    });
};
