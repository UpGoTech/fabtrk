// Copyright (c) 2026, UpGo Technologies and contributors
// FabTrk Tracking Page - Frontend JavaScript

frappe.pages["fabtrk-tracking"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: "FabTrk Tracking",
        single_column: true,
    });

    $(wrapper).find(".page-content").html(`<div id="fabtrk-tracking-root"></div>`);
    load_tracking_css();
    render_tracking_shell();
    load_active_projects();
    load_tracking_data();
};

// HTML SHELL
function render_tracking_shell() {
    document.getElementById("fabtrk-tracking-root").innerHTML = `
    <div class="fabtrk-tracking-wrap">
        
        <!-- HEADER -->
        <div class="fabtrk-tracking-header">
            <div class="fabtrk-tracking-header-content">
                <h1>📊 FabTrk Tracking Dashboard</h1>
                <p>Real-time Project, Drawing, Transaction and Amount overview</p>
            </div>
        </div>

        <div class="fabtrk-filter-row">
            <div class="fabtrk-filter-box" id="fabtrk-project-filter-box" onclick="fabtrk_toggle_dropdown()">
                <span id="fabtrk-filter-label">All Active Projects</span>
                <span class="fabtrk-filter-arrow">▾</span>
            </div>
            <div class="fabtrk-filter-dropdown" id="fabtrk-filter-dropdown" style="display:none;">
                <div class="fabtrk-filter-search-wrap">
                    <input type="text" id="fabtrk-filter-search" class="fabtrk-filter-search" placeholder="Search project..." oninput="fabtrk_filter_options()"/>
                </div>
                <div id="fabtrk-filter-options"></div>
                <div class="fabtrk-filter-footer">
                    <button class="fabtrk-filter-clear" onclick="fabtrk_clear_selection()">Clear</button>
                    <button class="fabtrk-filter-apply" onclick="fabtrk_apply_selection()">Apply</button>
                </div>
            </div>
        </div>

        <!-- SUMMARY CARDS -->
        <div class="fabtrk-cards-section">
            <h3>📈 Summary</h3>
            <div class="fabtrk-cards-grid" id="fabtrk-cards">
                ${skeleton_loader(6)}
            </div>
        </div>

        <!-- MAIN TRACKING GRID -->
        <div class="fabtrk-tracking-grid">
            
            <!-- LEFT COLUMN -->
            <div class="fabtrk-col-left">
                
                <!-- Project Status -->
                <div class="fabtrk-panel">
                    <div class="fabtrk-panel-header">
                        <h3>📁 Project Status</h3>
                        <span class="fabtrk-badge" id="fabtrk-proj-count">0</span>
                    </div>
                    <div id="fabtrk-status-chart" class="fabtrk-chart-area"></div>
                </div>

                <!-- Stage Progress -->
                <div class="fabtrk-panel">
                    <div class="fabtrk-panel-header">
                        <h3>🔧 Stage-wise Progress</h3>
                    </div>
                    <div id="fabtrk-stage-progress" class="fabtrk-progress-area"></div>
                </div>
            </div>

            <!-- RIGHT COLUMN -->
            <div class="fabtrk-col-right">
                
                <!-- Recent Transactions -->
                <div class="fabtrk-panel" style="flex: 1;">
                    <div class="fabtrk-panel-header">
                        <h3>🔄 Recent Transactions</h3>
                        <span class="fabtrk-badge" id="fabtrk-txn-count">0</span>
                    </div>
                    <div id="fabtrk-transactions" class="fabtrk-table-area"></div>
                </div>

                <!-- Project Progress -->
                <div class="fabtrk-panel">
                    <div class="fabtrk-panel-header">
                        <h3>📊 Top Projects</h3>
                    </div>
                    <div id="fabtrk-top-projects" class="fabtrk-projects-area"></div>
                </div>
            </div>
        </div>

        <!-- BOTTOM GRID -->
        <div class="fabtrk-bottom-section">
            
            <!-- Drawings -->
            <div class="fabtrk-panel">
                <div class="fabtrk-panel-header">
                    <h3>📐 Latest Drawings</h3>
                    <span class="fabtrk-badge" id="fabtrk-draw-count">0</span>
                </div>
                <div id="fabtrk-drawings" class="fabtrk-table-area"></div>
            </div>

            <!-- Amount Tracking -->
            <div class="fabtrk-panel">
                <div class="fabtrk-panel-header">
                    <h3>💰 Amount Tracking</h3>
                </div>
                <div id="fabtrk-amount" class="fabtrk-amount-area"></div>
            </div>
        </div>

        <!-- Additional Info -->
        <div class="fabtrk-info-section">
            <div class="fabtrk-panel">
                <div class="fabtrk-panel-header">
                    <h3>📋 Additional Info</h3>
                </div>
                <div id="fabtrk-additional" class="fabtrk-info-area"></div>
            </div>
        </div>
    </div>`;
}

