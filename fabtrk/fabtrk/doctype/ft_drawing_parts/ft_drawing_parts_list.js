// //export button added form list view
// frappe.listview_settings["FT Drawing Parts"] = {
//     onload(listview) {

//         // ── Export ──────────────────────────────────────
//         listview.page.add_inner_button("Export", function () {
//             window.location.href = '/api/method/fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.export_with_value';
//         });

//         // ── Import ──────────────────────────────────────
//         listview.page.add_inner_button('Import', function () {

//             let selected_file_url = null;

//             let d = new frappe.ui.Dialog({
//                 title: `
//                     <div style="display:flex; align-items:center; gap:10px;">
//                         <div style="width:36px; height:36px; border-radius:8px; background:#EBF5FF; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
//                             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2">
//                                 <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
//                                 <polyline points="17 8 12 3 7 8"/>
//                                 <line x1="12" y1="3" x2="12" y2="15"/>
//                             </svg>
//                         </div>
//                         <div>
//                             <div style="font-weight:500; font-size:15px; color:var(--color-text-primary);">Import Drawing Parts</div>
//                             <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400;">Importing data from excel/csv file</div>
//                         </div>
//                     </div>
//                 `,
//                 fields: [{
//                     fieldname: 'dialog_html',
//                     fieldtype: 'HTML',
//                     options: `
//                     <div id="dp-import-root">
//                         <div class="dp-drop-zone" style="border:1.5px dashed #C0C0B8; border-radius:12px; background:#F9FAFB; padding:2rem 1rem; text-align:center; margin-bottom:14px; cursor:pointer;">
//                             <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5" style="display:block; margin:0 auto 10px;">
//                                 <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
//                                 <polyline points="14 2 14 8 20 8"/>
//                                 <line x1="12" y1="18" x2="12" y2="12"/>
//                                 <line x1="9" y1="15" x2="15" y2="15"/>
//                             </svg>
//                             <div class="dp-drop-text" style="font-size:14px; font-weight:500; color:var(--color-text-primary); margin-bottom:4px;">Upload Excel or CSV File</div>
//                             <div style="font-size:12px; color:var(--color-text-secondary); margin-bottom:14px;">Drag & drop your file here, or click below to browse</div>
//                             <label class="dp-choose-btn" style="display:inline-block; background: var(--color-background-primary); border: 0.5px solid #C0C0B8; border-radius: 8px; padding: 7px 20px; font-size: 13px; cursor: pointer; color: var(--color-text-primary);">Choose File</label>
//                             <input type="file" class="dp-file-input" accept=".xlsx,.csv" style="display:none;" />
//                         </div>

//                         <div style="background:#EBF5FF; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
//                             <div style="font-size:12px; color:#1D4ED8; line-height:1.7;">
//                                 <strong>Note:</strong> .xlsx & .csv support &nbsp;·&nbsp; Unmatched columns → manual mapping dialog
//                             </div>
//                         </div>

//                         <div style="display:flex; gap:10px;">
//                             <button class="dp-cancel-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">Cancel</button>
//                             <button class="dp-import-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">Import</button>
//                         </div>
//                     </div>
//                     `
//                 }]
//             });

//             d.$wrapper.find('.modal-footer').hide();
//             d.show();

//             // ✅ KEY FIX: d.$wrapper.find() se sirf IS dialog ke elements milenge
//             d.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

//                 selected_file_url = null;

//                 // ✅ d.$wrapper.find() — ID ki jagah class use karo, scope current dialog
//                 let $dropZone  = d.$wrapper.find('.dp-drop-zone');
//                 let $dropText  = d.$wrapper.find('.dp-drop-text');
//                 let $chooseBtn = d.$wrapper.find('.dp-choose-btn');
//                 let $fileInput = d.$wrapper.find('.dp-file-input');

//                 let dropZone  = $dropZone[0];
//                 let fileInput = $fileInput[0];

//                 function reset_dropzone() {
//                     $dropText.text('Upload Excel or CSV File');
//                     dropZone.style.borderColor  = '#C0C0B8';
//                     dropZone.style.borderStyle  = 'dashed';
//                     dropZone.style.background   = '#F9FAFB';
//                     selected_file_url = null;
//                     fileInput.value = '';
//                 }

