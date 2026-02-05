// Copyright (c) 2026, UpGo Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("FT Project", {
// 	refresh(frm) {

// 	},
// });



// // //hidden hai    /Add Drawings table ke liye  isme dublicate stock item hidden form same drawing no
// frappe.ui.form.on('FT Project', {
//     refresh(frm) {
//         set_stock_item_query(frm);
//         // 🔥 form open / refresh pe bhi total calculate
//         calculate_parent_total_weight(frm);
//     }
// });

// function set_stock_item_query(frm) {
//     frm.fields_dict.add_drawings.grid.get_field('stock_item').get_query =
//         function (doc, cdt, cdn) {

//             let row = locals[cdt][cdn];

//             // agar drawing select nahi hai → normal dropdown
//             if (!row.drawing_no) {
//                 return {};
//             }

//             // same drawing ke already selected stock items
//             let used_stock_items = doc.add_drawings
//                 .filter(d =>
//                     d.drawing_no === row.drawing_no &&
//                     d.stock_item &&
//                     d.name !== row.name   // current row ko ignore karo
//                 )
//                 .map(d => d.stock_item);

//             return {
//                 filters: [
//                     ['FT Stocks RM', 'name', 'not in', used_stock_items]
//                 ]
//             };
//         };
// }
// // /// isme dublicate stock item hidden form same drawing no



// // /// chaild tble calculation
// frappe.ui.form.on('FT Drawing Childtable', {
//     stock_item: function (frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // Qty reset / refresh
//         row.qty = 0;

//         // Total weight bhi clear ho jaye (optional but clean)
//         row.total_weight_kg = 0;

//         frm.refresh_field('add_drawings');
//         // 🔥 parent total refresh
//         calculate_parent_total_weight(frm);
//     },
//     quality_weight: function (frm, cdt, cdn) {
//         calculate_total_weight_kg(frm, cdt, cdn);
//     },

//     qty: function (frm, cdt, cdn) {
//         calculate_total_weight_kg(frm, cdt, cdn);
//     },
//      // 🔥 jab row delete ho add drawing ka
//     add_drawings_remove(frm) {
//         calculate_parent_total_weight(frm);
//     }
// });

// function calculate_total_weight_kg(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];

//     let quality_weight = flt(row.quality_weight);
//     let qty = flt(row.qty);

//     row.total_weight_kg = quality_weight * qty;

//     frm.refresh_field('add_drawings');

//     calculate_parent_total_weight(frm);
// }
// function calculate_parent_total_weight(frm) {
//     let total = 0;

//     (frm.doc.add_drawings || []).forEach(row => {
//         total += flt(row.total_weight_kg);
//     });

//     frm.set_value('total_weight_for_stock_item', total);
// }

// // Add Drawings table ke liye /// chaild tble calculation