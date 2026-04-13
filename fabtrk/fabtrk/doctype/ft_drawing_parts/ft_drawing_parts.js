// // Copyright (c) 2026, UpGo Technologies and contributors
// // For license information, please see license.txt

frappe.ui.form.on("FT Drawing Parts", {
    quantity(frm) {
        calculate_total(frm);
        calculate_painted_area(frm);
        refresh_calculation_fields(frm);
    },
    lenght(frm) {
        calculate_total(frm);
        calculate_painted_area(frm);
        refresh_calculation_fields(frm);
    },
    width(frm) {
        calculate_total(frm);
        calculate_painted_area(frm);
        refresh_calculation_fields(frm);
    },
    single_weight(frm) {
        calculate_total(frm);
        calculate_painted_area(frm);
        refresh_calculation_fields(frm);
    },
    // Sirf painted area recalculate karo
    painted_surface_percentage(frm) {
        calculate_painted_area(frm);
        refresh_calculation_fields(frm);
    },
    refresh(frm) {
        toggle_dimension_fields(frm);
        calculate_total(frm);
        calculate_painted_area(frm);
    },
    project_number(frm) {
        // Project change hote hi Drawing clear karo
        frm.set_value("drawing_number", "");
        frm.set_value("item", "");
        frm.set_value("lenght", 0);
        frm.set_value("width", 0);
        frm.set_value("total_weight", 0);
        frm.set_value("painted_surface_percentage", 0);
        frm.set_value("total_percentage_for_area", "");

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
        frm.set_value("painted_surface_percentage", 0);
        frm.set_value("total_percentage_for_area", "");

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
        frm.set_value("painted_surface_percentage", 0);
        frm.set_value("total_percentage_for_area", "");

        // Force UI refresh
        frm.refresh_fields([
            "quantity",
            "lenght",
            "width",
            "single_weight",
            "total_weight",
            "painted_surface_percentage",
            "total_percentage_for_area"
        ]);


        reset_calculation_fields(frm);
        toggle_dimension_fields(frm);
        check_duplicate_item(frm);

        // Final recalculation after everything
        setTimeout(() => {
            calculate_total(frm);
            calculate_painted_area(frm);
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
    // let lenght = flt(frm.doc.lenght);
    let width = flt(frm.doc.width || 1);
    let single_weight = flt(frm.doc.single_weight);

    // if width is hidden so consider 1 [Agar width hidden hai to 1 consider hoga]
    if (!frm.fields_dict.width.df.hidden && width === 0) {
        width = 1;
    }

    let total = quantity * single_weight;
    frm.set_value("total_weight", total);
}

// ---------- Painted Surface Area ------------------------------------
//   Plate  → lenght × width × kg__sqm × painted_surface_percentage / 100
//   Section→ lenght × surface_area_sqm__mtr × painted_surface_percentage / 100
function calculate_painted_area(frm) {
    // if item is not selected then skip 
    if (!frm.doc.item) {
        frm.set_value("total_percentage_for_area", "");
        return;
    }

    let lenght = flt(frm.doc.lenght);
    let width = flt(frm.doc.width);
    let pct = flt(frm.doc.painted_surface_percentage);

    // Agar percentage 0 ya blank hai to result 0 karo
    if (!pct) {
        frm.set_value("total_percentage_for_area", "0");
        return;
    }

    // ✅ FT Stock RM List se kg__sqm, surface_area_sqm__mtr, section_type fetch karo
    frappe.db.get_value(
        "FT Stock RM List",
        frm.doc.item,
        ["section_type", "kg__sqm", "surface_area_sqm__mtr"]
    ).then(r => {
        if (!r.message) {
            frm.set_value("total_percentage_for_area", "");
            return;
        }

        let section_type = r.message.section_type || "";
        let kg_sqm = flt(r.message.kg__sqm);
        let surface_area_sqm_mtr = flt(r.message.surface_area_sqm__mtr);
        let result = 0;

        if (section_type === "Plate") {
            // Plate: length × width × kg__sqm × pct%
            let length_m = lenght / 1000;
            let width_m = width / 1000;
            result = length_m * width_m * kg_sqm * (pct / 100);

        } else {
            // Section: length × surface_area_sqm_mtr × pct%
            let length_m = lenght / 1000;
            result = length_m * surface_area_sqm_mtr * (pct / 100);
        }
        // Round to 4 decimal places aur string mein store karo (Data field hai)
        let formatted = result.toFixed(4);
        frm.set_value("total_percentage_for_area", formatted);
        frm.refresh_field("total_percentage_for_area");
    });
}

function toggle_dimension_fields(frm) {

    // Item select hone tak dono hide
    frm.toggle_display("lenght", false);
    frm.toggle_display("width", false);

    if (!frm.doc.item) {
        calculate_total(frm);
        return;
    }

    frappe.db.get_value("FT Stock RM List", frm.doc.item, "section_type")
        .then(r => {
            if (r.message && r.message.section_type === "Plate") {
                frm.toggle_display("lenght", true);
                frm.toggle_display("width", true);
            } else {
                frm.toggle_display("lenght", true);
                frm.toggle_display("width", false);
            }
            calculate_total(frm);
            calculate_painted_area(frm);
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
            // limit_page_length: 500
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