//                 function handle_file(file) {
//                     if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.csv')) {
//                         frappe.msgprint({ title: 'Wrong Format', message: 'Sirf .xlsx ya .csv file allowed hai.', indicator: 'orange' });
//                         return;
//                     }

//                     $dropText.text('Uploading: ' + file.name + '...');
//                     dropZone.style.borderColor = '#3B82F6';
//                     dropZone.style.borderStyle = 'solid';

//                     let formData = new FormData();
//                     formData.append('file', file, file.name);
//                     formData.append('is_private', '1');
//                     formData.append('folder', 'Home/Attachments');

//                     fetch('/api/method/upload_file', {
//                         method: 'POST',
//                         headers: { 'X-Frappe-CSRF-Token': frappe.csrf_token },
//                         body: formData
//                     })
//                         .then(r => r.json())
//                         .then(res => {
//                             if (res.message && res.message.file_url) {
//                                 selected_file_url = res.message.file_url;
//                                 $dropText.text('✓ Ready: ' + file.name);
//                                 dropZone.style.borderColor = '#1D9E75';
//                                 dropZone.style.borderStyle = 'solid';
//                             } else {
//                                 reset_dropzone();
//                                 frappe.msgprint({ title: 'Upload Error', message: 'File upload nahi hui.', indicator: 'red' });
//                             }
//                         })
//                         .catch(function () {
//                             reset_dropzone();
//                             frappe.msgprint({ title: 'Upload Error', message: 'Network error.', indicator: 'red' });
//                         });
//                 }

//                 // ✅ jQuery .on() use karo — automatically scoped to current dialog
//                 $fileInput.on('change', function () {
//                     if (fileInput.files && fileInput.files[0]) {
//                         handle_file(fileInput.files[0]);
//                     }
//                     fileInput.value = '';
//                 });

//                 // Choose File button click — label se file input trigger
//                 $chooseBtn.on('click', function () {
//                     fileInput.value = '';
//                     fileInput.click();
//                 });

//                 // Cancel button
//                 d.$wrapper.find('.dp-cancel-btn').on('click', function () {
//                     reset_dropzone();
//                     d.hide();
//                 });

//                 // Dropzone click (empty area)
//                 $dropZone.on('click', function (e) {
//                     if ($(e.target).hasClass('dp-choose-btn') || $(e.target).closest('.dp-choose-btn').length) return;
//                     fileInput.value = '';
//                     fileInput.click();
//                 });

//                 // Drag & Drop
//                 $dropZone.on('dragover', function (e) {
//                     e.preventDefault();
//                     dropZone.style.borderColor = '#3B82F6';
//                     dropZone.style.background  = '#EBF5FF';
//                 });
//                 $dropZone.on('dragleave', function () {
//                     dropZone.style.borderColor = '#C0C0B8';
//                     dropZone.style.background  = '#F9FAFB';
//                 });
//                 $dropZone.on('drop', function (e) {
//                     e.preventDefault();
//                     dropZone.style.borderColor = '#C0C0B8';
//                     dropZone.style.background  = '#F9FAFB';
//                     let dt = e.originalEvent.dataTransfer;
//                     if (dt && dt.files[0]) handle_file(dt.files[0]);
//                 });

//                 // Import button
//                 d.$wrapper.find('.dp-import-btn').on('click', function () {
//                     if (!selected_file_url) {
//                         frappe.msgprint({ title: 'File Missing', message: 'Pehle file select karo.', indicator: 'orange' });
//                         return;
//                     }

//                     let $btn = d.$wrapper.find('.dp-import-btn');
//                     $btn.text('Checking...').prop('disabled', true);

//                     frappe.call({
//                         method: 'fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.get_file_headers',
//                         args: { file_url: selected_file_url },
//                         callback: function (r) {
//                             $btn.text('Import').prop('disabled', false);
//                             if (!r.message) return;

//                             let { unmatched, all_fields } = r.message;
//                             if (unmatched && unmatched.length > 0) {
//                                 d.hide();
//                                 show_mapping_dialog(unmatched, all_fields, selected_file_url, listview, d);
//                             } else {
//                                 run_import(selected_file_url, null, $btn[0], listview, d);
//                             }
//                         }
//                     });
//                 });
//             });

