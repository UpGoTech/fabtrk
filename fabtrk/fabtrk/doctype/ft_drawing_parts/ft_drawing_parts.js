// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt

frappe.ui.form.on("FT Drawing Parts", {
    quantity(frm) {
        calculate_total(frm);
        refresh_calculation_fields(frm);
    },
    lenght(frm) {
        calculate_total(frm);
        refresh_calculation_fields(frm);
    },
    width(frm) {
        calculate_total(frm);
        refresh_calculation_fields(frm);
    },
    single_weight(frm) {
        calculate_total(frm);
        refresh_calculation_fields(frm);
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
        frm.set_value("width", 0);
        frm.set_value("total_weight", 0);

        reset_calculation_fields(frm);
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
        frm.set_value("width", 0);
        frm.set_value("total_weight", 0);

        reset_calculation_fields(frm);
        set_item_filter(frm);
        toggle_dimension_fields(frm);
        calculate_total(frm);
    },
    item(frm) {
        if (!frm.doc.item) return;

        // Reset dependent fields
        frm.set_value("quantity", 0);
        frm.set_value("lenght", 0);
        frm.set_value("width", 0);
        frm.set_value("single_weight", 0);
        frm.set_value("total_weight", 0);

        // Force UI refresh
        frm.refresh_fields([
            "quantity",
            "lenght",
            "width",
            "single_weight",
            "total_weight"
        ]);


        reset_calculation_fields(frm);
        toggle_dimension_fields(frm);
        check_duplicate_item(frm);

        // Final recalculation after everything
        setTimeout(() => {
            calculate_total(frm);
        }, 300);
    }
});

function reset_calculation_fields(frm) {

    frm.set_value({
        quantity: 0,
        lenght: 0,
        width: 0,
        single_weight: 0,
        total_weight: 0
    });

}

function refresh_calculation_fields(frm) {

    let fields = [
        "quantity",
        "lenght",
        "width",
        "single_weight",
        "total_weight"
    ];

    frm.refresh_fields(fields);
}

function calculate_total(frm) {

    let quantity = flt(frm.doc.quantity);
    let lenght = flt(frm.doc.lenght);
    let width = flt(frm.doc.width || 1);
    let single_weight = flt(frm.doc.single_weight);

    // Agar width hidden hai to 1 consider hoga
    if (!frm.fields_dict.width.df.hidden && width === 0) {
        width = 1;
    }

    let total = quantity * single_weight;

    frm.set_value("total_weight", total);
}


function toggle_dimension_fields(frm) {

    // Item select hone tak dono hide
    frm.toggle_display("lenght", false);
    frm.toggle_display("width", false);

    // if (!frm.doc.item) return;
    if (!frm.doc.item) {
        calculate_total(frm);   
        return;
    }

    frappe.db.get_value("FT Stock RM List", frm.doc.item_id, "section_type")
        .then(r => {
            if (r.message && r.message.section_type === "Plate") {
                frm.toggle_display("lenght", true);
                frm.toggle_display("width", true);
            } else {
                frm.toggle_display("lenght", true);
                frm.toggle_display("width", false);
            }
            calculate_total(frm); // yeh kam me nhi hai
        });
}

