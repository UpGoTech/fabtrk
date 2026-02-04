// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt


///// computed filed me auto name likhna 
frappe.ui.form.on("FT Stock RM List", {
    // RM TYPE CHANGE → RESET FIELDS
    stock_rm_type: function (frm) {
        // Section change hone par baki fields clear karo
        // frm.set_value("length", null);
        frm.set_value("breath", null);
        frm.set_value("weight", null);
        frm.set_value("thickness_mm", null);
        frm.set_value("grade", null);

        // Computed Name update karo
        update_computed_name(frm);
    },
    length: function (frm) { update_computed_name(frm); },
    breath: function (frm) { update_computed_name(frm); },
    weight: function (frm) { update_computed_name(frm); },
    thickness_mm: function (frm) { update_computed_name(frm); },
    grade: function (frm) { update_computed_name(frm); },



    // //////plate/ section select krne pr stock rm type me filetr ho 
    setup(frm) {
        frm.set_query("stock_rm_type", function () {
            if (frm.doc.section_type === "Plate") {
                return {
                    filters: {
                        name: "Plate"
                    }
                };
            }

            if (frm.doc.section_type === "Section") {
                return {
                    filters: [
                        ["FT Stock RM Type", "name", "!=", "Plate"]
                    ]
                };
            }
        });

        // 🔹 Stock RM Type → Grade filter
        frm.set_query("grade", function () {
            if (frm.doc.stock_rm_type) {
                return {
                    filters: {
                        stock_rm_type: frm.doc.stock_rm_type
                    }
                };
            }
        });
        // 🔹 Stock RM Type → Grade filter
    },

    section_type(frm) {
        // section change hua → RM type reset
        frm.set_value("stock_rm_type", "");
    }
    // //////plate/ section select krne pr stock rm type me filetr ho 

});


function update_computed_name(frm) {
    let section = frm.doc.stock_rm_type || "";
    let parts = [];

    // if (frm.doc.length) parts.push(frm.doc.length);
    if (frm.doc.breath) parts.push(frm.doc.breath);
    if (frm.doc.thickness_mm) parts.push(frm.doc.thickness_mm + "MM");
    if (frm.doc.weight) parts.push(frm.doc.weight);

    if (frm.doc.grade) {
        // Stock RM Type ke hisab se grade aur bis dono fetch karo
        frappe.db.get_value('FT Material Grade Catalogues', frm.doc.grade, ['grade','bis_section','bis_plate'])
            .then(r => {
                let grade_display = r.message ? r.message.grade : frm.doc.grade;
                let bis = "";

                // Section type ke hisab se BIS select karo
                if(frm.doc.section_type === "Section") {
                    bis = r.message ? r.message.bis_section : "";
                } else if(frm.doc.section_type === "Plate") {
                    bis = r.message ? r.message.bis_plate : "";
                }

                // Grade aur BIS combine karo
                if(bis) {
                    parts.push(`${grade_display} (${bis})`);
                } else {
                    parts.push(grade_display);
                }

                // Computed Name set karo
                let computed = section;
                if (parts.length > 0) {
                    computed += " " + parts.join(" × ");
                }
                frm.set_value("computed_name", computed);
            });
    } else {
        // Grade blank ho to normal computed name
        let computed = section;
        if (parts.length > 0) {
            computed += " " + parts.join(" × ");
        }
        frm.set_value("computed_name", computed);
    }
}

// function update_computed_name(frm) {
//     let section = frm.doc.stock_rm_type || "";
//     let parts = [];

//     if (frm.doc.length) parts.push(frm.doc.length);
//     if (frm.doc.breath) parts.push(frm.doc.breath);
//     if (frm.doc.thickness_mm) parts.push(frm.doc.thickness_mm + "MM");
//     if (frm.doc.weight) parts.push(frm.doc.weight);
    
//     if (frm.doc.grade) {
//         // Asynchronous fetch of display value
//         frappe.db.get_value('FT Material Grade Catalogues', frm.doc.grade, 'grade')
//             .then(r => {
//                 let grade_display = r.message ? r.message.grade : frm.doc.grade;
//                 parts.push(grade_display);

//                 let computed = section;
//                 if (parts.length > 0) {
//                     computed += " " + parts.join(" X ");
//                 }

//                 frm.set_value("computed_name", computed);
//             });
//     } else {
//         let computed = section;
//         if (parts.length > 0) {
//             computed += " " + parts.join(" × ");
//         }
//         frm.set_value("computed_name", computed);
//     }
// }


///// computed fi;ed me auto name likhna 