// LOAD DATA
function load_tracking_data() {
    let projects = window._fabtrk_selected_projects || [];
    frappe.call({
        method: "fabtrk.fabtrk.page.fabtrk_tracking.fabtrk_tracking.get_tracking_summary",
        args: { projects: JSON.stringify(projects) },
        callback: function (r) {
            if (r.message) {
                render_tracking_data(r.message);
            }
        }
    });
}

// RENDER DATA
function render_tracking_data(data) {

    // SUMMARY CARDS
    let cards_html = `
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">📁</div>
            <div><div class="fabtrk-card-value">${data.total_projects || 0}</div><div class="fabtrk-card-label">Total Projects</div></div>
        </div>
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">✅</div>
            <div><div class="fabtrk-card-value">${data.completed_projects || 0}</div><div class="fabtrk-card-label">Completed</div></div>
        </div>
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">⏳</div>
            <div><div class="fabtrk-card-value">${data.ongoing_projects || 0}</div><div class="fabtrk-card-label">Ongoing</div></div>
        </div>
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">📐</div>
            <div><div class="fabtrk-card-value">${data.total_drawings || 0}</div><div class="fabtrk-card-label">Drawings</div></div>
        </div>
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">⚖️</div>
            <div><div class="fabtrk-card-value">${(data.total_weight || 0).toLocaleString()}</div><div class="fabtrk-card-label">Weight (KG)</div></div>
        </div>
        <div class="fabtrk-card">
            <div class="fabtrk-card-icon">💰</div>
            <div><div class="fabtrk-card-value">₹${(data.po_total_amount || 0).toLocaleString()}</div><div class="fabtrk-card-label">Amount</div></div>
        </div>
    `;
    document.getElementById("fabtrk-cards").innerHTML = cards_html;

    // PROJECT STATUS
    document.getElementById("fabtrk-proj-count").textContent = data.total_projects || 0;
    let status_html = "";
    let status_colors = {
        "Order Received": "#3498db",
        "Material Planning": "#9b59b6",
        "WIP": "#f39c12",
        "Completed": "#27ae60",
        "Cancelled": "#e74c3c"
    };
    for (let [status, count] of Object.entries(data.status_counts || {})) {
        let color = status_colors[status] || "#95a5a6";
        status_html += `
            <div class="fabtrk-status-item">
                <span class="fabtrk-status-dot" style="background:${color}"></span>
                <span>${status}</span>
                <span class="fabtrk-status-badge">${count}</span>
            </div>`;
    }
    document.getElementById("fabtrk-status-chart").innerHTML = status_html || "<p class='fabtrk-empty'>No data</p>";

    // STAGE PROGRESS
    let stage_html = "";
    for (let [stage, info] of Object.entries(data.stage_summary || {})) {
        stage_html += `
            <div class="fabtrk-stage-progress-item">
                <div class="fabtrk-stage-label">${stage} (${info.count || 0} records)</div>
                <div class="fabtrk-progress-bar">
                    <div class="fabtrk-progress-fill" style="width:${info.avg_pct || 0}%"></div>
                </div>
                <div class="fabtrk-stage-stats">+${info.addition || 0} | -${info.subtraction || 0} | ${info.avg_pct || 0}%</div>
            </div>`;
    }
    document.getElementById("fabtrk-stage-progress").innerHTML = stage_html || "<p class='fabtrk-empty'>No stages</p>";

    // TRANSACTIONS TABLE
    document.getElementById("fabtrk-txn-count").textContent = data.total_transactions || 0;
    let txn_html = `<table class="fabtrk-table"><thead><tr><th>Txn ID</th><th>Project</th><th>Stage</th><th>Date</th><th>Work %</th><th>Add/Sub</th></tr></thead><tbody>`;
    for (let t of (data.transactions || []).slice(0, 8)) {
        txn_html += `<tr>
            <td>${t.name || "—"}</td>
            <td>${t.project_number || "—"}</td>
            <td>${t.stages || "—"}</td>
            <td>${t.date || "—"}</td>
            <td><span class="fabtrk-pct-badge">${t.work_completed || 0}%</span></td>
            <td><span class="fabtrk-add">+${t.addition || 0}</span> <span class="fabtrk-sub">-${t.subtraction || 0}</span></td>
        </tr>`;
    }
    txn_html += "</tbody></table>";
    document.getElementById("fabtrk-transactions").innerHTML = txn_html;

    // TOP PROJECTS
    let proj_html = "";
    for (let p of (data.projects || []).slice(0, 5)) {
        let pct = p.percentage_completed || 0;
        proj_html += `
            <div class="fabtrk-project-item">
                <div class="fabtrk-project-name">${p.name}</div>
                <div class="fabtrk-project-bar">
                    <div class="fabtrk-project-fill" style="width:${pct}%"></div>
                </div>
                <div class="fabtrk-project-info">${pct}% · ${p.status || "—"}</div>
            </div>`;
    }
    document.getElementById("fabtrk-top-projects").innerHTML = proj_html || "<p class='fabtrk-empty'>No projects</p>";

    // DRAWINGS TABLE
    document.getElementById("fabtrk-draw-count").textContent = data.total_drawings || 0;
    let draw_html = `<table class="fabtrk-table"><thead><tr><th>Drawing</th><th>Project</th><th>Unit Weight</th><th>Description</th></tr></thead><tbody>`;
    for (let d of (data.drawings || []).slice(0, 6)) {
        draw_html += `<tr>
            <td>${d.drawing_number || "—"}</td>
            <td>${d.project_number || "—"}</td>
            <td>${(d.unit_weight != null ? d.unit_weight : "—")}</td>
            <td>${d.drawing_description || "—"}</td>
        </tr>`;
    }
    draw_html += "</tbody></table>";
    document.getElementById("fabtrk-drawings").innerHTML = draw_html;

    // AMOUNT TRACKING
    let amount_html = `
        <div class="fabtrk-amount-item">
            <span class="fabtrk-amount-label">Total PO Amount:</span>
            <span class="fabtrk-amount-value">₹${(data.po_total_amount || 0).toLocaleString()}</span>
        </div>
        <div class="fabtrk-amount-item">
            <span class="fabtrk-amount-label">PO Weight:</span>
            <span class="fabtrk-amount-value">${(data.po_total_weight || 0)} KG</span>
        </div>
        <div class="fabtrk-amount-item">
            <span class="fabtrk-amount-label">Drawing Weight:</span>
            <span class="fabtrk-amount-value">${(data.total_drawing_weight || 0)} KG</span>
        </div>
        <div class="fabtrk-amount-item">
            <span class="fabtrk-amount-label">Total Weight:</span>
            <span class="fabtrk-amount-value">${(data.total_weight || 0)} KG</span>
        </div>
    `;
    document.getElementById("fabtrk-amount").innerHTML = amount_html;

    // ADDITIONAL INFO
    let info_html = `
        <div class="fabtrk-info-grid">
            <div class="fabtrk-info-box">
                <div class="fabtrk-info-label">👥 Customers</div>
                <div class="fabtrk-info-value">${data.total_customers || 0}</div>
            </div>
            <div class="fabtrk-info-box">
                <div class="fabtrk-info-label">📦 Raw Materials</div>
                <div class="fabtrk-info-value">${data.total_raw_materials || 0}</div>
            </div>
            <div class="fabtrk-info-box">
                <div class="fabtrk-info-label">📊 Transactions</div>
                <div class="fabtrk-info-value">${data.total_transactions || 0}</div>
            </div>
            <div class="fabtrk-info-box">
                <div class="fabtrk-info-label">📅 Monthly Targets</div>
                <div class="fabtrk-info-value">${data.monthly_targets_count || 0}</div>
            </div>
        </div>
    `;
    document.getElementById("fabtrk-additional").innerHTML = info_html;
}

