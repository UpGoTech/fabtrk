// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Monthly Achievement", {
// 	refresh(frm) {

// 	},
// });






// frappe.ui.form.on("FT Monthly Achievement", {

//     year(frm) {
//         frm.set_value("select_month", "");
//         frm.trigger("filter_month_by_year");
//     },

//     refresh(frm) {
//         frm.trigger("filter_month_by_year");
//     },

//     filter_month_by_year(frm) {
//         if (!frm.doc.year) return;

//         frm.set_query("select_month", function () {
//             return {
//                 filters: {
//                     year: frm.doc.year
//                 }
//             };
//         });
//     }
// });

frappe.ui.form.on("FT Monthly Achievement", {

    year(frm) {
        frm.set_value("select_month", "");
        frm.set_value("project_number", "");
        frm.trigger("set_month_filter");
        frm.trigger("set_project_filter");
    },

    select_month(frm) {
        frm.set_value("project_number", "");
        frm.trigger("set_project_filter");
        frm.trigger("filter_project_by_month");
    },

    refresh(frm) {
        frm.trigger("set_month_filter");
        frm.trigger("set_project_filter");
        frm.trigger("filter_project_by_month");
    },

    set_month_filter(frm) {
        if (!frm.doc.year) return;

        frm.set_query("select_month", () => ({
            filters: {
                year: frm.doc.year
            }
        }));
    },

    
    filter_project_by_month(frm) {
        if (!frm.doc.select_month) return;

        frm.set_query("project_number", function () {
            return {
                query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_projects_by_month",
                filters: {
                    month: frm.doc.select_month
                }
            };
        });
    }
});




