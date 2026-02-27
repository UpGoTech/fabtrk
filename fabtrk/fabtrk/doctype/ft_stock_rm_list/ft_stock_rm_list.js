
frappe.ui.form.on("FT Stock RM List", {    
    refresh(frm) {
        set_grade_filter(frm);
        update_computed_name(frm);
    },

    section_type(frm) {
        frm.set_value("grade", "");
        frm.set_value("stock_rm_type", "");
        set_grade_filter(frm);
        update_computed_name(frm);

        frm.set_value("name1", "");
        frm.set_value("thickness_mm", "");
        frm.set_value("kg__sqm", "");
        frm.set_value("kg__meter", "");
        frm.refresh_fields();
    },

    name1(frm) {
        update_computed_name(frm);
    },

    stock_rm_type(frm) {
        update_computed_name(frm);
    },

    thickness_mm(frm) {
        update_computed_name(frm);
    },

    kg__sqm(frm) {
        update_computed_name(frm);
    },

    kg__meter(frm) {
        update_computed_name(frm);
    },

    grade(frm) {
        update_computed_name(frm);
    }
});


// ✅ Grade Filter
function set_grade_filter(frm) {

    frm.set_query("grade", function () {

        if (frm.doc.section_type === "Section") {
            return {
                filters: {
                    bis_section: ["!=", ""]
                }
            };
        }

        if (frm.doc.section_type === "Plate") {
            return {
                filters: {
                    bis_plate: ["!=", ""]
                }
            };
        }
    });
}


function update_computed_name(frm) {

    let base_name = "";
    let size_part = "";
    let grade_display = "";
    let main_bis = "";
    let type_bis = "";

    // 🔹 SECTION TYPE
    if (frm.doc.section_type === "Section") {

        base_name = frm.doc.stock_rm_type || "";

        if (frm.doc.name1) {
            size_part = frm.doc.name1 + " THK";
        }
    }

    // 🔹 PLATE TYPE
    if (frm.doc.section_type === "Plate") {

        base_name = frm.doc.stock_rm_type || "";

        // if (frm.doc.thickness_mm !== undefined && frm.doc.thickness_mm !== null) {
        //     let thickness = String(frm.doc.thickness_mm).padStart(2, "0");
        //     size_part = thickness + " THK";
        // }
        if (frm.doc.thickness_mm !== undefined && frm.doc.thickness_mm !== null) {

            let thickness = String(frm.doc.thickness_mm);

            // Agar decimal hai (3.56 type)
            if (thickness.includes(".")) {
                let parts = thickness.split(".");
                let intPart = parts[0].padStart(2, "0");
                thickness = intPart + "." + parts[1];
            }
            else {
                // Agar sirf integer hai (3 type)
                thickness = thickness.padStart(2, "0");
            }

            size_part = thickness + " THK";
        }

    }

    // 🔹 If No Grade Selected → Simple Name
    if (!frm.doc.grade) {

        let final_name = [base_name, size_part]
            .filter(Boolean)
            .join(" ");

        frm.set_value("computed_name", final_name);
        return;
    }

    // 🔹 Fetch Grade + BIS
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "FT Material Grade Catalogues",
            name: frm.doc.grade
        },
        callback: function (res) {

            if (res.message) {

                let grade_doc = res.message;

                grade_display = grade_doc.grade || frm.doc.grade;
                main_bis = grade_doc.bis || "";

                if (frm.doc.section_type === "Section") {
                    type_bis = grade_doc.bis_section || "";
                }

                if (frm.doc.section_type === "Plate") {
                    type_bis = grade_doc.bis_plate || "";
                }

                // Beam 5131THK IS808 IS2062 E350BR
                let final_name = [
                    base_name,
                    size_part,
                    type_bis,
                    main_bis,
                    grade_display
                ]
                    .filter(Boolean)
                    .join(" ");

                frm.set_value("computed_name", final_name);
            }
        }
    });
}


