// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Drawing Parts", {
    quantity(frm) {
        calculate_total(frm);
    },
    lenght(frm) {
        calculate_total(frm);
    },
    single_weight(frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let quantity = frm.doc.quantity || 0;
    let lenght = frm.doc.lenght || 0;
    let single_weight = frm.doc.single_weight || 0;

    let total = quantity * lenght * single_weight;

    frm.set_value("total_weight", total);
}





