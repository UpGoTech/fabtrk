// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Monthly Target", {
// 	refresh(frm) {

// 	},
// });

///// month aur year change 

// frappe.ui.form.on('FT Monthly Target', {
//     onload(frm) {
//         set_month_options(frm);
//     },

//     refresh(frm) {
//         set_month_options(frm);
//     }
// });

// function set_month_options(frm) {
//     const current_year = new Date().getFullYear().toString().slice(-2);

//     const months = [
//         'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
//         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
//     ];

//     const options = months.map(m => `${m}-${current_year}`);

//     frm.set_df_property('month', 'options', options.join('\n'));
// }
///// month aur year change 










// ////////////15-01-26


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

        frm.set_query("select_month", function () {
            return {
                query: "fabtrk.fabtrk.doctype.ft_monthly_target.ft_monthly_target.get_used_months",
                filters: {
                    year: frm.doc.year,
                    current_doc: frm.doc.name
                },
                no_cache: true
            };
        });
    },

    validate(frm) {
        let missing_weight = [];

        if (frm.doc.project && frm.doc.project.length) {
            frm.doc.project.forEach((row, index) => {
                if (!row.total_weight_of_project || row.total_weight_of_project <= 0) {
                    missing_weight.push(index + 1); // Row number
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

        // ❌ Duplicate project
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

                        // Clear all fields in this row
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
        // let project_amount = flt(row.project_amount);

        // ✅ Store original balance only once
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

        // if (entered !== project_amount) {
        //     frappe.msgprint(`
        //         Entered weight(${entered.toLocaleString()}kg)
        //         does not match Proejct amount(${project_amount.toLocaleString()})
        //         `);
        //     frappe.model.set_value(cdt, cdn, "total_weight_of_project", 0);
        //     return;
        // }
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

        // ✅ Check if project weight is now complete
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

//child row if project total weight is complete this filed is refresh 
function clear_child_row(row, cdt, cdn) {
    let fields_to_clear = [
        "project_number",
        "project_name",
        "customer_name",
        "description",
        "project_amount",
        "total_weight_of_project",
        "balance_amount",
        "other_field1", // अगर और कोई field है तो add करो
    ];

    fields_to_clear.forEach(f => frappe.model.set_value(cdt, cdn, f, ""));
}


// Calculate Total Target and MT
function calculate_total_target_and_mt(frm) {
    let total = 0;

    if (frm.doc.project) {
        frm.doc.project.forEach(row => {
            if (row.total_weight_of_project) {
                total += row.total_weight_of_project;
            }
        });
    }

    // Set Total Target
    frm.set_value('kg', total);

    // Set MT (assuming 1 MT = 1000 kg)
    let mt = total / 1000;
    frm.set_value('mt', mt);
}

// ////////////15-01-26








// 14-1-26

// frappe.ui.form.on('FT Monthly Target', {

//     onload(frm) {
//         set_available_months(frm);
//         calculate_total_target(frm); // load hone p
//         // calculate_total_target_and_mt(frm);
//     },
//     refresh(frm) {
//         set_available_months(frm);
//         calculate_total_target(frm); // load hone p
//         // calculate_total_target_and_mt(frm);
//     }

// });
// // year + no duplicated entry
// function set_available_months(frm) {
//     const year = new Date().getFullYear().toString().slice(-2);
//     // const year = '25';


//     const all_months = [
//         'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
//         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
//     ].map(m => `${m}-${year}`);

//     // Get already used months from DB
//     frappe.db.get_list('FT Monthly Target', {
//         fields: ['month'],
//         filters: {
//             month: ['!=', '']
//         },
//         limit: 100
//     }).then(records => {

//         const used_months = records
//             .map(r => r.month)
//             .filter(m => m !== frm.doc.month);
//         // current doc ka month allow rahe

//         const available_months = all_months.filter(
//             m => !used_months.includes(m)
//         );

//         frm.set_df_property(
//             'month',
//             'options',
//             available_months.join('\n')
//         );
//     });
// }



// // Sum of Target weight = kg
// function calculate_total_target(frm) {
//     let total = 0;

//     if (frm.doc.project) {
//         frm.doc.project.forEach(row => {
//             if (row.total_weight_of_project) {
//                 total += row.total_weight_of_project;
//             }
//         });
//     }
//     // Total Target field me set karo
//     frm.set_value('kg', total);
// }


// // Child table field change
// frappe.ui.form.on('FT Month Target Childtable', {
//     total_weight_of_project: function (frm, cdt, cdn) {
//         calculate_total_target_and_mt(frm);
//     },
//     project_remove: function (frm, cdt, cdn) {
//         calculate_total_target_and_mt(frm);
//     }
// });

// // Calculate Total Target and MT
// function calculate_total_target_and_mt(frm) {
//     let total = 0;

//     if (frm.doc.project) {
//         frm.doc.project.forEach(row => {
//             if (row.total_weight_of_project) {
//                 total += row.total_weight_of_project;
//             }
//         });
//     }

//     // Set Total Target
//     frm.set_value('kg', total);

//     // Set MT (assuming 1 MT = 1000 kg)
//     let mt = total / 1000;
//     frm.set_value('mt', mt);
// }