//         });
//     }
// };

// // ── Mapping Dialog ───────────────────────────────────
// function show_mapping_dialog(unmatched_columns, all_fields, file_url, listview, upload_dialog) {

//     let field_options = all_fields.map(f =>
//         `<option value="${f.fieldname}">${f.label} (${f.fieldname})</option>`
//     ).join('');

//     let mapping_rows = unmatched_columns.map(col => `
//         <tr style="border-bottom: 1px solid #f0f0f0;">
//             <td style="padding: 10px; font-size:13px; color:#000; font-weight:500; width:45%;">
//                 <span>
//                     ${col}
//                 </span>
//             </td>
//             <td style="padding: 10px 8px; text-align:center; color:#9CA3AF; font-size:18px;">→</td>
//             <td style="padding: 10px 8px; width:45%;">
//                 <select data-excel-col="${col}"
//                     style="width:100%; padding:6px 10px; border:1px solid #D1D5DB; border-radius:6px; font-size:12px; background:#fff; color:var(--color-text-primary);">
//                     <option value=""> Don't Import </option>
//                     ${field_options}
//                 </select>
//             </td>
//         </tr>
//     `).join('');

//     let map_dialog = new frappe.ui.Dialog({
//         title: `
//             <div style="display:flex; align-items:center; gap:10px;">
//                 <div style="width:36px; height:36px; border-radius:8px; background:#FEF3C7; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
//                     <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2">
//                         <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
//                         <line x1="12" y1="9" x2="12" y2="13"/>
//                         <line x1="12" y1="17" x2="12.01" y2="17"/>
//                     </svg>
//                 </div>
//                 <div>
//                     <div style="font-weight:500; font-size:15px; color:var(--color-text-primary);">Column Mapping Required</div>
//                     <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400;">${unmatched_columns.length} column(s) match nahi hue — correct field select karo</div>
//                 </div>
//             </div>
//         `,
//         fields: [{
//             fieldname: 'mapping_html',
//             fieldtype: 'HTML',
//             options: `
//             <div style="margin-bottom:14px;">
//                 <div style="background:#FEF3C7; border-radius:8px; padding:10px 14px; margin-bottom:16px; border:1px solid #FCD34D;">
//                     <div style="font-size:12px; color:#92400E; line-height:1.7;">
//                         <strong>⚠️ Yeh columns match nahi hue:</strong> Har column ke liye correct Frappe field select karo.
//                         "Don't Import" select karne par wo column skip ho jayega.
//                         <br><strong style="color:#DC2626;">Note: Koi bhi data tab tak import nahi hoga jab tak sab columns map ya skip nahi ho jaate.</strong>
//                     </div>
//                 </div>
//                 <div style="border:1px solid #E5E7EB; border-radius:8px; overflow:hidden; margin-bottom:16px;">
//                     <div style="background:#F9FAFB; padding:8px 12px; border-bottom:1px solid #E5E7EB;">
//                         <div style="display:grid; grid-template-columns:1fr 40px 1fr; font-size:11px; font-weight:600; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">
//                             <span>Excel Column</span>
//                             <span></span>
//                             <span>Frappe Field</span>
//                         </div>
//                     </div>
//                     <table style="width:100%; border-collapse:collapse; background:#fff;">
//                         ${mapping_rows}
//                     </table>
//                 </div>
//                 <div style="display:flex; gap:10px;">
//                     <button class="map-back-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">
//                         ← Back
//                     </button>
//                     <button class="map-confirm-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">
//                         Confirm & Import
//                     </button>
//                 </div>
//             </div>
//             `
//         }]
//     });

//     map_dialog.$wrapper.find('.modal-footer').hide();
//     map_dialog.show();

//     // ✅ map_dialog.$wrapper.find() — scoped to this dialog only
//     map_dialog.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

//         map_dialog.$wrapper.find('.map-back-btn').on('click', function () {
//             map_dialog.hide();
//             upload_dialog.show();
//         });

//         map_dialog.$wrapper.find('.map-confirm-btn').on('click', function () {
//             let custom_mapping = {};

