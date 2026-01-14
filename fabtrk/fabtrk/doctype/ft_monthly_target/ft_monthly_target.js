// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Monthly Target", {
// 	refresh(frm) {

// 	},
// });

///// month aut year change 

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
///// month aut year change 

















frappe.ui.form.on('FT Monthly Target', {

    onload(frm) {
        set_available_months(frm);
        calculate_total_target(frm); // load hone p
        // calculate_total_target_and_mt(frm);
    },
    refresh(frm) {
        set_available_months(frm);
        calculate_total_target(frm); // load hone p
        // calculate_total_target_and_mt(frm);
    }

});
// year + no duplicated entry
function set_available_months(frm) {
    const year = new Date().getFullYear().toString().slice(-2);
    // const year = '25';


    const all_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ].map(m => `${m}-${year}`);

    // Get already used months from DB
    frappe.db.get_list('FT Monthly Target', {
        fields: ['month'],
        filters: {
            month: ['!=', '']
        },
        limit: 100
    }).then(records => {

        const used_months = records
            .map(r => r.month)
            .filter(m => m !== frm.doc.month);
        // current doc ka month allow rahe

        const available_months = all_months.filter(
            m => !used_months.includes(m)
        );

        frm.set_df_property(
            'month',
            'options',
            available_months.join('\n')
        );
    });
}




// Sum of Target weight = kg
function calculate_total_target(frm) {
    let total = 0;

    if (frm.doc.project) {
        frm.doc.project.forEach(row => {
            if (row.target_weight) {
                total += row.target_weight;
            }
        });
    }
    // Total Target field me set karo
    frm.set_value('kg', total);
}


// Child table field change
frappe.ui.form.on('FT Month Target Childtable', {
    target_weight: function (frm, cdt, cdn) {
        calculate_total_target_and_mt(frm);
    },
    project_remove: function (frm, cdt, cdn) {
        calculate_total_target_and_mt(frm);
    }
});

// Calculate Total Target and MT
function calculate_total_target_and_mt(frm) {
    let total = 0;

    if (frm.doc.project) {
        frm.doc.project.forEach(row => {
            if (row.target_weight) {
                total += row.target_weight;
            }
        });
    }

    // Set Total Target
    frm.set_value('kg', total);

    // Set MT (assuming 1 MT = 1000 kg)
    let mt = total / 1000;
    frm.set_value('mt', mt);
}
