// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Add Drawings Old", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("FT Add Drawings Old", {

    // ✅ Drawing select → fetch QTY SET (SAFE)
    select_drawing_no(frm) {
        if (!frm.doc.select_drawing_no) return;

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_add_drawings.ft_add_drawings.get_qty_set_from_po_child",
            args: {
                drawing_name: frm.doc.select_drawing_no
            },
            callback(r) {
                let qty_set = r.message || 0;
                frm.set_value("drawing_qty_setkgs", qty_set);

                // recalc all child rows
                (frm.doc.drawing_material_list || []).forEach(row => {
                    calc_drawing_qty_setkgs(frm, row.doctype, row.name);
                });

                calculate_total_weight_calculate(frm);
            }
        });
    },

    // ✅ Customer → Project filter
    customer_name(frm) {
        frm.set_value("project_number", "");
        frm.set_value("po_number", "");

        frm.set_query("project_number", function () {
            return {
                filters: {
                    customer_name: frm.doc.customer_name
                }
            };
        });
    },

    // ✅ Project → PO filter
    project_number(frm) {
        frm.set_value("po_number", "");

        frm.set_query("po_number", function () {
            return {
                filters: {
                    project_number: frm.doc.project_number
                }
            };
        });
    },

    // ✅ PO → Drawing filter
    po_number(frm) {
        frm.set_value("select_drawing_no", "");

        frm.set_query("select_drawing_no", function () {
            return {
                query: "fabtrk.fabtrk.doctype.ft_add_drawings.ft_add_drawings.get_available_drawings",
                filters: {
                    po_number: frm.doc.po_number
                }
            };
        });
    }
});

frappe.ui.form.on("FT Drawing Childtable", {

    drawing_quantity(frm, cdt, cdn) {
        calc_total_in_kgs(frm, cdt, cdn);
    },

    weightunit(frm, cdt, cdn) {
        calc_total_in_kgs(frm, cdt, cdn);
    }
});

function calc_total_in_kgs(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    const qty = Number(row.drawing_quantity) || 0;
    const wpu = Number(row.weightunit) || 0;

    const total = qty * wpu;

    frappe.model.set_value(
        cdt,
        cdn,
        "total_in_kgs",
        Math.round(total * 100) / 100
    );

    calc_drawing_qty_setkgs(frm, cdt, cdn);
    calculate_total_weight_calculate(frm);
}

function calc_drawing_qty_setkgs(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const qty_set = Number(frm.doc.drawing_qty_setkgs) || 0;
    const total_in_kgs = Number(row.total_in_kgs) || 0;

    frappe.model.set_value(
        cdt,
        cdn,
        "drawing_qty_setkgs",
        Math.round(qty_set * total_in_kgs * 100) / 100
    );
}

function calculate_total_weight_calculate(frm) {
    let total_weight = 0;
    let sum_qty = 0;
    let sum_set_kgs = 0;

    (frm.doc.drawing_material_list || []).forEach(row => {
        total_weight += row.total_in_kgs || 0;
        sum_qty += row.drawing_quantity || 0;
        sum_set_kgs += row.drawing_qty_setkgs || 0;
    });

    frm.set_value("total_weight_calculate", total_weight);
    frm.set_value("sum_of_total_in_kgs", total_weight);
    frm.set_value("sum_of_quatity", sum_qty);
    frm.set_value("sum_of_drawing_quatitysetkgs", sum_set_kgs);
}