//             map_dialog.$wrapper.find('[data-excel-col]').each(function () {
//                 let excel_col = $(this).attr('data-excel-col');
//                 let fieldname = $(this).val();
//                 if (fieldname) custom_mapping[excel_col] = fieldname;
//             });

//             let $btn = map_dialog.$wrapper.find('.map-confirm-btn');
//             $btn.text('Importing...').prop('disabled', true);

//             run_import(file_url, custom_mapping, $btn[0], listview, map_dialog);
//         });
//     });
// }

// // ── Run Import ───────────────────────────────────────
// function run_import(file_url, custom_mapping, btn, listview, dialog) {
//     frappe.call({
//         method: 'fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.import_with_value',
//         args: {
//             file_url: file_url,
//             custom_mapping: custom_mapping ? JSON.stringify(custom_mapping) : null
//         },
//         freeze: true,
//         freeze_message: 'Importing...',
//         callback: function (r) {
//             if (btn) {
//                 btn.textContent = 'Confirm & Import';
//                 btn.disabled = false;
//             }
//             if (r.message) {
//                 frappe.msgprint({
//                     title: 'Import Complete',
//                     message: r.message.replace(/\n/g, '<br>'),
//                     indicator: r.message.includes('❌') ? 'red'
//                         : r.message.includes('⚠️') ? 'orange'
//                             : 'green'
//                 });
//                 listview.refresh();
//                 dialog.hide();
//             }
//         }
//     });
// }



