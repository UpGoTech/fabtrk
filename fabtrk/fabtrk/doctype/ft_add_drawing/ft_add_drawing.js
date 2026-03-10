// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("FT Add Drawing", {
    unit_weight(frm) {
        calculate_total_weight(frm);
    },
    quantity(frm) {
        calculate_total_weight(frm);
    },
    refresh(frm) {
        set_drawing_filter(frm);
    },

    project_number(frm) {
        frm.set_value("drawing_number", null);
        set_drawing_filter(frm);
    }
});

function calculate_total_weight(frm) {
    let unit_weight = frm.doc.unit_weight || 0;
    let quantity = frm.doc.quantity || 0;

    frm.set_value("total_weight", unit_weight * quantity);
}

function set_drawing_filter(frm) {
    if (!frm.doc.project_number) return;

    // pehle se use ho chuke drawings lao
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "FT Add Drawing",
            fields: ["drawing_number"],
            
        },
        callback(r) {
            let used_drawings = [];

            if (r.message) {
                used_drawings = r.message
                    .map(d => d.drawing_number)
                    .filter(d => d); 
            }

            // drawing_number link field filter
            frm.set_query("drawing_number", function () {
                return {
                    filters: [
                        ["FT Drawings", "name", "not in", used_drawings]
                    ]
                };
            });
        }
    });
}