function get_existing_items(frm) {

    let items = [];

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "FT Drawing Parts",
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




// // ///////////report and here doctype width hide if you import the data inside the excel
// frappe.ui.form.on("FT Drawing Parts", {
//     quantity(frm) {
//         calculate_total(frm);
//         refresh_calculation_fields(frm);
//     },
//     lenght(frm) {
//         calculate_total(frm);
//         refresh_calculation_fields(frm);
//     },
//     width(frm) {
//         calculate_total(frm);
//         refresh_calculation_fields(frm);
//     },
//     single_weight(frm) {
//         calculate_total(frm);
//         refresh_calculation_fields(frm);
//     },
//     refresh(frm) {
//         toggle_dimension_fields(frm);
//         calculate_total(frm);
//     },
//     project_number(frm) {
//         // Project change hote hi Drawing clear karo
//         frm.set_value("drawing_number", "");
//         frm.set_value("item", "");
//         frm.set_value("item_id", ""); // ✅ FIX
//         frm.set_value("lenght", 0);
//         frm.set_value("width", 0);
//         frm.set_value("total_weight", 0);

//         reset_calculation_fields(frm);

//         // Drawing filter set karo
//         frm.set_query("drawing_number", function () {
//             return {
//                 filters: {
//                     project_number: frm.doc.project_number
//                 }
//             };
//         });

//         set_item_filter(frm);
//         toggle_dimension_fields(frm);
//         calculate_total(frm);
//     },
//     drawing_number(frm) {
//         frm.set_value("item", "");
//         frm.set_value("item_id", ""); // ✅ FIX
//         frm.set_value("lenght", 0);
//         frm.set_value("width", 0);
//         frm.set_value("total_weight", 0);

//         reset_calculation_fields(frm);
//         set_item_filter(frm);
//         toggle_dimension_fields(frm);
//         calculate_total(frm);
//     },

//     // ✅ MAIN FIX (item → item_id)
//     item_id(frm) {
//         if (!frm.doc.item_id) return;

//         // Reset dependent fields
//         frm.set_value("quantity", 0);
//         frm.set_value("lenght", 0);
//         frm.set_value("width", 0);
//         frm.set_value("single_weight", 0);
//         frm.set_value("total_weight", 0);

//         // Force UI refresh
//         frm.refresh_fields([
//             "quantity",
//             "lenght",
//             "width",
//             "single_weight",
//             "total_weight"
//         ]);

//         reset_calculation_fields(frm);
//         toggle_dimension_fields(frm);
//         check_duplicate_item(frm);

//         // Final recalculation after everything
//         setTimeout(() => {
//             calculate_total(frm);
//         }, 300);
//     }
// });

// function reset_calculation_fields(frm) {
//     frm.set_value({
//         quantity: 0,
//         lenght: 0,
//         width: 0,
//         single_weight: 0,
//         total_weight: 0
//     });
// }

// function refresh_calculation_fields(frm) {
//     let fields = [
//         "quantity",
//         "lenght",
//         "width",
//         "single_weight",
//         "total_weight"
//     ];

//     frm.refresh_fields(fields);
// }

// function calculate_total(frm) {

//     let quantity = flt(frm.doc.quantity);
//     let lenght = flt(frm.doc.lenght);
//     let width = flt(frm.doc.width || 1);
//     let single_weight = flt(frm.doc.single_weight);

//     // ✅ FIX: width hidden hai to 1 lo
//     if (frm.fields_dict.width.df.hidden) {
//         width = 1;
//     }

//     let total = quantity * single_weight;

//     frm.set_value("total_weight", total);
// }

// function toggle_dimension_fields(frm) {

//     // Item select hone tak dono hide
//     frm.toggle_display("lenght", false);
//     frm.toggle_display("width", false);

//     // ❗ FIX: item की जगह item_id
//     if (!frm.doc.item_id) {
//         return;
//     }

//     frappe.db.get_value("FT Stock RM List", frm.doc.item_id, "section_type")
//         .then(r => {
//             if (r.message && r.message.section_type === "Plate") {
//                 frm.toggle_display("lenght", true);
//                 frm.toggle_display("width", true);
//             } else {
//                 frm.toggle_display("lenght", true);
//                 frm.toggle_display("width", false);

//                 // 🔥 IMPORTANT FIX (Data cleanup)
//                 if (frm.doc.width) {
//                     frm.set_value("width", 0);
//                 }
//             }

//             calculate_total(frm);
//         });
// }

// function get_existing_items(frm) {

//     let items = [];

//     frappe.call({
//         method: "frappe.client.get_list",
//         args: {
//             doctype: "FT Drawing Parts",
//             filters: {
//                 project_number: frm.doc.project_number,
//                 drawing_number: frm.doc.drawing_number,
//                 name: ["!=", frm.doc.name]
//             },
//             fields: ["item"],
//             limit_page_length: 500
//         },
//         async: false,
//         callback: function (res) {
//             if (res.message) {
//                 res.message.forEach(d => {
//                     if (d.item) {
//                         items.push(d.item);
//                     }
//                 });
//             }
//         }
//     });

//     return items;
// }