function load_active_projects() {
    frappe.call({
        method: "fabtrk.fabtrk.page.fabtrk_tracking.fabtrk_tracking.get_active_projects_list",
        callback: function (r) {
            window._fabtrk_all_projects = (r.message || []).map(p => p.name);
            window._fabtrk_selected_projects = [];
            fabtrk_render_options(window._fabtrk_all_projects);
            document.addEventListener("click", function (e) {
                if (!document.getElementById("fabtrk-project-filter-box")?.contains(e.target) && !document.getElementById("fabtrk-filter-dropdown")?.contains(e.target)) {
                    document.getElementById("fabtrk-filter-dropdown").style.display = "none";
                }
            });
        }
    });
}

window.fabtrk_toggle_dropdown = function () {
    let dd = document.getElementById("fabtrk-filter-dropdown");
    dd.style.display = dd.style.display === "none" ? "block" : "none";
};

window.fabtrk_filter_options = function () {
    let txt = (document.getElementById("fabtrk-filter-search")?.value || "").toLowerCase();
    let filtered = (window._fabtrk_all_projects || []).filter(p => p.toLowerCase().includes(txt));
    fabtrk_render_options(filtered);
};

function fabtrk_render_options(projects) {
    let selected = window._fabtrk_selected_projects || [];
    document.getElementById("fabtrk-filter-options").innerHTML = projects.map(p => `
        <label class="fabtrk-filter-option ${selected.includes(p) ? 'fabtrk-opt-checked' : ''}">
            <input type="checkbox" value="${p}" ${selected.includes(p) ? 'checked' : ''} onchange="fabtrk_on_check(this)"/>
            ${p}
        </label>`).join("");
}

