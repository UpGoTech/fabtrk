// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("FT Monthly Target", {

    year(frm) {
        frm.set_value("select_month", "");
        frm.trigger("set_month_filter");
        frm.clear_table("project");
        frm.refresh_field("project");
    },

    refresh(frm) {
        frm.trigger("set_month_filter");
    },

    set_month_filter(frm) {
        if (!frm.doc.year) return;
    },

    validate(frm) {
        let missing_weight = [];

        if (frm.doc.project && frm.doc.project.length) {
            frm.doc.project.forEach((row, index) => {
                if (!row.total_weight_of_project || row.total_weight_of_project <= 0) {
                    missing_weight.push(index + 1); 
                }
            });
        }

        if (missing_weight.length) {
            frappe.msgprint({
                title: __("Missing Total Weight"),
                indicator: "red",
                message: __(
                    `❌ Total Weight of Project not entered in row(s): <b>${missing_weight.join(", ")}</b><br>
                     ⚠ Please enter Total Weight before saving.`
                )
            });

            frappe.validated = false; // 🚫 Stop Save
        }
    }

});


frappe.ui.form.on("FT Month Target Childtable", {

    project_number(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.project_number) return;

        let duplicate = frm.doc.project.filter(
            d => d.project_number === row.project_number && d.name !== row.name
        );

        if (duplicate.length) {
            frappe.msgprint("❌ This Project is already added");
            clear_child_row(row, cdt, cdn);
            return;
        }

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_monthly_target.ft_monthly_target.get_project_balance",
            args: { project: row.project_number },
            callback(r) {
                if (r.message !== undefined) {
                    if (r.message <= 0) {
                        frappe.msgprint("✅ Project Total Weight already completed");

                        clear_child_row(row, cdt, cdn);

                    } else {
                        frappe.model.set_value(cdt, cdn, "balance_amount", r.message);
                    }
                }
            }
        });
    },

    total_weight_of_project(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let entered = flt(row.total_weight_of_project);
        let balance = flt(row.balance_amount);

        if (!row.previous_balance) {
            frappe.model.set_value(cdt, cdn, "previous_balance", balance);
        }

        if (!entered || entered <= 0) {
            frappe.model.set_value(cdt, cdn, "total_weight_of_project", 0);
            frappe.model.set_value(
                cdt,
                cdn,
                "balance_amount",
                flt(row.previous_balance)
            );
            return;
        }

        if (entered > balance) {
            frappe.msgprint(`
                    ✅Maximum allowed: ${balance.toLocaleString()} <br>
                    ❌You entered: ${entered.toLocaleString()} <br>
                    ⚠ Please adjust the weight.
            `);
            frappe.model.set_value(cdt, cdn, "total_weight_of_project", 0);
            frappe.model.set_value(cdt, cdn, "balance_amount", flt(row.previous_balance));
            return;
        }

        let new_balance = balance - entered;
        frappe.model.set_value(cdt, cdn, "balance_amount", new_balance);

        if (new_balance <= 0) {
            frappe.msgprint(`
                🎉 Project Weight Completed!<br>
                Project Number: ${row.project_number || ""}
            `);
        }

        calculate_total_target_and_mt(frm);
    },


    project_remove(frm, cdt, cdn) {
        calculate_total_target_and_mt(frm);
    }
});

function clear_child_row(row, cdt, cdn) {
    let fields_to_clear = [
        "project_number",
        "project_name",
        "customer_name",
        "description",
        "project_amount",
        "total_weight_of_project",
        "balance_amount",
        "other_field1", 
    ];

    fields_to_clear.forEach(f => frappe.model.set_value(cdt, cdn, f, ""));
}

function calculate_total_target_and_mt(frm) {
    let total = 0;

    if (frm.doc.project) {
        frm.doc.project.forEach(row => {
            if (row.total_weight_of_project) {
                total += row.total_weight_of_project;
            }
        });
    }

    frm.set_value('kg', total);
    let mt = total / 1000;
    frm.set_value('mt', mt);
}

