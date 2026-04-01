// frappe.listview_settings['FT Stock RM List'] = {
//     refresh: function(listview) {
//         listview.page.add_inner_button('Export', function() {
//             window.location.href =
//                 '/api/method/fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.export_with_value';
//         });
//     }
// };

frappe.listview_settings['FT Stock RM List'] = {
    refresh: function(listview) {

        listview.page.add_inner_button('Export', function() {
            window.location.href =
                '/api/method/fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.export_with_value';
        });

        listview.page.add_inner_button('Import', function() {

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
                            <div style="font-weight:500; font-size:15px; color:var(--color-text-primary); line-height:1.3;">Import Stock RM List</div>
                            <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400; line-height:1.3;">Excel file se data import karo</div>
                        </div>
                    </div>
                `,
                fields: [
                    {
                        fieldname: 'dialog_html',
                        fieldtype: 'HTML',
                        options: `
                        <div id="import-dialog-root">

                            <!-- Drop Zone -->
                            <div id="drop-zone" style="
                                border: 1.5px dashed #b8b8c0;
                                border-radius: 12px;
                                background: rgba(232, 231, 225, 0.5);
                                padding: 2rem 1rem;
                                text-align: center;
                                margin-bottom: 14px;
                                cursor: pointer;
                            ">
                                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5" style="display:block; margin:0 auto 10px;">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                    <polyline points="14 2 14 8 20 8"/>
                                    <line x1="12" y1="18" x2="12" y2="12"/>
                                    <line x1="9" y1="15" x2="15" y2="15"/>
                                </svg>
                                <div id="drop-text" style="font-size:14px; font-weight:500; color:var(--color-text-primary); margin-bottom:4px;">Excel file yahan drop karo</div>
                                <div style="font-size:12px; color:var(--color-text-secondary); margin-bottom:14px;">ya button se select karo</div>
                                <button id="choose-file-btn" style="
                                    background: #ffffff;
                                    border: 0.5px solid #C0C0B8;
                                    border-radius: 8px;
                                    padding: 7px 20px;
                                    font-size: 13px;
                                    cursor: pointer;
                                    color: var(--color-text-primary);
                                ">File Choose karo</button>
                                <input type="file" id="file-input" accept=".xlsx" style="display:none;" />
                            </div>

                            <!-- Note -->
                            <div style="background:#EBF5FF; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
                                <div style="font-size:12px; color:#1D4ED8; line-height:1.7;">
                                    <strong>Note:</strong> Sirf .xlsx format support hai
                                    &nbsp;·&nbsp; Grade value automatically match hogi
                                    &nbsp;·&nbsp; Duplicate records skip honge
                                </div>
                            </div>

                            <!-- Supported Fields -->
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:12px; color:var(--color-text-secondary); margin-bottom:20px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <div style="width:7px; height:7px; border-radius:50%; background:#888; flex-shrink:0;"></div>
                                    Section / Plate
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <div style="width:7px; height:7px; border-radius:50%; background:#888; flex-shrink:0;"></div>
                                    Grade auto-link
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <div style="width:7px; height:7px; border-radius:50%; background:#888; flex-shrink:0;"></div>
                                    KG / Meter
                                </div>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <div style="width:7px; height:7px; border-radius:50%; background:#888; flex-shrink:0;"></div>
                                    Computed name auto
                                </div>
                            </div>

                            <!-- Buttons -->
                            <div style="display:flex; gap:10px;">
                                <button id="cancel-btn" style="
                                    flex:1;
                                    background: transparent;
                                    border: 0.5px solid #C0C0B8;
                                    border-radius: 8px;
                                    padding: 10px;
                                    font-size: 14px;
                                    cursor: pointer;
                                    color: var(--color-text-secondary);
                                ">Cancel</button>
                                <button id="import-btn" style="
                                    flex:2;
                                    background: rgb(20, 20, 19);
                                    border: none;
                                    border-radius: 8px;
                                    padding: 10px;
                                    font-size: 14px;
                                    font-weight: 500;
                                    cursor: pointer;
                                    color: #fff;
                                ">Import</button>
                            </div>

                        </div>
                        `
                    }
                ]
            });

            // ✅ Frappe default footer hide
            d.$wrapper.find('.modal-footer').hide();

            d.show();

            setTimeout(function() {

                let dropZone  = document.getElementById('drop-zone');
                let fileInput = document.getElementById('file-input');
                let dropText  = document.getElementById('drop-text');

                // Cancel
                document.getElementById('cancel-btn').addEventListener('click', function() {
                    d.hide();
                });

                // Choose file button
                document.getElementById('choose-file-btn').addEventListener('click', function(e) {
                    e.stopPropagation();
                    fileInput.click();
                });

                // Drop zone click
                dropZone.addEventListener('click', function() {
                    fileInput.click();
                });

                // Drag over
                dropZone.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#3B82F6';
                    dropZone.style.background  = '#EBF5FF';
                });

                dropZone.addEventListener('dragleave', function() {
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background  = '';
                });

                // Drop
                dropZone.addEventListener('drop', function(e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background  = '';
                    let file = e.dataTransfer.files[0];
                    if (file) handle_file(file);
                });

                // File input change
                fileInput.addEventListener('change', function() {
                    if (fileInput.files[0]) handle_file(fileInput.files[0]);
                });

                function handle_file(file) {

                    if (!file.name.endsWith('.xlsx')) {
                        frappe.msgprint({
                            title: 'Wrong Format',
                            message: 'Sirf .xlsx file allowed hai.',
                            indicator: 'orange'
                        });
                        return;
                    }

                    dropText.textContent       = 'Uploading: ' + file.name + '...';
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
                            selected_file_url          = res.message.file_url;
                            dropText.textContent       = '✓ Ready: ' + file.name;
                            dropZone.style.borderColor = '#1D9E75';
                        } else {
                            dropText.textContent       = 'Excel file yahan drop karo';
                            dropZone.style.borderColor = '#C0C0B8';
                            dropZone.style.borderStyle = 'dashed';
                            frappe.msgprint({
                                title: 'Upload Error',
                                message: 'File upload nahi hui. Dobara try karo.',
                                indicator: 'red'
                            });
                        }
                    })
                    .catch(function() {
                        dropText.textContent       = 'Excel file yahan drop karo';
                        dropZone.style.borderColor = '#C0C0B8';
                        dropZone.style.borderStyle = 'dashed';
                        frappe.msgprint({
                            title: 'Upload Error',
                            message: 'Network error. Dobara try karo.',
                            indicator: 'red'
                        });
                    });
                }

                // Import button
                document.getElementById('import-btn').addEventListener('click', function() {

                    if (!selected_file_url) {
                        frappe.msgprint({
                            title: 'File Missing',
                            message: 'Pehle Excel file select karo.',
                            indicator: 'orange'
                        });
                        return;
                    }

                    let btn         = document.getElementById('import-btn');
                    btn.textContent = 'Importing...';
                    btn.disabled    = true;

                    frappe.call({
                        method: 'fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.import_with_value',
                        args: { file_url: selected_file_url },
                        freeze: true,
                        freeze_message: 'Import ho raha hai...',
                        callback: function(r) {
                            btn.textContent = 'Import Karo';
                            btn.disabled    = false;
                            if (r.message) {
                                frappe.msgprint({
                                    title: 'Import Complete',
                                    message: r.message.replace(/\n/g, '<br>'),
                                    indicator: r.message.includes('❌') ? 'red'
                                             : r.message.includes('⚠️') ? 'orange'
                                             : 'green'
                                });
                                listview.refresh();
                                d.hide();
                            }
                        }
                    });
                });

            }, 300);
        });
    }
};


