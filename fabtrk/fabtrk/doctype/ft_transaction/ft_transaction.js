// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Transaction", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('FT Transaction', {
    stages: function (frm) {
        handle_fields(frm);
    },
    refresh: function (frm) {
        handle_fields(frm);
        set_stage_query(frm);

    },
    project_number: function (frm) {
        set_stage_query(frm);   // 🔥 IMPORTANT
    }
});
function set_stage_query(frm) {
    frm.set_query("stages", function () {
        return {
            query: "fabtrk.fabtrk.doctype.ft_transaction.ft_transaction.get_project_stages",
            filters: {
                project: frm.doc.project_number || ""
            }
        };
    });
}

function handle_fields(frm) {
    let stage = (frm.doc.stages || "").toLowerCase();  // safe + lowercase

    // Default: dono hide + disable
    frm.set_df_property('addition', 'hidden', 1);
    frm.set_df_property('addition', 'read_only', 1);

    frm.set_df_property('subtraction', 'hidden', 1);
    frm.set_df_property('subtraction', 'read_only', 1);

    // 🔹 agar text me "cutting" kahin bhi ho
    if (stage.includes("cutting")) {
        frm.set_df_property('subtraction', 'hidden', 0);
        frm.set_df_property('subtraction', 'read_only', 0);
    }

    // 🔹 agar text me "mrp" kahin bhi ho
    else if (stage.includes("mrp")) {
        frm.set_df_property('addition', 'hidden', 0);
        frm.set_df_property('addition', 'read_only', 0);
    }
}