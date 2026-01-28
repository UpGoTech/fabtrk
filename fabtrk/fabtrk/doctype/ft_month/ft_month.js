// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Month", {
// 	refresh(frm) {

// 	},
// });



// month doctype me sort filed ke liye yeh code hai abhi hide hai filed
// frappe.ui.form.on('FT Month', {
//     month(frm) {
//         if (!frm.doc.month) {
//             frm.set_value('month_order', '');
//             return;
//         }

//         const month_map = {
//             january: "1",
//             february: "2",
//             march: "3",
//             april: "4",
//             may: "5",
//             june: "6",
//             july: "7",
//             august: "8",
//             september: "9",
//             october: "10",
//             november: "11",
//             december: "12"
//         };

//         const m = frm.doc.month.trim().toLowerCase();

//         if (month_map[m]) {
//             frm.set_value('month_order', month_map[m]);
//         } else {
//             frm.set_value('month_order', '');
//             // frappe.msgprint(__('Please enter valid month name (January–December)'));
//         }
//     }
// });