// FT Drawing Parts — List View Settings (Export / Import)
frappe.listview_settings["FT Drawing Parts"] = {
    onload(listview) {

        // ── Export Button ──────────────────────────────────────
        listview.page.add_inner_button("Export", function () {
            window.location.href = '/api/method/fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.export_with_value';
        });

        // ── Import Button ──────────────────────────────────────
        listview.page.add_inner_button('Import', function () {

            let selected_file_url = null;

            let d = new frappe.ui.Dialog({
                title: `
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:36px; height:36px; border-radius:8px; background:#EBF5FF; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="17 8 12 3 7 8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                        </div>
                        <div>
                            <div style="font-weight:500; font-size:15px; color:var(--color-text-primary);">Import Drawing Parts</div>
                            <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400;">Import data from Excel or CSV file</div>
                        </div>
                    </div>
                `,
                fields: [{
                    fieldname: 'dialog_html',
                    fieldtype: 'HTML',
                    options: `
                    <div id="dp-import-root">
                        <div class="dp-drop-zone" style="border:1.5px dashed #C0C0B8; border-radius:12px; background:#F9FAFB; padding:2rem 1rem; text-align:center; margin-bottom:14px; cursor:pointer;">
                            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5" style="display:block; margin:0 auto 10px;">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                                <line x1="12" y1="18" x2="12" y2="12"/>
                                <line x1="9" y1="15" x2="15" y2="15"/>
                            </svg>
                            <div class="dp-drop-text" style="font-size:14px; font-weight:500; color:var(--color-text-primary); margin-bottom:4px;">Upload Excel or CSV File</div>
                            <div style="font-size:12px; color:var(--color-text-secondary); margin-bottom:14px;">Drag & drop your file here, or click below to browse</div>
                            <label class="dp-choose-btn" style="display:inline-block; background: var(--color-background-primary); border: 0.5px solid #C0C0B8; border-radius: 8px; padding: 7px 20px; font-size: 13px; cursor: pointer; color: var(--color-text-primary);">Choose File</label>
                            <input type="file" class="dp-file-input" accept=".xlsx,.csv" style="display:none;" />
                        </div>

                        <div style="background:#EBF5FF; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
                            <div style="font-size:12px; color:#1D4ED8; line-height:1.7;">
                                <strong>Note:</strong> Supported formats: .xlsx and .csv &nbsp;·&nbsp; Unmatched columns will prompt a mapping dialog
                            </div>
                        </div>

                        <div style="display:flex; gap:10px;">
                            <button class="dp-cancel-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">Cancel</button>
                            <button class="dp-import-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">Import</button>
                        </div>
                    </div>
                    `
                }]
            });

            d.$wrapper.find('.modal-footer').hide();
            d.show();

            d.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

                selected_file_url = null;

                let $dropZone  = d.$wrapper.find('.dp-drop-zone');
                let $dropText  = d.$wrapper.find('.dp-drop-text');
                let $chooseBtn = d.$wrapper.find('.dp-choose-btn');
                let $fileInput = d.$wrapper.find('.dp-file-input');

                let dropZone  = $dropZone[0];
                let fileInput = $fileInput[0];

                function reset_dropzone() {
                    $dropText.text('Upload Excel or CSV File');
                    dropZone.style.borderColor  = '#C0C0B8';
                    dropZone.style.borderStyle  = 'dashed';
                    dropZone.style.background   = '#F9FAFB';
                    selected_file_url = null;
                    fileInput.value = '';
                }

                function handle_file(file) {
                    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.csv')) {
                        frappe.msgprint({ title: 'Invalid Format', message: 'Only .xlsx or .csv files are allowed.', indicator: 'orange' });
                        return;
                    }

                    $dropText.text('Uploading: ' + file.name + '...');
                    dropZone.style.borderColor = '#3B82F6';
                    dropZone.style.borderStyle = 'solid';

                    let formData = new FormData();
                    formData.append('file', file, file.name);
                    formData.append('is_private', '1');
                    formData.append('folder', 'Home/Attachments');

                    fetch('/api/method/upload_file', {
                        method: 'POST',
                        headers: { 'X-Frappe-CSRF-Token': frappe.csrf_token },
                        body: formData
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.message && res.message.file_url) {
                                selected_file_url = res.message.file_url;
                                $dropText.text('✓ Ready: ' + file.name);
                                dropZone.style.borderColor = '#1D9E75';
                                dropZone.style.borderStyle = 'solid';
                            } else {
                                reset_dropzone();
                                frappe.msgprint({ title: 'Upload Failed', message: 'File upload failed. Please try again.', indicator: 'red' });
                            }
                        })
                        .catch(function () {
                            reset_dropzone();
                            frappe.msgprint({ title: 'Upload Error', message: 'Network error occurred.', indicator: 'red' });
                        });
                }

                $fileInput.on('change', function () {
                    if (fileInput.files && fileInput.files[0]) {
                        handle_file(fileInput.files[0]);
                    }
                    fileInput.value = '';
                });

                $chooseBtn.on('click', function () {
                    fileInput.value = '';
                    fileInput.click();
                });

                d.$wrapper.find('.dp-cancel-btn').on('click', function () {
                    reset_dropzone();
                    d.hide();
                });

                $dropZone.on('click', function (e) {
                    if ($(e.target).hasClass('dp-choose-btn') || $(e.target).closest('.dp-choose-btn').length) return;
                    fileInput.value = '';
                    fileInput.click();
                });

                $dropZone.on('dragover', function (e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#3B82F6';
                    dropZone.style.background  = '#EBF5FF';
                });
                $dropZone.on('dragleave', function () {
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background  = '#F9FAFB';
                });
                $dropZone.on('drop', function (e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background  = '#F9FAFB';
                    let dt = e.originalEvent.dataTransfer;
                    if (dt && dt.files[0]) handle_file(dt.files[0]);
                });

                d.$wrapper.find('.dp-import-btn').on('click', function () {
                    if (!selected_file_url) {
                        frappe.msgprint({ title: 'No File Selected', message: 'Please select a file first.', indicator: 'orange' });
                        return;
                    }

                    let $btn = d.$wrapper.find('.dp-import-btn');
                    $btn.text('Checking...').prop('disabled', true);

                    frappe.call({
                        method: 'fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.get_file_headers',
                        args: { file_url: selected_file_url },
                        callback: function (r) {
                            $btn.text('Import').prop('disabled', false);
                            if (!r.message) return;

                            let { unmatched, all_fields } = r.message;
                            if (unmatched && unmatched.length > 0) {
                                d.hide();
                                show_mapping_dialog(unmatched, all_fields, selected_file_url, listview, d);
                            } else {
                                run_import(selected_file_url, null, $btn[0], listview, d);
                            }
                        }
                    });
                });
            });

        });
    }
};


