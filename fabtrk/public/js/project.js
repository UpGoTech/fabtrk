frappe.ui.form.on("Project", {
	setup(frm) {
		frm.set_query("custom_bill_to", () => {
			if (!frm.doc.customer) {
				return { filters: { name: "" } };
			}
			return {
				query: "frappe.contacts.doctype.address.address.address_query",
				filters: {
					link_doctype: "Customer",
					link_name: frm.doc.customer,
				},
			};
		});
		frm.set_query("address", "custom_ship_to", () => {
			if (!frm.doc.customer) {
				return { filters: { name: "" } };
			}
			return {
				query: "frappe.contacts.doctype.address.address.address_query",
				filters: {
					link_doctype: "Customer",
					link_name: frm.doc.customer,
				},
			};
		});
	},

	customer(frm) {
		if (frm.doc.custom_bill_to) {
			frm.set_value("custom_bill_to", null);
		}
		(frm.doc.custom_ship_to || []).forEach((row) => {
			frappe.model.set_value(row.doctype, row.name, "address", null);
		});
	},

	custom_order_qty_kg(frm) {
		frm.trigger("calc_order_value");
	},

	custom_rate_per_kg(frm) {
		frm.trigger("calc_order_value");
	},

	calc_order_value(frm) {
		const qty = flt(frm.doc.custom_order_qty_kg);
		const rate = flt(frm.doc.custom_rate_per_kg);
		frm.set_value("custom_order_value", qty * rate);
	},
});
