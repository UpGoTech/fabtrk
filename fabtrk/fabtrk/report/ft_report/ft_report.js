// // // // Copyright (c) 2026, UpGo Technologies and contributors
// // // // For license information, please see license.txt


// frappe.query_reports["FT Report"] = {
//     filters: [
//         {
//             fieldname: "year",
//             label: __("Year"),
//             fieldtype: "Link",
//             options: "FT Year"
//         }
//     ],

//     onload: function (report) {

//         // container for detail table
//         report.page.wrapper.append(`
//             <div id="ft-detail-container" style="margin-top:25px;"></div>
//         `);

//         // 🔥 VIEW BUTTON CLICK
//         report.page.wrapper.on("click", ".ft-view-btn", function () {
//             let year = $(this).data("year");

//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_year_wise_project_data",
//                 args: { year: year },
//                 callback: function (r) {

//                     let html = `
//                         <div class="card">
//                             <div class="card-body">
//                                 <h4>Project Details - ${year}</h4>
//                                 <table class="table table-bordered table-striped">
//                                     <thead>
//                                         <tr>
//                                             <th>Project No</th>
//                                             <th>Project Name</th>
//                                             <th>Customer</th>
//                                             <th>Achieved Weight</th>
//                                         </tr>
//                                     </thead>
//                                     <tbody>
//                     `;

//                     if (r.message && r.message.length) {
//                         r.message.forEach(d => {
//                             html += `
//                                 <tr>
//                                     <td>${d.project_number || ""}</td>
//                                     <td>${d.project_name || ""}</td>
//                                     <td>${d.customer_name || ""}</td>
//                                     <td class="text-end">
//                                         ${d.total_weight_for_project_achieve || 0}
//                                     </td>
//                                 </tr>
//                             `;
//                         });
//                     } else {
//                         html += `
//                             <tr>
//                                 <td colspan="4" class="text-center">
//                                     No Data Found
//                                 </td>
//                             </tr>
//                         `;
//                     }

//                     html += `
//                                     </tbody>
//                                 </table>
//                             </div>
//                         </div>
//                     `;

//                     $("#ft-detail-container").html(html);
//                 }
//             });
//         });
//     }
// };



// # ///////////////////////////////21-01-26
// frappe.query_reports["FT Report"] = {
//     filters: [
//         { fieldname: "year", label: __("Year"), fieldtype: "Link", options: "FT Year" }
//     ],

//     onload(report) {
//         report.page.wrapper.append(`<div id="ft-detail-container" style="margin-top:25px;"></div>`);

//         // YEAR → MONTH
//         report.page.wrapper.on("click", ".ft-view-btn", function () {
//             let year = $(this).data("year");

//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_month_wise_data",
//                 args: { year },
//                 callback(r) {
//                     let html = `<h4>Month Details - ${year}</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Month</th><th>Total</th><th>Achieved</th><th>Balance</th><th>%</th><th>View</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         let bal = d.total_weight - d.achieved_weight;
//                         let per = d.total_weight ? ((d.achieved_weight / d.total_weight) * 100).toFixed(1) : 0;

//                         html += `<tr>
//                             <td>${d.month}</td>
//                             <td>${d.total_weight}</td>
//                             <td>${d.achieved_weight}</td>
//                             <td>${bal}</td>
//                             <td>${per}%</td>
//                             <td>
//                                 <button class="btn btn-xs btn-info ft-month-view"
//                                     data-year="${year}"
//                                     data-month="${d.month_no}">
//                                     View
//                                 </button>
//                             </td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });

//         // MONTH → PROJECT
//         report.page.wrapper.on("click", ".ft-month-view", function () {
//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_wise_data",
//                 args: {
//                     year: $(this).data("year"),
//                     month: $(this).data("month")  // JS key matches Python parameter
//                 },
//                 callback(r) {
//                     let html = `<h4>Project Details</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Project</th><th>Total</th><th>Achieved</th><th>Balance</th><th>Entries</th><th>View</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         html += `<tr>
//                             <td>${d.project_name}</td>
//                             <td>${d.total_weight}</td>
//                             <td>${d.achieved_weight}</td>
//                             <td>${d.total_weight - d.achieved_weight}</td>
//                             <td>${d.entry_count}</td>
//                             <td>
//                                 <button class="btn btn-xs btn-warning ft-project-view"
//                                     data-project="${d.project_name}">
//                                     View
//                                 </button>
//                             </td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });

