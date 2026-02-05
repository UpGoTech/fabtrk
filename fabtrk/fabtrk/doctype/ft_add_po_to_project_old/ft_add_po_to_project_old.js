// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Add Po To Project Old", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("FT Add Po To Project Old", {

    // 🔹 GST change → recalc totals
    gst(frm) {
        calculate_total(frm);
    },

    // 🔹 Customer → filter Project Number
    customer_name(frm) {
        frm.set_value("project_number", "");

        frm.set_query("project_number", function () {
            return {
                filters: {
                    customer_name: frm.doc.customer_name
                }
            };
        });
    }
});

frappe.ui.form.on("FT Po List  Child", {

    qty_set(frm, cdt, cdn) {
        calculate_row(frm, cdt, cdn);
    },

    unit_weight(frm, cdt, cdn) {
        calculate_row(frm, cdt, cdn);
    },

    rate(frm, cdt, cdn) {
        calculate_row(frm, cdt, cdn);
    }
});

function calculate_row(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // 1️⃣ Total Weight = QTY Set × Unit Weight
    row.total_weight =
        (row.qty_set || 0) * (row.unit_weight || 0);

    // 2️⃣ Amount = Total Weight × Rate
    row.amount =
        (row.total_weight || 0) * (row.rate || 0);

    // 🔄 Refresh child table
    frm.refresh_field("drawing_list");

    // 3️⃣ Recalculate parent totals
    calculate_total(frm);
}

function calculate_total(frm) {

    let total_basic = 0;
    let sum_unit_weight = 0;
    let sum_total_weight = 0;

    (frm.doc.drawing_list || []).forEach(function (row) {
        total_basic += row.amount || 0;
        sum_unit_weight += row.unit_weight || 0;
        sum_total_weight += row.total_weight || 0;
    });

    frm.set_value("total_basic_value", total_basic);
    frm.set_value("sum_of_unit_weight", sum_unit_weight);
    frm.set_value("sum_of_quantity_weight", sum_total_weight);

    // 🔹 GST calculation
    let gst = frm.doc.gst || 0;
    let gst_value = (total_basic * gst) / 100;

    frm.set_value("total_include_gst", gst_value);
}