// PORTAL-BASED DROPDOWN — Opens in <body>, never clipped by dialog overflow
// Global portal element — ek hi baar banao
let $dp_portal = null;
let dp_active_dd = null;   // currently open .dp-custom-dd element

function get_portal() {
    if (!$dp_portal) {
        $dp_portal = $(`
            <div id="dp-dd-portal" style="
                position: fixed;
                z-index: 99999;
                display: none;
                background: #fff;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                overflow: hidden;
            ">
                <div style="padding:6px 8px; border-bottom:1px solid #f0f0f0; background:#fff;">
                    <input id="dp-portal-search" type="text" placeholder="Search fields..." style="
                        width:100%; padding:5px 8px; border:1px solid #E5E7EB; border-radius:4px;
                        font-size:12px; outline:none; box-sizing:border-box;
                    " />
                </div>
                <div id="dp-portal-options" style="max-height:220px; overflow-y:auto;"></div>
            </div>
        `).appendTo('body');

        // Search handler
        $dp_portal.on('input', '#dp-portal-search', function () {
            let q = $(this).val().toLowerCase();
            $dp_portal.find('.dp-portal-opt').each(function () {
                $(this).toggle($(this).text().toLowerCase().includes(q));
            });
        });

        // Option select handler
        $dp_portal.on('click', '.dp-portal-opt', function (e) {
            e.stopPropagation();
            if (!dp_active_dd) return;

            let val      = $(this).data('value');
            let labelTxt = $(this).find('.dp-opt-label').text();
            let subTxt   = $(this).find('.dp-opt-sub').text();
            let hasSub   = ($(this).find('.dp-opt-sub').length > 0 && val !== '');

            let $dd = $(dp_active_dd);
            $dd.data('selected-value', val);

            if (hasSub) {
                $dd.find('.dp-dd-trigger').html(`
                    <div style="line-height:1.3;">
                        <div style="font-size:13px; color:var(--color-text-primary);">${labelTxt}</div>
                        <div style="font-size:11px; color:#9CA3AF; font-family:monospace,'Courier New',sans-serif;">${subTxt}</div>
                    </div>
                `).css('color', 'var(--color-text-primary)');
            } else {
                $dd.find('.dp-dd-trigger').html(`<span>${labelTxt}</span>`).css('color', '#6B7280');
            }

            $dd.find('.dp-dd-trigger').css('border-color', val ? '#1D9E75' : '#D1D5DB');
            close_portal();
        });

        // Prevent search click from closing
        $dp_portal.on('click', '#dp-portal-search', function (e) { e.stopPropagation(); });

        // Close on outside click
        $(document).on('click.dp_portal_global', function (e) {
            if (
                $dp_portal &&
                !$dp_portal.is(':hidden') &&
                !$dp_portal[0].contains(e.target) &&
                !(dp_active_dd && dp_active_dd.contains(e.target))
            ) {
                close_portal();
            }
        });
    }
    return $dp_portal;
}

function close_portal() {
    if ($dp_portal) {
        $dp_portal.hide();
    }
    dp_active_dd = null;
}