//         // PROJECT → ENTRY
//         report.page.wrapper.on("click", ".ft-project-view", function () {
//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_entry_data",
//                 args: { project_name: $(this).data("project") },
//                 callback(r) {
//                     let html = `<h4>Project Entries</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Description</th><th>Weight</th><th>Achieved</th><th>Balance</th><th>Date</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         html += `<tr>
//                             <td>${d.description || ""}</td>
//                             <td>${d.project_weight}</td>
//                             <td>${d.achieved_weight}</td>
//                             <td>${d.project_weight - d.achieved_weight}</td>
//                             <td>${d.posting_date}</td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });
//     }
// };
// # ///////////////////////////////21-01-26

// /////////////////////////////////////////
frappe.query_reports["FT Report"] = {
    filters: [
        { fieldname: "year", label: __("Year"), fieldtype: "Link", options: "FT Year" }
    ],

    onload(report) {
        report.page.wrapper.append(`
            <div id="ft-detail-container" style="margin-top:25px;">
                <div id="ft-month-container"></div>
                <div id="ft-project-container" style="margin-top:20px;"></div>
                <div id="ft-entry-container" style="margin-top:20px;"></div>
            </div>
        `);

        // YEAR → MONTH
        report.page.wrapper.on("click", ".ft-view-btn", function () {
            let year = $(this).data("year");

            frappe.call({
                method: "fabtrk.fabtrk.report.ft_report.ft_report.get_month_wise_data",
                args: { year },
                callback(r) {
                    let html = `<h4>Month Details - ${year}</h4>
                    <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Total</th>
                            <th>Achieved</th>
                            <th>Balance</th>
                            <th>%</th>
                            <th>View</th>
                        </tr>
                    </thead><tbody>`;

                    r.message.forEach(d => {
                        let bal = d.total_weight - d.achieved_weight;
                        let per = d.total_weight ? ((d.achieved_weight / d.total_weight) * 100).toFixed(1) : 0;

                        html += `<tr>
                            <td>${d.month}</td>
                            <td>${d.total_weight}</td>
                            <td>${d.achieved_weight}</td>
                            <td>${bal}</td>
                            <td>${per}%</td>
                            <td>
                                <button class="btn btn-xs btn-info ft-month-view"
                                    data-year="${year}"
                                    data-month="${d.month_no}">
                                    View
                                </button>
                            </td>
                        </tr>`;
                    });

                    html += `</tbody></table>`;

                    $("#ft-month-container").html(html);
                    $("#ft-project-container").html("");
                    $("#ft-entry-container").html("");
                }
            });
        });

        // MONTH → PROJECT
        report.page.wrapper.on("click", ".ft-month-view", function () {
            let year = $(this).data("year");
            let month = $(this).data("month");

            frappe.call({
                method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_wise_data",
                args: { year, month },
                callback(r) {
                    let html = `<h4>Project Details</h4>
                    <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Project</th>
                            <th>Total</th>
                            <th>Achieved</th>
                            <th>Balance</th>
                            <th>Entries</th>
                            <th>View</th>
                        </tr>
                    </thead><tbody>`;

                    r.message.forEach(d => {
                        html += `<tr>
                            <td>${d.project_name}</td>
                            <td>${d.total_weight}</td>
                            <td>${d.achieved_weight}</td>
                            <td>${d.total_weight - d.achieved_weight}</td>
                            <td>${d.entry_count}</td>
                            <td>
                                <button class="btn btn-xs btn-warning ft-project-view"
                                    data-project="${d.project_name}">
                                    View
                                </button>
                            </td>
                        </tr>`;
                    });

                    html += `</tbody></table>`;

                    $("#ft-project-container").html(html);
                    $("#ft-entry-container").html("");
                }
            });
        });

        // PROJECT → ENTRY
        report.page.wrapper.on("click", ".ft-project-view", function () {
            let project_name = $(this).data("project");

            frappe.call({
                method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_entry_data",
                args: { project_name },
                callback(r) {
                    let html = `<h4>Project Entries</h4>
                    <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Weight</th>
                            <th>Achieved</th>
                            <th>Balance</th>
                            <th>Date</th>
                        </tr>
                    </thead><tbody>`;

                    r.message.forEach(d => {
                        html += `<tr>
                            <td>${d.description || ""}</td>
                            <td>${d.project_weight}</td>
                            <td>${d.achieved_weight}</td>
                            <td>${d.project_weight - d.achieved_weight}</td>
                            <td>${d.posting_date}</td>
                        </tr>`;
                    });

                    html += `</tbody></table>`;

                    $("#ft-entry-container").html(html);
                }
            });
        });
    }
};

