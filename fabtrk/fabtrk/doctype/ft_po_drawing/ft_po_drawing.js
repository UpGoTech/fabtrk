// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("FT Po Drawing", {

    refresh(frm) {
        set_drawing_filter(frm);
    },

    project_number(frm) {
        frm.set_value("drawing_number", null);
        set_drawing_filter(frm);
    },

    unit_weight(frm) {
        calculate_total_weight(frm);
    },

    required_qty(frm) {
        calculate_total_weight(frm);
    }
});


function set_drawing_filter(frm) {
    frm.set_query("drawing_number", function () {
        return {
            filters: {
                project_number: frm.doc.project_number
            }
        };
    });
}


function calculate_total_weight(frm) {
    let unit_weight = frm.doc.unit_weight || 0;
    let required_qty = frm.doc.required_qty || 0;

    frm.set_value("total_weight", unit_weight * required_qty);
}