function open_portal($dd, all_fields) {
    let portal = get_portal();

    // Populate options
    let $opts = portal.find('#dp-portal-options');
    $opts.empty();

    // Don't Import option
    $opts.append(`
        <div class="dp-portal-opt" data-value="" style="padding:8px 12px; cursor:pointer; border-bottom:1px solid #f0f0f0;">
            <div class="dp-opt-label" style="font-size:13px; color:#6B7280;">Don't Import</div>
        </div>
    `);

    let selectedVal = $dd.data('selected-value') || '';

    all_fields.forEach(function (f) {
        let label     = f.label || f.fieldname;
        let fieldname = f.fieldname;
        let showSub   = (label !== fieldname);
        let isSelected = (fieldname === selectedVal);

        let subHtml = showSub
            ? `<div class="dp-opt-sub" style="font-size:11px; color:#9CA3AF; margin-top:1px; font-family:monospace,'Courier New',sans-serif;">${fieldname}</div>`
            : '';

        $opts.append(`
            <div class="dp-portal-opt" data-value="${fieldname}" style="
                padding:8px 12px; cursor:pointer; border-bottom:1px solid #f0f0f0;
                background: ${isSelected ? '#EFF6FF' : '#fff'};
            ">
                <div class="dp-opt-label" style="font-size:13px; color:var(--color-text-primary);">${label}</div>
                ${subHtml}
            </div>
        `);
    });

    // Hover effect
    $opts.find('.dp-portal-opt').on('mouseenter', function () {
        let v = $(this).data('value');
        if (v !== selectedVal) $(this).css('background', '#F9FAFB');
    }).on('mouseleave', function () {
        let v = $(this).data('value');
        $(this).css('background', v === selectedVal ? '#EFF6FF' : '#fff');
    });

    // Position: Smart dropup/dropdown
    let trigger     = $dd.find('.dp-dd-trigger')[0];
    let rect        = trigger.getBoundingClientRect();
    let portalH     = 280; // estimated max height
    let spaceBelow  = window.innerHeight - rect.bottom;
    let spaceAbove  = rect.top;
    let portalW     = Math.max(rect.width, 240);

    portal.css({
        width:   portalW + 'px',
        display: 'block',
        left:    rect.left + 'px',
    });

    if (spaceBelow >= 220 || spaceBelow >= spaceAbove) {
        // Open downward
        portal.css({ top: (rect.bottom + 4) + 'px', bottom: 'auto' });
    } else {
        // Open upward (dropup)
        portal.css({ top: 'auto', bottom: (window.innerHeight - rect.top + 4) + 'px' });
    }

    // Clear search & focus
    portal.find('#dp-portal-search').val('').trigger('input');
    setTimeout(function () { portal.find('#dp-portal-search').focus(); }, 50);

    dp_active_dd = $dd[0];
}

// BUILD MAPPING DROPDOWN TRIGGER — only trigger HTML, list is in portal
function build_mapping_dropdown(all_fields, excel_col) {
    return `
        <div class="dp-custom-dd" data-excel-col="${excel_col}" style="position:relative; width:100%;">
            <div class="dp-dd-trigger" style="
                width:100%;
                padding:7px 30px 7px 10px;
                border:1px solid #D1D5DB;
                border-radius:6px;
                font-size:13px;
                background:#fff;
                color:#6B7280;
                cursor:pointer;
                min-height:36px;
                box-sizing:border-box;
                display:flex;
                align-items:center;
                user-select:none;
            ">Don't Import</div>
            <svg class="dp-dd-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2.5" style="
                position:absolute; right:10px; top:50%; transform:translateY(-50%); pointer-events:none; transition:transform 0.2s;
            "><polyline points="6 9 12 15 18 9"/></svg>
        </div>
    `;
}


