// Export and Import buttons with dynamic file upload and column mapping for unmatched fields.
frappe.listview_settings['FT Stock RM List'] = {
    refresh: function (listview) {

        // ── Export Button ──────────────────────────────────────
        // listview.page.add_inner_button('Export', function() {
        //     window.location.href =
        //         '/api/method/fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.export_with_value';
        // });

        listview.page.add_inner_button('Export', function () {

            // Fetch doctype fields dynamically for filter UI
            frappe.model.with_doctype('FT Stock RM List', function () {
                let meta = frappe.get_meta('FT Stock RM List');
                let filterable_fields = meta.fields.filter(function (f) {
                    return !['Section Break', 'Column Break', 'HTML', 'Heading', 'Button', 'Tab Break'].includes(f.fieldtype);
                }).map(function (f) {
                    return { label: f.label || f.fieldname, fieldname: f.fieldname, fieldtype: f.fieldtype, reqd: f.reqd };
                });

                // Add standard fields
                filterable_fields.unshift({ label: 'ID', fieldname: 'name', fieldtype: 'Data', reqd: 1 });

                let export_dialog = new frappe.ui.Dialog({
                    title: `
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:36px; height:36px; border-radius:8px; background:#ECFDF5; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                            </div>
                            <div>
                                <div style="font-weight:600; font-size:15px; color:var(--color-text-primary);">Export Stock RM List</div>
                                <!-- <div style="font-size:11px; color:var(--color-text-secondary); font-weight:400;">Export data to Excel or CSV file</div> -->
                            </div>
                        </div>
                    `,
                    fields: [{
                        fieldname: 'export_dialog_html',
                        fieldtype: 'HTML',
                        options: `
                        <div id="rm-export-root" style="padding:4px 0;">
 
                            <div style="margin-bottom:14px;">
                                <label style="font-size:12px; font-weight:600; color:#000; text-transform:capitalize; letter-spacing:0.06em; display:block; margin-bottom:6px;">File Type</label>                                
                                <select id="rm-file-type" style="width:100%; padding:6px 12px; border:1px solid #D1D5DB; border-radius:8px; font-size:13px; color:var(--color-text-primary); background:#F3F3F3; cursor:pointer; outline:none;">
                                    <option value="csv">CSV</option>
                                    <option value="xlsx">Excel</option>
                                </select>
                            </div>
 
                            <div style="margin-bottom:14px;">
                                <label style="font-size:12px; font-weight:600; color:#000; text-transform:capitalize; letter-spacing:0.06em; display:block; margin-bottom:6px;">Export Type</label>                               
                                <select id="rm-export-type" style="width:100%; padding:6px 12px; border:1px solid #D1D5DB; border-radius:8px; font-size:14px; color:var(--color-text-primary); background:#F3F3F3; cursor:pointer; outline:none;">
                                    <option value="all">All Records</option>
                                    <option value="filtered">Filtered Records</option>
                                    <option value="5">5 Records</option>
                                    <option value="blank">Blank Template</option>                                    
                                </select>
                            </div>
 
                            <!-- FILTER SECTION — shown only when "Filtered Records" selected -->
                            <div id="rm-filter-section" style="display:none; margin-bottom:14px; border:1px solid #E5E7EB; border-radius:10px; overflow:visible; background:#fff;">
 
                                <!-- Record count — top of filter section -->
                                <div id="rm-filter-record-count" style="padding:10px 14px 0 14px; font-size:14px; color:#374151; font-weight:400;">
                                    <!-- e.g. 1287 records will be exported -->
                                </div>
 
                                <!-- Filter rows container -->
                                <div id="rm-filter-rows-container" style="padding:10px 14px 0 14px;">
                                    <!-- Filter rows injected here on + Add a Filter click -->
                                </div>
 
                                <!-- Empty state — shown when no rows -->
                                <div id="rm-no-filters-msg" style="padding:20px 14px; text-align:center; font-size:14px; color:#9CA3AF;">
                                    No filters selected
                                </div>
 
                                <!-- Bottom bar -->
                                <div style="padding:10px 14px; display:flex; align-items:center; justify-content:space-between; border-top:1px solid #F3F4F6; margin-top:8px;">
                                    <button id="rm-add-filter-btn" style="background:none; border:none; font-size:14px; color:#2563EB; cursor:pointer; padding:0; font-weight:500;">+ Add a Filter</button>
                                    <button id="rm-clear-filters-btn" style="background:#F3F3F3; border:1px solid #D1D5DB; border-radius:6px; font-size:13px; color:#374151; cursor:pointer; padding:6px 14px;">Clear Filters</button>
                                </div>
 
                            </div>
 
                            <div id="rm-export-info" style="border-radius:8px; padding:10px 14px; margin-bottom:16px; background:#ECFDF5;">
                                <div id="rm-export-info-text" style="font-size:13px; color:#065F46; line-height:1.7;">
                                    <strong>ℹ️</strong> All records from FT Stock RM List will be exported.
                                </div>
                            </div>
 
                            <!-- SELECT FIELDS TO INSERT -->
                            <div id="rm-fields-section" style="margin-bottom:16px;">
                                <div style="font-size:12px; font-weight:500; color:#000; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;">Select Fields to Insert</div>
 
                                <div style="display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;">                                   
                                    <button id="rm-select-all-btn" style="background:#F3F4F6; border:1px solid #E5E7EB; border-radius:6px; padding:6px 16px; font-size:13px; cursor:pointer; color:#374151; font-weight:500; transition:all 0.15s;" 
                                    onmouseover="this.style.background='#E5E7EB'; this.style.borderColor='#D1D5DB';" 
                                    onmouseout="this.style.background='#F3F4F6'; this.style.borderColor='#E5E7EB';">Select All</button>
                                    <button id="rm-select-mandatory-btn" style="background:#F3F4F6; border:1px solid #E5E7EB; border-radius:6px; padding:6px 16px; font-size:13px; cursor:pointer; color:#374151; font-weight:500; transition:all 0.15s;" 
                                        onmouseover="this.style.background='#E5E7EB'; this.style.borderColor='#D1D5DB';" 
                                        onmouseout="this.style.background='#F3F4F6'; this.style.borderColor='#E5E7EB';">Select Mandatory</button>
                                    <button id="rm-unselect-all-btn" style="background:#F3F4F6; border:1px solid #E5E7EB; border-radius:6px; padding:6px 16px; font-size:13px; cursor:pointer; color:#374151; font-weight:500; transition:all 0.15s;" 
                                        onmouseover="this.style.background='#E5E7EB'; this.style.borderColor='#D1D5DB';" 
                                        onmouseout="this.style.background='#F3F4F6'; this.style.borderColor='#E5E7EB';">Unselect All</button>
                                </div>
 
                                <div style="font-size:13px; color:#000; margin-bottom:8px; font-weight:500;">FT Stock RM List</div>
 
                                <div id="rm-fields-checkboxes" style="display:grid; grid-template-columns:1fr 1fr; max-height:200px; overflow-y:auto;">
                                    <!-- Checkboxes injected here -->
                                </div>
                            </div>
 
                            <div style="display:flex; gap:10px;">
                                <button class="rm-export-cancel-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">Cancel</button>
                                <button class="rm-export-confirm-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">Export</button>
                            </div>
 
                        </div>
                        `
                    }]
                });

                export_dialog.$wrapper.find('.modal-footer').hide();
                // ── Wider dialog ──
                export_dialog.$wrapper.find('.modal-dialog').css({ 'width': '680px', 'max-width': '96vw' });
                export_dialog.show();

                export_dialog.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

                    const $fileType = export_dialog.$wrapper.find('#rm-file-type');
                    const $exportType = export_dialog.$wrapper.find('#rm-export-type');
                    const $info = export_dialog.$wrapper.find('#rm-export-info');
                    const $infoText = export_dialog.$wrapper.find('#rm-export-info-text');
                    const $filterSec = export_dialog.$wrapper.find('#rm-filter-section');

                    const info_map = {
                        'all': { bg: '#ECFDF5', color: '#065F46', text: '<strong>ℹ️</strong> All records from FT Stock RM List will be exported.' },
                        'filtered': { bg: '#EBF5FF', color: '#1E40AF', text: '<strong>🔽</strong> Only records matching the applied filters will be exported.' },
                        '5': { bg: '#FEF3C7', color: '#92400E', text: '<strong>🔢</strong> Only the first 5 records will be exported.' },
                        'blank': { bg: '#F5F3FF', color: '#5B21B6', text: '<strong>📄</strong> No records will be exported — only column headers (blank template).' },
                    };

                    // ── Operator options based on fieldtype ──
                    function get_operators(fieldtype) {
                        let base = ['Equals', 'Not Equals', 'Like', 'Not Like', 'In', 'Not In', 'Is'];
                        if (['Int', 'Float', 'Currency', 'Percent', 'Duration'].includes(fieldtype)) {
                            return ['Equals', 'Not Equals', '>', '<', '>=', '<=', 'In', 'Not In', 'Is'];
                        } else if (fieldtype === 'Check') {
                            return ['Equals', 'Is'];
                        } else if (['Date', 'Datetime'].includes(fieldtype)) {
                            return ['Equals', 'Not Equals', '>', '<', '>=', '<=', 'Between', 'Is'];
                        } else if (fieldtype === 'Select') {
                            return ['Equals', 'Not Equals', 'In', 'Not In', 'Is'];
                        }
                        return base;
                    }

                    // ── Build one filter row ──
                    function build_filter_row(row_id) {
                        let field_options = filterable_fields.map(function (f) {
                            return `<option value="${f.fieldname}" data-fieldtype="${f.fieldtype}">${f.label}</option>`;
                        }).join('');

                        let default_ops = get_operators('Data');
                        let op_options = default_ops.map(function (op) {
                            return `<option value="${op}">${op}</option>`;
                        }).join('');

                        return `
                            <div class="rm-filter-row" data-row-id="${row_id}" style="display:flex; align-items:flex-start; gap:8px; margin-bottom:10px; flex-wrap:nowrap;">
                                <select class="rm-filter-field" style="flex:2; min-width:0; padding:7px 8px; border:1px solid #D1D5DB; border-radius:6px; font-size:13px; background:#F3F3F3; color:var(--color-text-primary); outline:none; cursor:pointer;">
                                    ${field_options}
                                </select>
                                <select class="rm-filter-operator" style="flex:1.5; min-width:0; padding:7px 8px; border:1px solid #D1D5DB; border-radius:6px; font-size:13px; background:#F3F3F3; color:var(--color-text-primary); outline:none; cursor:pointer;">
                                    ${op_options}
                                </select>
                                <div class="rm-filter-value-wrap" style="flex:2; min-width:0; position:relative;">
                                    <input class="rm-filter-value" type="text" placeholder="Value" autocomplete="off" style="width:100%; padding:7px 8px; border:1px solid #D1D5DB; border-radius:6px; font-size:13px; outline:none; color:var(--color-text-primary); background:#F3F3F3; box-sizing:border-box;" />
                                    <div class="rm-autocomplete-list" style="display:none; position:fixed; z-index:999999; background:#fff; border:1px solid #D1D5DB; border-radius:6px; box-shadow:0 4px 16px rgba(0,0,0,0.13); max-height:200px; overflow-y:auto; min-width:160px;"></div>
                                </div>
                                <button class="rm-filter-remove" data-row-id="${row_id}" style="flex-shrink:0; background:none; border:none; cursor:pointer; color:#9CA3AF; padding:7px 4px; font-size:16px; line-height:1; border-radius:4px;" title="Remove filter">✕</button>
                            </div>
                        `;
                    }

                    let filter_row_counter = 0;

                    // ── Toggle empty state visibility ──
                    function sync_empty_state() {
                        let has_rows = export_dialog.$wrapper.find('.rm-filter-row').length > 0;
                        export_dialog.$wrapper.find('#rm-no-filters-msg').toggle(!has_rows);
                    }

                    // ── Add filter row (only on button click) ──
                    function add_filter_row() {
                        filter_row_counter++;
                        let row_id = 'fr_' + filter_row_counter;
                        export_dialog.$wrapper.find('#rm-filter-rows-container').append(build_filter_row(row_id));
                        bind_filter_row_events(row_id);
                        sync_empty_state();
                        update_record_count();
                    }

                    // ── Autocomplete: fetch suggestions from DB ──
                    function fetch_suggestions(fieldname, search_text, $list, $input) {
                        let field_meta = meta.fields.find(function (f) { return f.fieldname === fieldname; });

                        // ── ID (name) field — DB se distinct values ──
                        if (fieldname === 'name') {
                            frappe.call({
                                method: 'fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.get_field_distinct_values',
                                args: { fieldname: 'name', search_text: search_text || '' },
                                callback: function (r) {
                                    render_autocomplete_list(r.message || [], $list, $input);
                                }
                            });
                            return;
                        }

                        if (!field_meta) { $list.hide(); return; }

                        // ── Select field → meta se saare options ──
                        if (field_meta.fieldtype === 'Select') {
                            let options = (field_meta.options || '').split('\n')
                                .map(function (o) { return o.trim(); })
                                .filter(function (o) {
                                    return o !== '' && (!search_text || o.toLowerCase().includes(search_text.toLowerCase()));
                                });
                            render_autocomplete_list(options, $list, $input);
                            return;
                        }

                        // ── Link field → linked doctype se fetch ──
                        if (field_meta.fieldtype === 'Link') {
                            frappe.call({
                                method: 'frappe.client.get_list',
                                args: {
                                    doctype: field_meta.options,
                                    fields: ['name'],
                                    filters: search_text ? [['name', 'like', '%' + search_text + '%']] : [],
                                    limit: 0,
                                    order_by: 'name asc'
                                },
                                callback: function (r) {
                                    let vals = (r.message || []).map(function (row) { return row.name; });
                                    render_autocomplete_list(vals, $list, $input);
                                }
                            });
                            return;
                        }

                        // ── Data / Small Text → DB se distinct values ──
                        if (['Data', 'Small Text'].includes(field_meta.fieldtype)) {
                            frappe.call({
                                method: 'fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.get_field_distinct_values',
                                args: { fieldname: fieldname, search_text: search_text || '' },
                                callback: function (r) {
                                    render_autocomplete_list(r.message || [], $list, $input);
                                }
                            });
                            return;
                        }

                        // ── Float / Int / Check / Date etc. → koi dropdown nahi ──
                        $list.hide();
                    }

                    // ── Helper: list render karo ──
                    function render_autocomplete_list(values, $list, $input) {
                        $list.empty();
                        if (!values.length) { $list.hide(); return; }

                        values.forEach(function (val) {
                            let $item = $(`
            <div style="padding:8px 12px; font-size:13px; cursor:pointer;
                color:var(--color-text-primary); border-bottom:1px solid #F3F4F6;">
                ${val}
            </div>
        `);
                            $item.on('mousedown', function (e) {
                                e.preventDefault();
                                e.stopPropagation();
                                $input.val(val);
                                $list.hide();
                                update_record_count();
                            });
                            $item.on('mouseenter', function () { $(this).css('background', '#F3F4F6'); });
                            $item.on('mouseleave', function () { $(this).css('background', '#fff'); });
                            $list.append($item);
                        });

                        let rect = $input[0].getBoundingClientRect();
                        $list.css({
                            top: (rect.bottom + 2) + 'px',
                            left: rect.left + 'px',
                            width: rect.width + 'px',
                        }).show();
                    }

                    // ── Bind events on a specific row ──
                    function bind_filter_row_events(row_id) {
                        let $row = export_dialog.$wrapper.find(`.rm-filter-row[data-row-id="${row_id}"]`);
                        let $input = $row.find('.rm-filter-value');
                        let $list = $row.find('.rm-autocomplete-list');
                        let $opSel = $row.find('.rm-filter-operator');
                        let $fieldSel = $row.find('.rm-filter-field');

                        // Field change → update operators + clear value
                        $fieldSel.on('change', function () {
                            let ft = $(this).find(':selected').data('fieldtype') || 'Data';
                            let ops = get_operators(ft);
                            $opSel.empty();
                            ops.forEach(function (op) { $opSel.append(`<option value="${op}">${op}</option>`); });
                            $input.val('');
                            $list.hide();
                            update_record_count();
                        });

                        // Operator change → hide list for Is operator (no value needed)
                        $opSel.on('change', function () {
                            let op = $(this).val();
                            if (op === 'Is') {
                                $input.val('').attr('placeholder', 'set / not set').prop('disabled', false);
                            } else if (op === 'In' || op === 'Not In') {
                                $input.attr('placeholder', 'val1, val2, ...').prop('disabled', false);
                            } else {
                                $input.attr('placeholder', 'Value').prop('disabled', false);
                            }
                            $list.hide();
                            update_record_count();
                        });

                        // Value input → autocomplete (skip for In/Not In/Is operators)

                        let ac_timer = null;
                        $input.on('input', function () {
                            let op = $opSel.val();
                            if (['In', 'Not In', 'Is'].includes(op)) { $list.hide(); return; }
                            let fieldname = $fieldSel.val();
                            let search_text = $input.val().trim();
                            clearTimeout(ac_timer);
                            ac_timer = setTimeout(function () {
                                fetch_suggestions(fieldname, search_text, $list, $input);
                            }, 250);
                        });

                        $input.on('focus', function () {
                            let op = $opSel.val();
                            if (['In', 'Not In', 'Is'].includes(op)) { $list.hide(); return; }
                            // Focus pe bhi suggestions dikhao (empty search = sab values)
                            let fieldname = $fieldSel.val();
                            let search_text = $input.val().trim();
                            clearTimeout(ac_timer);
                            ac_timer = setTimeout(function () {
                                fetch_suggestions(fieldname, search_text, $list, $input);
                            }, 150);
                        });

                        $input.on('blur', function () {
                            // Thoda delay diya taaki mousedown fire ho sake pehle
                            setTimeout(function () { $list.hide(); }, 250);
                        });

                        $input.on('change', function () { update_record_count(); });

                        $row.find('.rm-filter-remove').on('click', function () {
                            $list.hide();
                            $row.remove();
                            sync_empty_state();
                            update_record_count();
                        });
                    }

                    // ── Collect filters from UI ──
                    function collect_filters() {
                        let filters = [];
                        let equals_groups = {};  // field → [values]
                        let other_filters_list = [];

                        export_dialog.$wrapper.find('.rm-filter-row').each(function () {
                            let field = $(this).find('.rm-filter-field').val();
                            let operator = $(this).find('.rm-filter-operator').val();
                            let value = $(this).find('.rm-filter-value').val().trim();

                            let op_map = {
                                'Equals': '=', 'Not Equals': '!=',
                                'Like': 'like', 'Not Like': 'not like',
                                '>': '>', '<': '<', '>=': '>=', '<=': '<=',
                                'Between': 'between', 'In': 'in', 'Not In': 'not in',
                                'Is': 'is',
                            };
                            let frappe_op = op_map[operator] || '=';

                            if (operator === 'Is') {
                                if (value !== '') {
                                    other_filters_list.push(['FT Stock RM List', field, 'is', value]);
                                }
                                return;
                            }

                            if (!field || value === '') return;

                            if (frappe_op === 'like' || frappe_op === 'not like') {
                                if (!value.includes('%')) value = '%' + value + '%';
                                other_filters_list.push(['FT Stock RM List', field, frappe_op, value]);
                                return;
                            }

                            if (frappe_op === 'in' || frappe_op === 'not in') {
                                value = value.split(',').map(function (v) { return v.trim(); });
                                other_filters_list.push(['FT Stock RM List', field, frappe_op, value]);
                                return;
                            }

                            // ── Equals → group by field ──
                            if (frappe_op === '=') {
                                if (!equals_groups[field]) equals_groups[field] = [];
                                equals_groups[field].push(value);
                                return;
                            }

                            other_filters_list.push(['FT Stock RM List', field, frappe_op, value]);
                        });

                        // ── Same field multiple Equals → IN ──
                        for (let field in equals_groups) {
                            let values = equals_groups[field];
                            if (values.length === 1) {
                                filters.push(['FT Stock RM List', field, '=', values[0]]);
                            } else {
                                filters.push(['FT Stock RM List', field, 'in', values]);
                            }
                        }

                        // ── Other filters ──
                        for (let f of other_filters_list) {
                            filters.push(f);
                        }

                        return filters;
                    }

                    // ── Count records — shown at top of filter section ──
                    let count_debounce_timer = null;
                    function update_record_count() {
                        let $count_div = export_dialog.$wrapper.find('#rm-filter-record-count');
                        clearTimeout(count_debounce_timer);
                        count_debounce_timer = setTimeout(function () {
                            let filters = collect_filters();
                            frappe.call({
                                method: 'frappe.client.get_count',
                                args: { doctype: 'FT Stock RM List', filters: filters.length > 0 ? filters : [] },
                                callback: function (r) {
                                    let count = r.message || 0;
                                    $count_div.html(`<span style="font-size:14px; color:#374151; font-weight:400;">${count} records will be exported</span>`);
                                    // Also update export button text for filtered type
                                    update_export_btn_text(count);
                                }
                            });
                        }, 400);
                    }

                    // ── Add Filter button — row added ONLY on click ──
                    export_dialog.$wrapper.find('#rm-add-filter-btn').on('click', function () {
                        add_filter_row();
                    });

                    // ── Clear Filters button ──
                    export_dialog.$wrapper.find('#rm-clear-filters-btn').on('click', function () {
                        export_dialog.$wrapper.find('#rm-filter-rows-container').empty();
                        filter_row_counter = 0;
                        sync_empty_state();
                        update_record_count();
                    });

                    // ── Build field checkboxes ──
                    function build_field_checkboxes() {
                        let $container = export_dialog.$wrapper.find('#rm-fields-checkboxes');
                        $container.empty();

                        // ID (name) always first
                        $container.append(rm_make_checkbox('name', 'ID', true, true));

                        filterable_fields.forEach(function (f) {
                            if (f.fieldname === 'name') return; // already added
                            $container.append(rm_make_checkbox(f.fieldname, f.label, f.reqd ? true : false, f.reqd ? true : false));
                        });
                    }

                    function rm_make_checkbox(fieldname, label, checked, is_mandatory) {
                        let mandatory_dot = is_mandatory
                            ? `<span style="color:#EF4444; font-size:14px; margin-left:3px;" title="Mandatory">*</span>`
                            : '';
                        return `
                            <label class="rm-field-checkbox-label" style="display:flex; align-items:center; cursor:pointer; font-size:12px; gap:2px; color:var(--color-text-primary); padding:0; user-select:none;">
                                <input type="checkbox" class="rm-field-cb" data-fieldname="${fieldname}" data-mandatory="${is_mandatory ? '1' : '0'}"
                                    ${checked ? 'checked' : ''}
                                    style="width:14px; height:14px; accent-color:#2563EB; cursor:pointer; flex-shrink:0;" />
                                <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${label}${mandatory_dot}</span>
                            </label>
                        `;
                    }

                    build_field_checkboxes();

                    // ── Select All ──
                    export_dialog.$wrapper.find('#rm-select-all-btn').on('click', function () {
                        export_dialog.$wrapper.find('.rm-field-cb').prop('checked', true);
                    });

                    // ── Select Mandatory ──
                    export_dialog.$wrapper.find('#rm-select-mandatory-btn').on('click', function () {
                        export_dialog.$wrapper.find('.rm-field-cb').each(function () {
                            $(this).prop('checked', $(this).data('mandatory') == '1');
                        });
                    });

                    // ── Unselect All — fully uncheck everything including ID ──
                    export_dialog.$wrapper.find('#rm-unselect-all-btn').on('click', function () {
                        export_dialog.$wrapper.find('.rm-field-cb').prop('checked', false);
                    });

                    // ── Collect selected fields ──
                    function collect_selected_fields() {
                        let fields = [];
                        export_dialog.$wrapper.find('.rm-field-cb:checked').each(function () {
                            fields.push($(this).data('fieldname'));
                        });
                        return fields;
                    }

                    // ── Helper: update Export button text ──
                    function update_export_btn_text(count) {
                        let type = $exportType.val();
                        let $btn = export_dialog.$wrapper.find('.rm-export-confirm-btn');
                        if (type === 'blank') {
                            $btn.text('Export');
                        } else {
                            $btn.text('Export ' + count + ' records');
                        }
                    }

                    // ── Export Type change ──
                    function update_info() {
                        let type = $exportType.val();
                        let info = info_map[type];
                        $info.css('background', info.bg);

                        if (type === 'blank') {
                            $infoText.css('color', info.color).html('<strong>📄</strong> No records will be exported.');
                            $filterSec.slideUp(200);
                            $info.show();
                            update_export_btn_text(0);

                        } else if (type === '5') {
                            $infoText.css('color', info.color).html('<strong>🔢</strong> 5 records will be exported.');
                            $filterSec.slideUp(200);
                            $info.show();
                            update_export_btn_text(5);

                        } else if (type === 'all') {
                            $infoText.css('color', info.color).html('<strong>ℹ️</strong> Counting...');
                            $filterSec.slideUp(200);
                            $info.show();
                            export_dialog.$wrapper.find('.rm-export-confirm-btn').text('Export...');
                            frappe.call({
                                method: 'frappe.client.get_count',
                                args: { doctype: 'FT Stock RM List', filters: [] },
                                callback: function (r) {
                                    let count = r.message || 0;
                                    $infoText.html('<strong>ℹ️</strong> ' + count + ' records will be exported.');
                                    update_export_btn_text(count);
                                }
                            });

                        } else if (type === 'filtered') {
                            $filterSec.slideDown(200);
                            $info.hide();
                            sync_empty_state();
                            update_record_count();
                        }
                    }

                    $exportType.on('change', update_info);
                    update_info();

                    // ── Cancel ──
                    export_dialog.$wrapper.find('.rm-export-cancel-btn').on('click', function () {
                        export_dialog.hide();
                    });

                    // ── Export Confirm ──
                    export_dialog.$wrapper.find('.rm-export-confirm-btn').on('click', function () {
                        let file_type = $fileType.val();
                        let export_type = $exportType.val();
                        let filters = null;

                        if (export_type === 'filtered') {
                            let custom_filters = collect_filters();
                            if (custom_filters.length > 0) {
                                filters = JSON.stringify(custom_filters);
                            } else {
                                filters = null;
                            }
                        }

                        // Collect selected fields
                        let selected_fields = collect_selected_fields();
                        if (selected_fields.length === 0) {
                            frappe.msgprint({ title: 'No Fields Selected', message: 'Please select at least one field to export.', indicator: 'orange' });
                            return;
                        }

                        let $btn = export_dialog.$wrapper.find('.rm-export-confirm-btn');
                        $btn.text('Exporting...').prop('disabled', true);

                        let url = `/api/method/fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.export_with_value?file_type=${file_type}&export_type=${export_type}`;
                        if (filters) url += `&filters=${encodeURIComponent(filters)}`;
                        url += `&selected_fields=${encodeURIComponent(JSON.stringify(selected_fields))}`;

                        window.location.href = url;

                        setTimeout(function () {
                            $btn.text('Export').prop('disabled', false);
                            export_dialog.hide();
                        }, 1500);
                    });
                });
            });
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
                            <div style="font-weight:500; font-size:15px; color:var(--color-text-primary);">Import Stock RM List</div>
                            <div style="font-size:12px; color:var(--color-text-secondary); font-weight:400;">Import data from Excel or CSV file</div>
                        </div>
                    </div>
                `,
                fields: [{
                    fieldname: 'dialog_html',
                    fieldtype: 'HTML',
                    options: `
                    <div id="rm-import-root">
                        <div class="rm-drop-zone" style="border:1.5px dashed #C0C0B8; border-radius:12px; background:#F9FAFB; padding:2rem 1rem; text-align:center; margin-bottom:14px; cursor:pointer;">
                            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5" style="display:block; margin:0 auto 10px;">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                                <line x1="12" y1="18" x2="12" y2="12"/>
                                <line x1="9" y1="15" x2="15" y2="15"/>
                            </svg>
                            <div class="rm-drop-text" style="font-size:14px; font-weight:500; color:var(--color-text-primary); margin-bottom:4px;">Upload Excel or CSV File</div>
                            <div style="font-size:12px; color:var(--color-text-secondary); margin-bottom:14px;">Drag & drop your file here, or click below to browse</div>
                            <label class="rm-choose-btn" style="display:inline-block; background:#fff; border:0.5px solid #C0C0B8; border-radius:8px; padding:7px 20px; font-size:13px; cursor:pointer; color:var(--color-text-primary);">Choose File</label>
                            <input type="file" class="rm-file-input" accept=".xlsx,.csv" style="display:none;" />
                        </div>

                        <div style="background:#EBF5FF; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
                            <div style="font-size:12px; color:#1D4ED8; line-height:1.7;">
                                <strong>Note:</strong> Supported formats: .xlsx and .csv &nbsp;·&nbsp; Unmatched columns will prompt a mapping dialog
                            </div>
                        </div>

                        <div style="display:flex; gap:10px;">
                            <button class="rm-cancel-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">Cancel</button>
                            <button class="rm-import-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">Import</button>
                        </div>
                    </div>
                    `
                }]
            });

            d.$wrapper.find('.modal-footer').hide();
            d.show();

            d.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

                selected_file_url = null;

                let $dropZone = d.$wrapper.find('.rm-drop-zone');
                let $dropText = d.$wrapper.find('.rm-drop-text');
                let $chooseBtn = d.$wrapper.find('.rm-choose-btn');
                let $fileInput = d.$wrapper.find('.rm-file-input');

                let dropZone = $dropZone[0];
                let fileInput = $fileInput[0];

                function reset_dropzone() {
                    $dropText.text('Upload Excel or CSV File');
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.borderStyle = 'dashed';
                    dropZone.style.background = '#F9FAFB';
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

                d.$wrapper.find('.rm-cancel-btn').on('click', function () {
                    reset_dropzone();
                    d.hide();
                });

                $dropZone.on('click', function (e) {
                    if ($(e.target).hasClass('rm-choose-btn') || $(e.target).closest('.rm-choose-btn').length) return;
                    fileInput.value = '';
                    fileInput.click();
                });

                $dropZone.on('dragover', function (e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#3B82F6';
                    dropZone.style.background = '#EBF5FF';
                });
                $dropZone.on('dragleave', function () {
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background = '#F9FAFB';
                });
                $dropZone.on('drop', function (e) {
                    e.preventDefault();
                    dropZone.style.borderColor = '#C0C0B8';
                    dropZone.style.background = '#F9FAFB';
                    let dt = e.originalEvent.dataTransfer;
                    if (dt && dt.files[0]) handle_file(dt.files[0]);
                });

                d.$wrapper.find('.rm-import-btn').on('click', function () {
                    if (!selected_file_url) {
                        frappe.msgprint({ title: 'No File Selected', message: 'Please select a file first.', indicator: 'orange' });
                        return;
                    }

                    let $btn = d.$wrapper.find('.rm-import-btn');
                    $btn.text('Checking...').prop('disabled', true);

                    frappe.call({
                        method: 'fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.get_file_headers',
                        args: { file_url: selected_file_url },
                        callback: function (r) {
                            $btn.text('Import').prop('disabled', false);
                            if (!r.message) return;

                            let { unmatched, all_fields } = r.message;
                            if (unmatched && unmatched.length > 0) {
                                d.hide();
                                rm_show_mapping_dialog(unmatched, all_fields, selected_file_url, listview, d);
                            } else {
                                rm_run_import(selected_file_url, null, $btn[0], listview, d);
                            }
                        }
                    });
                });
            });
        });
    }
};


// PORTAL — Global (body mein, dialog overflow se bahar)
let $rm_portal = null;
let rm_active_dd = null;

function rm_get_portal() {
    if (!$rm_portal) {
        $rm_portal = $(`
            <div id="rm-dd-portal" style="
                position:fixed; z-index:99999; display:none;
                background:#fff; border:1px solid #D1D5DB;
                border-radius:6px; box-shadow:0 4px 20px rgba(0,0,0,0.15);
                overflow:hidden;
            ">
                <div style="padding:6px 8px; border-bottom:1px solid #f0f0f0; background:#fff;">
                    <input id="rm-portal-search" type="text" placeholder="Search fields..." style="
                        width:100%; padding:5px 8px; border:1px solid #E5E7EB;
                        border-radius:4px; font-size:12px; outline:none; box-sizing:border-box;
                    " />
                </div>
                <div id="rm-portal-options" style="max-height:220px; overflow-y:auto;"></div>
            </div>
        `).appendTo('body');

        $rm_portal.on('input', '#rm-portal-search', function () {
            let q = $(this).val().toLowerCase();
            $rm_portal.find('.rm-portal-opt').each(function () {
                $(this).toggle($(this).text().toLowerCase().includes(q));
            });
        });

        $rm_portal.on('click', '.rm-portal-opt', function (e) {
            e.stopPropagation();
            if (!rm_active_dd) return;

            let val = $(this).data('value');
            let labelTxt = $(this).find('.rm-opt-label').text();
            let subTxt = $(this).find('.rm-opt-sub').text();
            let hasSub = ($(this).find('.rm-opt-sub').length > 0 && val !== '');

            let $dd = $(rm_active_dd);
            $dd.data('selected-value', val);

            if (hasSub) {
                $dd.find('.rm-dd-trigger').html(`
                    <div style="line-height:1.3;">
                        <div style="font-size:13px; color:var(--color-text-primary);">${labelTxt}</div>
                        <div style="font-size:11px; color:#9CA3AF; font-family:monospace,'Courier New',sans-serif;">${subTxt}</div>
                    </div>
                `).css('color', 'var(--color-text-primary)');
            } else {
                $dd.find('.rm-dd-trigger').html(`<span>${labelTxt}</span>`).css('color', '#6B7280');
            }
            $dd.find('.rm-dd-trigger').css('border-color', val ? '#1D9E75' : '#D1D5DB');
            rm_close_portal();
        });

        $rm_portal.on('click', '#rm-portal-search', function (e) { e.stopPropagation(); });

        $(document).on('click.rm_portal_global', function (e) {
            if (
                $rm_portal && !$rm_portal.is(':hidden') &&
                !$rm_portal[0].contains(e.target) &&
                !(rm_active_dd && rm_active_dd.contains(e.target))
            ) {
                rm_close_portal();
            }
        });
    }
    return $rm_portal;
}

function rm_close_portal() {
    if ($rm_portal) $rm_portal.hide();
    rm_active_dd = null;
}

function rm_open_portal($dd, all_fields) {
    let portal = rm_get_portal();
    let $opts = portal.find('#rm-portal-options');
    $opts.empty();

    $opts.append(`
        <div class="rm-portal-opt" data-value="" style="padding:8px 12px; cursor:pointer; border-bottom:1px solid #f0f0f0;">
            <div class="rm-opt-label" style="font-size:13px; color:#6B7280;">Don't Import</div>
        </div>
    `);

    let selectedVal = $dd.data('selected-value') || '';

    all_fields.forEach(function (f) {
        let label = f.label || f.fieldname;
        let fieldname = f.fieldname;
        let showSub = (label !== fieldname);
        let isSelected = (fieldname === selectedVal);

        let subHtml = showSub
            ? `<div class="rm-opt-sub" style="font-size:11px; color:#9CA3AF; margin-top:1px; font-family:monospace,'Courier New',sans-serif;">${fieldname}</div>`
            : '';

        $opts.append(`
            <div class="rm-portal-opt" data-value="${fieldname}" style="
                padding:8px 12px; cursor:pointer; border-bottom:1px solid #f0f0f0;
                background:${isSelected ? '#EFF6FF' : '#fff'};
            ">
                <div class="rm-opt-label" style="font-size:13px; color:var(--color-text-primary);">${label}</div>
                ${subHtml}
            </div>
        `);
    });

    $opts.find('.rm-portal-opt').on('mouseenter', function () {
        if ($(this).data('value') !== selectedVal) $(this).css('background', '#F9FAFB');
    }).on('mouseleave', function () {
        $(this).css('background', $(this).data('value') === selectedVal ? '#EFF6FF' : '#fff');
    });

    let trigger = $dd.find('.rm-dd-trigger')[0];
    let rect = trigger.getBoundingClientRect();
    let portalW = Math.max(rect.width, 240);
    let spaceBelow = window.innerHeight - rect.bottom;
    let spaceAbove = rect.top;

    portal.css({ width: portalW + 'px', display: 'block', left: rect.left + 'px' });

    if (spaceBelow >= 220 || spaceBelow >= spaceAbove) {
        portal.css({ top: (rect.bottom + 4) + 'px', bottom: 'auto' });
    } else {
        portal.css({ top: 'auto', bottom: (window.innerHeight - rect.top + 4) + 'px' });
    }

    portal.find('#rm-portal-search').val('').trigger('input');
    setTimeout(function () { portal.find('#rm-portal-search').focus(); }, 50);
    rm_active_dd = $dd[0];
}


// MAPPING DROPDOWN TRIGGER
function rm_build_mapping_dropdown(excel_col) {
    return `
        <div class="rm-custom-dd" data-excel-col="${excel_col}" style="position:relative; width:100%;">
            <div class="rm-dd-trigger" style="
                width:100%; padding:7px 30px 7px 10px; border:1px solid #D1D5DB;
                border-radius:6px; font-size:13px; background:#fff; color:#6B7280;
                cursor:pointer; min-height:36px; box-sizing:border-box;
                display:flex; align-items:center; user-select:none;
            ">Don't Import</div>
            <svg class="rm-dd-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2.5" style="
                position:absolute; right:10px; top:50%; transform:translateY(-50%);
                pointer-events:none; transition:transform 0.2s;
            "><polyline points="6 9 12 15 18 9"/></svg>
        </div>
    `;
}


// MAPPING DIALOG
function rm_show_mapping_dialog(unmatched_columns, all_fields, file_url, listview, upload_dialog) {

    let proper_rows = '';
    unmatched_columns.forEach(function (col) {
        proper_rows += `
            <tr style="border-bottom:1px solid #f0f0f0;">
                <td style="padding:12px 10px; font-size:13px; color:#171717; font-weight:500; width:38%; vertical-align:middle;">
                    <span>${col}</span>
                </td>
                <td style="padding:12px 8px; text-align:center; color:#D1D5DB; font-size:16px; width:5%; vertical-align:middle;">→</td>
                <td style="padding:6px; width:57%; vertical-align:middle;">
                    ${rm_build_mapping_dropdown(col)}
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
            <div class="rm-mapping-container" style="margin-bottom:14px;">
                <div style="background:#FEF3C7; border-radius:8px; padding:12px 14px; margin-bottom:16px; border:1px solid #FCD34D;">
                    <div style="font-size:12px; color:#92400E; line-height:1.8;">
                        <strong>⚠️ Action Required:</strong> The following columns could not be automatically matched.
                        Select the correct field for each column, or choose "Don't Import" to skip it.
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
                    <div style="max-height:260px; overflow-y:auto;">
                        <table style="width:100%; border-collapse:collapse; background:#fff;">
                            ${proper_rows}
                        </table>
                    </div>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="rm-map-back-btn" style="flex:1; background:transparent; border:0.5px solid #C0C0B8; border-radius:8px; padding:10px; font-size:14px; cursor:pointer; color:var(--color-text-secondary);">
                        ← Back
                    </button>
                    <button class="rm-map-confirm-btn" style="flex:2; background:#000; border:none; border-radius:8px; padding:10px; font-size:14px; font-weight:500; cursor:pointer; color:#fff;">
                        Confirm & Import
                    </button>
                </div>
            </div>
            `
        }]
    });

    map_dialog.$wrapper.find('.modal-footer').hide();
    map_dialog.$wrapper.find('.modal-dialog').css({ 'width': '720px', 'max-width': '92vw' });
    map_dialog.show();

    map_dialog.$wrapper.off('shown.bs.modal').on('shown.bs.modal', function () {

        let $all_dd = map_dialog.$wrapper.find('.rm-custom-dd');

        $all_dd.on('click', '.rm-dd-trigger', function (e) {
            e.stopPropagation();
            let $dd = $(this).closest('.rm-custom-dd');

            if (rm_active_dd === $dd[0]) {
                rm_close_portal();
                $dd.find('.rm-dd-arrow').css('transform', 'translateY(-50%)');
                return;
            }

            rm_close_portal();
            rm_open_portal($dd, all_fields);
            $dd.find('.rm-dd-arrow').css('transform', 'translateY(-50%) rotate(180deg)');
        });

        $(document).on('click.rm_map_arrow', function () {
            if (rm_active_dd) {
                $(rm_active_dd).find('.rm-dd-arrow').css('transform', 'translateY(-50%)');
            }
        });

        map_dialog.$wrapper.find('.rm-map-back-btn').on('click', function () {
            rm_close_portal();
            $(document).off('click.rm_map_arrow');
            map_dialog.hide();
            upload_dialog.show();
        });

        map_dialog.$wrapper.find('.rm-map-confirm-btn').on('click', function () {
            rm_close_portal();
            $(document).off('click.rm_map_arrow');

            let custom_mapping = {};
            $all_dd.each(function () {
                let col = $(this).data('excel-col');
                let val = $(this).data('selected-value') || '';
                if (val) custom_mapping[col] = val;
            });

            let $btn = map_dialog.$wrapper.find('.rm-map-confirm-btn');
            $btn.text('Importing...').prop('disabled', true);

            rm_run_import(file_url, custom_mapping, $btn[0], listview, map_dialog);
        });

        map_dialog.$wrapper.on('hidden.bs.modal', function () {
            rm_close_portal();
            $(document).off('click.rm_map_arrow');
        });
    });
}


// RUN IMPORT
function rm_run_import(file_url, custom_mapping, btn, listview, dialog) {
    frappe.call({
        method: 'fabtrk.fabtrk.doctype.ft_stock_rm_list.ft_stock_rm_list.import_with_value',
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