// /////////////////////////////////////////



// frappe.query_reports["FT Report"] = {
//     filters: [
//         { fieldname: "year", label: __("Year"), fieldtype: "Link", options: "FT Year" }
//     ],

//     onload(report) {
//         report.page.wrapper.append(`<div id="ft-detail-container" style="margin-top:25px;"></div>`);

//         // YEAR → MONTH
//         report.page.wrapper.on("click", ".ft-view-btn", function () {
//             let year = $(this).data("year");

//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_month_wise_data",
//                 args: { year },
//                 callback(r) {
//                     let html = `<h4>Month Details - ${year}</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Month</th><th>Total</th><th>Achieved</th><th>Balance</th><th>%</th><th>View</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         let bal = d.total_weight - d.achieved_weight;
//                         let per = d.total_weight ? ((d.achieved_weight / d.total_weight) * 100).toFixed(1) : 0;

//                         html += `<tr>
//                             <td>${d.month}</td>
//                             <td>${d.total_weight}</td>
//                             <td>${d.achieved_weight}</td>
//                             <td>${bal}</td>
//                             <td>${per}%</td>
//                             <td>
//                                 <button class="btn btn-xs btn-info ft-month-view"
//                                     data-year="${year}"
//                                     data-month-no="${d.month_no}">
//                                     View
//                                 </button>
//                             </td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });

//         // MONTH → PROJECT
//         report.page.wrapper.on("click", ".ft-month-view", function () {
//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_wise_data",
//                 args: {
//                     year: $(this).data("year"),
//                     month_no: $(this).data("month-no")
//                 },
//                 callback(r) {
//                     let html = `<h4>Project Details</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Project</th><th>Total</th><th>Achieved</th><th>Balance</th><th>Entries</th><th>View</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         html += `<tr>
//                             <td>${d.project_name}</td>
//                             <td>${d.total_weight}</td>
//                             <td>${d.achieved_weight}</td>
//                             <td>${d.total_weight - d.achieved_weight}</td>
//                             <td>${d.entry_count}</td>
//                             <td>
//                                 <button class="btn btn-xs btn-warning ft-project-view"
//                                     data-project="${d.project_name}">
//                                     View
//                                 </button>
//                             </td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });

//         // PROJECT → ENTRY
//         report.page.wrapper.on("click", ".ft-project-view", function () {
//             frappe.call({
//                 method: "fabtrk.fabtrk.report.ft_report.ft_report.get_project_entry_data",
//                 args: { project_name: $(this).data("project") },
//                 callback(r) {
//                     let html = `<h4>Project Entries</h4>
//                     <table class="table table-bordered"><thead>
//                     <tr><th>Description</th><th>Weight</th><th>Achieved</th><th>Balance</th><th>Date</th></tr>
//                     </thead><tbody>`;

//                     r.message.forEach(d => {
//                         html += `<tr>
//                             <td>${d.description || ""}</td>
//                             <td>${d.project_weight}</td>
//                             <td>${d.total_weight_for_project_achieve}</td>
//                             <td>${d.project_weight - d.total_weight_for_project_achieve}</td>
//                             <td>${d.posting_date}</td>
//                         </tr>`;
//                     });

//                     $("#ft-detail-container").html(html + "</tbody></table>");
//                 }
//             });
//         });
//     }
// };