window.fabtrk_on_check = function (checkbox) {
    let project = checkbox.value;
    let selected = window._fabtrk_selected_projects || [];
    if (checkbox.checked) {
        if (!selected.includes(project)) selected.push(project);
    } else {
        selected = selected.filter(p => p !== project);
    }
    window._fabtrk_selected_projects = selected;
    fabtrk_render_options(window._fabtrk_all_projects || []);
};

window.fabtrk_clear_selection = function () {
    window._fabtrk_selected_projects = [];
    fabtrk_render_options(window._fabtrk_all_projects || []);
    document.getElementById("fabtrk-filter-label").textContent = "All Active Projects";
};

window.fabtrk_apply_selection = function () {
    let selected = window._fabtrk_selected_projects || [];
    document.getElementById("fabtrk-filter-label").textContent = selected.length > 0 ? `${selected.length} selected` : "All Active Projects";
    document.getElementById("fabtrk-filter-dropdown").style.display = "none";
    load_tracking_data();
};

// SKELETON LOADER
function skeleton_loader(count) {
    return Array(count).fill('<div class="fabtrk-skeleton"></div>').join("");
}

// CSS LOADER
function load_tracking_css() {
    if (document.getElementById("fabtrk-tracking-styles")) return;

    let style = document.createElement("style");
    style.id = "fabtrk-tracking-styles";
    style.textContent = `
        .fabtrk-tracking-wrap { padding: 20px; background: #f5f7fa; min-height: 100vh; font-family: 'Inter', sans-serif; }
        .fabtrk-tracking-header { display: flex; justify-content: flex-start; align-items: flex-start; flex-direction: column; gap: 10px; margin-bottom: 20px; background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%); color: white; padding: 28px 24px; border-radius: 18px; box-shadow: 0 20px 40px rgba(40, 53, 147, 0.16); }
        .fabtrk-tracking-header h1 { margin: 0; font-size: 32px; line-height: 1.1; letter-spacing: 0.02em; }
        .fabtrk-tracking-header p { margin: 0; opacity: 0.88; font-size: 14px; color: rgba(255,255,255,0.9); }
        .fabtrk-cards-section h3 { margin: 0 0 16px; color: #2c3e50; }
        .fabtrk-cards-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 24px; }
        .fabtrk-card { background: white; padding: 18px 18px 16px; border-radius: 16px; box-shadow: 0 12px 30px rgba(39, 66, 103, 0.08); display: flex; align-items: center; gap: 14px; transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .fabtrk-card:hover { transform: translateY(-2px); box-shadow: 0 18px 34px rgba(39, 66, 103, 0.12); }
        .fabtrk-card-icon { font-size: 30px; }
        .fabtrk-card-value { font-size: 26px; font-weight: 700; color: #22303f; }
        .fabtrk-card-label { font-size: 12px; color: #7f8c8d; margin-top: 4px; }
        .fabtrk-tracking-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .fabtrk-col-left, .fabtrk-col-right { display: flex; flex-direction: column; gap: 24px; }
        .fabtrk-panel { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
        .fabtrk-panel-header { padding: 16px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; }
        .fabtrk-panel-header h3 { margin: 0; color: #2c3e50; font-size: 16px; }
        .fabtrk-badge { background: #e8f4ff; color: #667eea; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .fabtrk-chart-area, .fabtrk-table-area, .fabtrk-progress-area, .fabtrk-projects-area, .fabtrk-amount-area, .fabtrk-info-area { padding: 16px; }
        .fabtrk-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .fabtrk-table th { padding: 10px; text-align: left; background: #f8f9fa; color: #7f8c8d; font-weight: 600; border-bottom: 1px solid #e9ecef; }
        .fabtrk-table td { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        .fabtrk-table tr:hover { background: #f8f9fa; }
        .fabtrk-status-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
        .fabtrk-status-dot { width: 12px; height: 12px; border-radius: 50%; }
        .fabtrk-status-badge { margin-left: auto; background: #f0f0f0; padding: 2px 8px; border-radius: 12px; font-weight: 600; }
        .fabtrk-stage-progress-item { margin-bottom: 16px; }
        .fabtrk-stage-label { font-size: 13px; font-weight: 600; color: #2c3e50; margin-bottom: 6px; }
        .fabtrk-progress-bar { height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
        .fabtrk-progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
        .fabtrk-stage-stats { font-size: 12px; color: #7f8c8d; margin-top: 4px; }
        .fabtrk-project-item { margin-bottom: 12px; }
        .fabtrk-project-name { font-weight: 600; color: #2c3e50; margin-bottom: 4px; }
        .fabtrk-project-bar { height: 16px; background: #e9ecef; border-radius: 8px; overflow: hidden; }
        .fabtrk-project-fill { height: 100%; background: linear-gradient(90deg, #27ae60 0%, #16a085 100%); border-radius: 8px; }
        .fabtrk-project-info { font-size: 12px; color: #7f8c8d; margin-top: 4px; }
        .fabtrk-pct-badge { background: #e8f4ff; color: #667eea; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
        .fabtrk-add { color: #27ae60; font-weight: 600; }
        .fabtrk-sub { color: #e74c3c; font-weight: 600; }
        .fabtrk-amount-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
        .fabtrk-amount-label { color: #7f8c8d; }
        .fabtrk-amount-value { font-weight: 600; color: #2c3e50; }
        .fabtrk-filter-row { display: flex; justify-content: flex-start; margin-bottom: 18px; gap: 12px; position: relative; }
        .fabtrk-filter-box { display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 10px; background: white; border: 1px solid #e9ecef; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
        .fabtrk-filter-arrow { color: #7f8c8d; }
        .fabtrk-filter-dropdown { position: absolute; z-index: 1000; width: 320px; background: white; border: 1px solid #e9ecef; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.12); margin-top: 8px; }
        .fabtrk-filter-search-wrap { padding: 12px; border-bottom: 1px solid #e9ecef; }
        .fabtrk-filter-search { width: 100%; padding: 10px 12px; border: 1px solid #e9ecef; border-radius: 8px; }
        .fabtrk-filter-option { display: flex; align-items: center; gap: 10px; padding: 10px 14px; cursor: pointer; }
        .fabtrk-filter-option:hover { background: #f8f9fa; }
        .fabtrk-opt-checked { background: #e8f4ff; }
        .fabtrk-filter-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 12px; border-top: 1px solid #e9ecef; }
        .fabtrk-filter-clear, .fabtrk-filter-apply { padding: 8px 14px; border-radius: 8px; cursor: pointer; border: none; }
        .fabtrk-filter-clear { background: #f8f9fa; color: #7f8c8d; }
        .fabtrk-filter-apply { background: #667eea; color: white; }
        .fabtrk-info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .fabtrk-info-box { background: #f8f9fa; padding: 12px; border-radius: 8px; }
        .fabtrk-info-label { font-size: 12px; color: #7f8c8d; }
        .fabtrk-info-value { font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 4px; }
        .fabtrk-bottom-section { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .fabtrk-info-section { }
        .fabtrk-empty { color: #7f8c8d; text-align: center; padding: 40px; }
        .fabtrk-skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: fabtrk-skeleton-loading 1.5s infinite; height: 80px; border-radius: 12px; }
        @keyframes fabtrk-skeleton-loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        @media (max-width: 1400px) { .fabtrk-cards-grid { grid-template-columns: repeat(3, 1fr); } }
        @media (max-width: 1024px) { .fabtrk-tracking-grid, .fabtrk-bottom-section { grid-template-columns: 1fr; } }
        @media (max-width: 768px) { .fabtrk-cards-grid { grid-template-columns: repeat(2, 1fr); } }
    `;
    document.head.appendChild(style);
}
