function formatINR(value) {
    return frappe.format(value, { fieldtype: "Float" });
}

frappe.ui.form.on("FT Monthly Achievement", {

    year(frm) {
        frm.set_value("select_month", "");
        frm.set_value("project_number", "");
        frm.trigger("set_month_filter");
    },

    select_month(frm) {
        frm.set_value("project_number", "");
        frm.trigger("set_project_filter");
    },

    refresh(frm) {
        frm.trigger("set_month_filter");
        frm.trigger("set_project_filter");
    },

    set_month_filter(frm) {
        frm.set_query("select_month", () => ({
            query: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_months_by_year"
        }));
    },

    set_project_filter(frm) {
        frm.set_query("project_number", () => ({
            filters: { is_active: 1 }
        }));
    },

    project_number(frm) {
        frm.set_value("target_set_for_the_month", 0);
        frm.set_value("total_weight_for_project_achieved", 0);

        if (!frm.doc.select_month || !frm.doc.project_number) return;

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_monthly_total_weight",
            args: {
                month_target: frm.doc.select_month,
                project_number: frm.doc.project_number
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("target_set_for_the_month", r.message);
                }
            }
        });
    },


    total_weight_for_project_achieved(frm) {
        if (!frm.doc.total_weight_for_project_achieved || !frm.doc.target_set_for_the_month) return;

        let entered = flt(frm.doc.total_weight_for_project_achieved);
        let target = flt(frm.doc.target_set_for_the_month);

        frappe.call({
            method: "fabtrk.fabtrk.doctype.ft_monthly_achievement.ft_monthly_achievement.get_already_achieved",
            args: {
                select_month: frm.doc.select_month,
                project_number: frm.doc.project_number,
                docname: frm.doc.name
            },
            callback(r) {
                let already = flt(r.message || 0);
                let remaining = target - already;

                /* 🔴 CASE 1: Target already achieved */
                if (remaining <= 0) {
                    frappe.msgprint({
                        title: __("Target Already Achieved"),
                        indicator: "green",
                        wide: true,
                        message: `
                        <div class="text-center" style="padding: 15px;width:300px">
                            <h4 class="text-success">✅ Monthly Target Completed</h4>
                            <p style="margin-top:10px;">
                                This project's monthly target has already been fully achieved.
                            </p>
                        </div>
                    `
                    });

                    frm.set_value("total_weight_for_project_achieved", 0);
                    return;
                }

                /* 🔴 CASE 2: Exceeding remaining balance */
                if (entered > remaining) {
                    frappe.msgprint({
                        title: __("Exceeding Monthly Limit"),
                        indicator: "red",
                        wide: true,
                        message: `
                        <table class="table table-bordered table-sm" style="width:420px; margin:auto;">
                            <tr>
                                <td><strong>Monthly Target</strong></td>
                                <td class="text-right">${formatINR(target)} Kg</td>
                            </tr>
                            <tr>
                                <td><strong>Remaining Balance</strong></td>
                                <td class="text-right text-success">
                                    <strong>${formatINR(remaining)} Kg</strong>
                                </td>
                            </tr>
                            <tr class="text-danger">
                                <td><strong>You Entered</strong></td>
                                <td class="text-right">
                                    <strong>${formatINR(entered)} Kg</strong>
                                </td>
                            </tr>
                            <tr class="text-danger">
                                <td><strong>Excess Amount</strong></td>
                                <td class="text-right">
                                    <strong>${formatINR(entered - remaining)} Kg</strong>
                                </td>
                            </tr>
                        </table>
                    `
                    });

                    frm.set_value("total_weight_for_project_achieved", 0);
                    return;
                }

                /* 🟢 CASE 3: Valid entry (OPTIONAL popup – can remove if not needed) */
                frappe.msgprint({
                    title: __("Entry Accepted"),
                    indicator: "blue",
                    message: `
                    <div style="padding:10px;">
                        Remaining after this entry: 
                        <strong>${formatINR(remaining - entered)} Kg</strong>
                    </div>
                `
                });
            }
        });
    }

});