// MAPPING DIALOG
function show_mapping_dialog(unmatched_columns, all_fields, file_url, listview, upload_dialog) {

    let proper_rows = '';
    unmatched_columns.forEach(function (col) {
        proper_rows += `
            <tr style="border-bottom:1px solid #f0f0f0;">
                <td style="padding:12px 10px; font-size:13px; color:#171717; font-weight:500; width:38%; vertical-align:middle;">
                    <span>${col}</span>
                </td>
                <td style="padding:12px 8px; text-align:center; color:#D1D5DB; font-size:16px; width:5%; vertical-align:middle;">→</td>
                <td style="padding:6px; width:57%; vertical-align:middle;">
                    ${build_mapping_dropdown(all_fields, col)}
                </td>
            </tr>
        `;
    });

    let map_dialog = new frappe.ui.Dialog({
        title: `
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; border-radius:8px; background:#FEF3C7; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                </div>
                <div>
                    <div style="font-weight:500; font-size:15px; color:var(--color-text-primary);">Map Columns</div>
                    <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400;">${unmatched_columns.length} column(s) could not be matched automatically</div>
                </div>
            </div>
        `,
        fields: [{
            fieldname: 'mapping_html',
            fieldtype: 'HTML',
            options: `
            <div class="dp-mapping-container" style="margin-bottom:14px;">
                <div style="background:#FEF3C7; border-radius:8px; padding:12px 14px; margin-bottom:16px; border:1px solid #FCD34D;">
                    <div style="font-size:12px; color:#92400E; line-height:1.8;">
                        <strong>⚠️ Action Required:</strong> The following columns could not be automatically matched.
                        Select the correct Frappe field for each column, or choose "Don't Import" to skip it.
                    </div>
                </div>
                <div style="border:1px solid #E5E7EB; border-radius:8px; overflow:hidden; margin-bottom:16px;">
                    <div style="background:#F9FAFB; padding:10px 12px; border-bottom:1px solid #E5E7EB;">
                        <div style="display:grid; grid-template-columns:38% 5% 57%; font-size:11px; font-weight:600; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">
                            <span>CSV Column</span>
                            <span></span>
                            <span>Map To Field</span>
                        </div>
                    </div>
                    <div style="max-height:380px; overflow-y:auto;">
                        <table style="width:100%; border-collapse:collapse; background:#fff;">
                            ${proper_rows}
                        </table>
                    </div>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="map-back-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">
                        ← Back
                    </button>
                    <button class="map-confirm-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">
                        Confirm & Import
                    </button>
                </div>
            </div>
            `
        }]
    });

    map_dialog.$wrapper.find('.modal-footer').hide();
    map_dialog.$wrapper.find('.modal-dialog').css({
        'width': '720px',
        'max-width': '92vw'
    });

    map_dialog.show();

    map_dialog.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

        let $all_dd = map_dialog.$wrapper.find('.dp-custom-dd');

        // ── Trigger click → open portal ──
        $all_dd.on('click', '.dp-dd-trigger', function (e) {
            e.stopPropagation();
            let $dd = $(this).closest('.dp-custom-dd');

            // If same dropdown clicked again → close
            if (dp_active_dd === $dd[0]) {
                close_portal();
                $dd.find('.dp-dd-arrow').css('transform', 'translateY(-50%)');
                return;
            }

            close_portal();
            open_portal($dd, all_fields);
            $dd.find('.dp-dd-arrow').css('transform', 'translateY(-50%) rotate(180deg)');
        });

        // Reset arrow when portal closes via outside click
        $(document).on('click.dp_map_arrow', function () {
            if (dp_active_dd) {
                $(dp_active_dd).find('.dp-dd-arrow').css('transform', 'translateY(-50%)');
            }
        });

        // ── Back ──
        map_dialog.$wrapper.find('.map-back-btn').on('click', function () {
            close_portal();
            $(document).off('click.dp_map_arrow');
            map_dialog.hide();
            upload_dialog.show();
        });

        // ── Confirm ──
        map_dialog.$wrapper.find('.map-confirm-btn').on('click', function () {
            close_portal();
            $(document).off('click.dp_map_arrow');

            let custom_mapping = {};
            $all_dd.each(function () {
                let col = $(this).data('excel-col');
                let val = $(this).data('selected-value') || '';
                if (val) custom_mapping[col] = val;
            });

            let $btn = map_dialog.$wrapper.find('.map-confirm-btn');
            $btn.text('Importing...').prop('disabled', true);

            run_import(file_url, custom_mapping, $btn[0], listview, map_dialog);
        });

        // Close portal when dialog hides
        map_dialog.$wrapper.on('hidden.bs.modal', function () {
            close_portal();
            $(document).off('click.dp_map_arrow');
        });
    });
}


// RUN IMPORT
function run_import(file_url, custom_mapping, btn, listview, dialog) {
    frappe.call({
        method: 'fabtrk.fabtrk.doctype.ft_drawing_parts.ft_drawing_parts.import_with_value',
        args: {
            file_url: file_url,
            custom_mapping: custom_mapping ? JSON.stringify(custom_mapping) : null
        },
        freeze: true,
        freeze_message: 'Importing data...',
        callback: function (r) {
            if (btn) {
                btn.textContent = 'Confirm & Import';
                btn.disabled = false;
            }
            if (r.message) {
                frappe.msgprint({
                    title: 'Import Complete',
                    message: r.message.replace(/\n/g, '<br>'),
                    indicator: r.message.includes('❌') ? 'red'
                        : r.message.includes('⚠️') ? 'orange'
                            : 'green'
                });
                listview.refresh();
                dialog.hide();
            }
        }
    });
}


