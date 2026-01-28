// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Monthly Achievement", {
// 	refresh(frm) {

// 	},
// });


// 19-1-26
// frappe.ui.form.on("FT Monthly Achievement", {

//     year(frm) {
//         frm.set_value("select_month", "");
//         frm.set_value("project_number", "");
//         frm.trigger("set_month_filter");
//         frm.trigger("set_project_filter");
//     },

//     select_month(frm) {
//         frm.set_value("project_number", "");
//         frm.trigger("set_project_filter");
//         frm.trigger("filter_project_by_month");
//     },

//     refresh(frm) {
//         frm.trigger("set_month_filter");
//         frm.trigger("set_project_filter");
//         frm.trigger("filter_project_by_month");
//     },

//     set_month_filter(frm) {
//         if (!frm.doc.year) return;

//         frm.set_query("select_month", () => ({
//             filters: {
//                 year: frm.doc.year
//             }
//         }));
//     },


//     filter_project_by_month(frm) {
//         if (!frm.doc.select_month) return;

//         frm.set_query("project_number", function () {
//             return {
//                 query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_projects_by_month",
//                 filters: {
//                     month: frm.doc.select_month
//                 }
//             };
//         });
//     }
// });
// 19-1-26





function formatINR(value) {
    return frappe.format(value, { fieldtype: "Float" });
}

frappe.ui.form.on("FT Monthly Achievement", {

    year(frm) {
        frm.set_value("select_month", "");
        frm.set_value("project_number", "");
        frm.trigger("set_month_filter");
    },

    select_month(frm) {
        frm.set_value("project_number", "");
        frm.trigger("set_project_filter");
    },

    refresh(frm) {
        frm.trigger("set_month_filter");
        frm.trigger("set_project_filter");
    },
    ////////////// year pe  month filter
    // set_month_filter(frm) {
    //     if (!frm.doc.year) return;

    //     frm.set_query("select_month", () => ({
    //         query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_months_by_year",
    //         filters: {
    //             year: frm.doc.year
    //         }
    //     }));
    // },
    ////////////// year pe  month filter

    // # seperat month sort
    set_month_filter(frm) {
        frm.set_query("select_month", () => ({
            query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_months_by_year"
        }));
    },
    // # seperat month sort

    //  ////project number filter after select month
    // set_project_filter(frm) {
    //     if (!frm.doc.year || !frm.doc.select_month) return;

    //     frm.set_query("project_number", () => ({
    //         query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_projects_by_year_month",
    //         filters: {
    //             year: frm.doc.year,
    //             month: frm.doc.select_month
    //         }
    //     }));
    // },

    // ////only show those project which is check the is active
    set_project_filter(frm) {
        frm.set_query("project_number", () => ({
            filters: {
                is_active: 1
            }
        }));
    },
    // ////only show those project which is check the is active

    total_weight_for_project_achieve(frm) {
        if (!frm.doc.year || !frm.doc.select_month || !frm.doc.project_number) return;
        if (!frm.doc.total_weight_for_project_achieve) return;

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.check_project_weight",
            args: {
                year: frm.doc.year,
                select_month: frm.doc.select_month,
                project_number: frm.doc.project_number,
                current_value: frm.doc.total_weight_for_project_achieve,
                docname: frm.doc.name,
                actual_weight: frm.doc.month_total_weight_of_project  // ✅ Pass month total weight
            },
            callback: function (r) {
                if (!r.message) return;

                const res = r.message;

                if (res.status === "full") {
                    frappe.msgprint({
                        title: "Project Fully Achieved",
                        indicator: "red",
                        message: `
                            Month Total Weight of Project: ${formatINR(res.actual)}<br>
                            Already Achieved: ${res.achieved}<br><br>
                            🎉 This project is already fully achieved.
                        `
                    });
                    frm.set_value("total_weight_for_project_achieve", 0);
                }

                if (res.status === "exceed") {
                    frappe.msgprint({
                        title: "Invalid Weight Entry",
                        indicator: "red",
                        message: `
                            Month Total Weight of Project: ${res.actual}<br>
                            Already Achieved: ${res.achieved}<br>
                            Remaining Balance: ${res.balance}<br><br>
                            👉 You can enter maximum ${res.balance}
                        `
                    });
                }

                if (res.status === "ok") {
                    frappe.show_alert({
                        message: `✅ Entry OK. Remaining balance after save: ${res.balance}`,
                        indicator: "green"
                    });
                }
            }
        });
    },

    project_number(frm) {
        // 🔄 RESET Month Total Weight when project changes
        frm.set_value("month_total_weight_of_project", 0);
        frm.set_value("total_weight_for_project_achieve", 0);

        
        if (!frm.doc.select_month || !frm.doc.project_number) return;

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_monthly_total_weight",
            args: {
                month_target: frm.doc.select_month,
                project_number: frm.doc.project_number
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("month_total_weight_of_project", r.message);
                }
            }
        });
    },

});




