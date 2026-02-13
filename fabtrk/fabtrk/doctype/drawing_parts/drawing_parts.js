// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Drawing Parts", {
    quantity(frm) {
        calculate_total(frm);
    },
    lenght(frm) {
        calculate_total(frm);
    },
    breath(frm) {
        calculate_total(frm);
    },
    single_weight(frm) {
        calculate_total(frm);
    },
    refresh(frm) {
        toggle_dimension_fields(frm);
        calculate_total(frm);
    },

    project_number(frm) {
        // Project change hote hi Drawing clear karo
        frm.set_value("drawing_number", "");
        frm.set_value("item", "");
        frm.set_value("lenght", 0);
        frm.set_value("breath", 0);
        frm.set_value("total_weight", 0);

        // Drawing filter set karo
        frm.set_query("drawing_number", function () {
            return {
                filters: {
                    project_number: frm.doc.project_number
                }
            };
        });

        set_item_filter(frm);
        toggle_dimension_fields(frm);
        calculate_total(frm);
    },

    drawing_number(frm) {
        frm.set_value("item", "");
        frm.set_value("lenght", 0);
        frm.set_value("breath", 0);
        frm.set_value("total_weight", 0);

        set_item_filter(frm);
        toggle_dimension_fields(frm);
        calculate_total(frm);
    },

    item(frm) {
        frm.set_value("lenght", 0);
        frm.set_value("breath", 0);
        frm.set_value("total_weight", 0);

        toggle_dimension_fields(frm);
        check_duplicate_item(frm);
        calculate_total(frm);
    }
});
        

function calculate_total(frm) {
    let quantity = frm.doc.quantity || 0;
    let lenght = frm.doc.lenght || 0;
    let breath = frm.doc.breath || 0;
    let single_weight = frm.doc.single_weight || 0;

    let total = quantity * lenght * breath * single_weight;

    frm.set_value("total_weight", total);
}


function set_item_filter(frm) {

    if (!frm.doc.project_number || !frm.doc.drawing_number) {
        return;
    }

    // Pehle existing items nikalo
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Drawing Parts",
            filters: {
                project_number: frm.doc.project_number,
                drawing_number: frm.doc.drawing_number,
                name: ["!=", frm.doc.name]
            },
            fields: ["item"],
            limit_page_length: 500
        },
        callback: function (res) {

            let used_items = [];

            if (res.message) {
                res.message.forEach(d => {
                    if (d.item) {
                        used_items.push(d.item);
                    }
                });
            }

            // Ab item field me filter lagao
            frm.set_query("item", function () {

                if (used_items.length > 0) {
                    return {
                        filters: {
                            name: ["not in", used_items]
                        }
                    };
                } else {
                    return {};
                }
            });

        }
    });
}


// ✅ 2️⃣ Duplicate Check
function check_duplicate_item(frm) {

    if (!frm.doc.project_number || !frm.doc.drawing_number || !frm.doc.item) {
        return;
    }

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Drawing Parts",
            filters: {
                project_number: frm.doc.project_number,
                drawing_number: frm.doc.drawing_number,
                item: frm.doc.item,
                name: ["!=", frm.doc.name] // current doc ignore kare
            },
            fields: ["name"]
        },
        callback: function (res) {

            if (res.message.length > 0) {

                frappe.msgprint("⚠ This Item already exists for selected Project & Drawing");

                frm.set_value("item", "");
            }
        }
    });
}

function toggle_dimension_fields(frm) {

    // Item select hone tak dono hide
    frm.toggle_display("lenght", false);
    frm.toggle_display("breath", false);

    if (!frm.doc.item) return;

    frappe.db.get_value("FT Stock RM List", frm.doc.item, "section_type")
        .then(r => {
            if (r.message && r.message.section_type === "Plate") {
                frm.toggle_display("lenght", true);
                frm.toggle_display("breath", true);
            } else {
                frm.toggle_display("lenght", true);
                frm.toggle_display("breath", false);
            }
        });
}

function get_existing_items(frm) {

    let items = [];

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Drawing Parts",
            filters: {
                project_number: frm.doc.project_number,
                drawing_number: frm.doc.drawing_number,
                name: ["!=", frm.doc.name]
            },
            fields: ["item"],
            limit_page_length: 500
        },
        async: false,   // IMPORTANT (sync call)
        callback: function (res) {
            if (res.message) {
                res.message.forEach(d => {
                    if (d.item) {
                        items.push(d.item);
                    }
                });
            }
        }
    });

    return items;
}







    

