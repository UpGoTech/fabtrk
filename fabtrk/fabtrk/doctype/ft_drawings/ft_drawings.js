// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("FT Drawings", {
    unit_weight(frm) {
        calculate_total_weight(frm);
    },
    quantity(frm) {
        calculate_total_weight(frm);
    }
});

function calculate_total_weight(frm) {
    let unit_weight = frm.doc.unit_weight || 0;
    let quantity = frm.doc.quantity || 0;

    frm.set_value("total_weight", unit_weight * quantity);
}

