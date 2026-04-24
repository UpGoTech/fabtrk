
frappe.pages["transaction-dashboard"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: "FabTrk Dashboard",
		single_column: true,
	});

	$(wrapper).find(".page-content").html(`<div id="ft-dashboard-root"></div>`);
	load_dashboard_css();
	render_shell();
	load_projects_filter();
};

// ─────────────────────────────────────────────
// SHELL — static HTML structure
// ─────────────────────────────────────────────
function render_shell() {
	document.getElementById("ft-dashboard-root").innerHTML = `
	<div class="ftd-wrap">

		<!-- HEADER -->
		<div class="ftd-header">
			<div class="ftd-header-left">
				<div class="ftd-logo">FT</div>
				<div>
					<h1 class="ftd-title">FabTrk Dashboard</h1>
					<p class="ftd-subtitle">Project · Drawing · Stage · Transaction Tracker</p>
				</div>
			</div>
			<div class="ftd-header-right">
				<select id="ftd-project-filter" class="ftd-select">
					<option value="">All Active Projects</option>
				</select>
				<button class="ftd-refresh-btn" onclick="ftd_refresh()">
					↻ Refresh
				</button>
			</div>
		</div>

		<!-- SUMMARY CARDS -->
		<div class="ftd-cards-grid" id="ftd-cards">
			${skeletons(4)}
		</div>

		<!-- MAIN GRID -->
		<div class="ftd-main-grid">
			<div class="ftd-col-left">
				<div class="ftd-panel">
					<div class="ftd-panel-header">
						<span class="ftd-panel-title">Project Status</span>
						<span class="ftd-panel-badge" id="ftd-proj-badge">—</span>
					</div>
					<div id="ftd-pie-area" class="ftd-chart-wrap"></div>
				</div>
				<div class="ftd-panel">
					<div class="ftd-panel-header">
						<span class="ftd-panel-title">Stage-wise Work %</span>
					</div>
					<div id="ftd-stage-bar" class="ftd-chart-wrap"></div>
				</div>
			</div>
			<div class="ftd-col-right">
				<div class="ftd-panel" style="flex:1;">
					<div class="ftd-panel-header">
						<span class="ftd-panel-title">Latest Transactions</span>
						<span class="ftd-panel-badge" id="ftd-txn-badge">—</span>
					</div>
					<div id="ftd-txn-table" class="ftd-table-wrap"></div>
				</div>
				<div class="ftd-panel">
					<div class="ftd-panel-header">
						<span class="ftd-panel-title">Project Progress</span>
					</div>
					<div id="ftd-proj-progress" class="ftd-progress-list"></div>
				</div>
			</div>
		</div>

		<!-- BOTTOM GRID -->
		<div class="ftd-bottom-grid">
			<div class="ftd-panel">
				<div class="ftd-panel-header">
					<span class="ftd-panel-title">Drawings</span>
					<span class="ftd-panel-badge" id="ftd-draw-badge">—</span>
				</div>
				<div id="ftd-draw-table" class="ftd-table-wrap"></div>
			</div>
			<div class="ftd-panel">
				<div class="ftd-panel-header">
					<span class="ftd-panel-title">Addition vs Subtraction per Stage</span>
				</div>
				<div id="ftd-add-sub" class="ftd-chart-wrap"></div>
			</div>
		</div>

	</div>`;
}

// ─────────────────────────────────────────────
// LOAD PROJECT FILTER
// ─────────────────────────────────────────────
function load_projects_filter() {
	frappe.call({
		method: "fabtrk.fabtrk.page.transaction_dashboard.transaction_dashboard.get_active_projects",
		callback: function (r) {
			let sel = document.getElementById("ftd-project-filter");
			(r.message || []).forEach(p => {
				let o = document.createElement("option");
				o.value = p.name; o.text = p.name;
				sel.appendChild(o);
			});
			sel.addEventListener("change", ftd_refresh);
			ftd_refresh();
		}
	});
}

// ─────────────────────────────────────────────
// MAIN REFRESH — single Python API call
// ─────────────────────────────────────────────
window.ftd_refresh = function () {
	let project = document.getElementById("ftd-project-filter")?.value || "";

	// Show skeletons while loading
	document.getElementById("ftd-cards").innerHTML = skeletons(4);

	frappe.call({
		method: "fabtrk.fabtrk.page.transaction_dashboard.transaction_dashboard.get_dashboard_data",
		args: { project: project || null },
		callback: function (r) {
			if (!r.message) return;
			let d = r.message;
			render_cards(d);
			render_pie(d);
			render_stage_bar(d);
			render_txn_table(d);
			render_proj_progress(d);
			render_draw_table(d);
			render_add_sub(d);
		}
	});
};

// ─────────────────────────────────────────────
// 1. SUMMARY CARDS
// ─────────────────────────────────────────────
function render_cards(d) {
	let cards = [
		{ icon: "🏗️", label: "Active Projects",       value: d.total_projects,     color: "#3b82f6" },
		{ icon: "📐", label: "Total Drawings",          value: d.total_drawings,     color: "#8b5cf6" },
		{ icon: "⚖️",  label: "Total Project Wt (Kg)", value: fmt(d.total_weight,2), color: "#f59e0b" },
		{ icon: "🔄", label: "Total Transactions",      value: d.total_transactions, color: "#10b981" },
	];
	document.getElementById("ftd-cards").innerHTML = cards.map(c => `
		<div class="ftd-card" style="--ca:${c.color}">
			<div class="ftd-card-bar" style="background:${c.color}"></div>
			<div class="ftd-card-icon">${c.icon}</div>
			<div class="ftd-card-body">
				<p class="ftd-card-label">${c.label}</p>
				<p class="ftd-card-value">${c.value}</p>
			</div>
		</div>
	`).join("");
}

// ─────────────────────────────────────────────
// 2. PROJECT STATUS PIE (SVG)
// ─────────────────────────────────────────────
function render_pie(d) {
	let counts = d.status_counts || {};
	let total  = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
	document.getElementById("ftd-proj-badge").textContent = total + " projects";

	let colors = {
		"Order Received":    "#3b82f6",
		"Material Planning": "#8b5cf6",
		"WIP":               "#f59e0b",
		"Completed":         "#10b981",
		"Cancelled":         "#ef4444",
		"Unknown":           "#94a3b8",
	};

	let entries = Object.entries(counts);
	if (!entries.length) {
		document.getElementById("ftd-pie-area").innerHTML = empty("No project data");
		return;
	}

	// Draw SVG pie
	let cx = 80, cy = 80, r = 70, angle = -Math.PI / 2, paths = "";
	entries.forEach(([k, v]) => {
		let slice = (v / total) * 2 * Math.PI;
		let x1 = cx + r * Math.cos(angle), y1 = cy + r * Math.sin(angle);
		angle += slice;
		let x2 = cx + r * Math.cos(angle), y2 = cy + r * Math.sin(angle);
		let lg = slice > Math.PI ? 1 : 0;
		let col = colors[k] || "#94a3b8";
		paths += `<path d="M${cx},${cy} L${x1.toFixed(2)},${y1.toFixed(2)} A${r},${r} 0 ${lg},1 ${x2.toFixed(2)},${y2.toFixed(2)} Z" fill="${col}" stroke="#fff" stroke-width="2"/>`;
	});

	let legend = entries.map(([k, v]) => `
		<div class="ftd-legend-item">
			<span class="ftd-legend-dot" style="background:${colors[k]||'#94a3b8'}"></span>
			<span class="ftd-legend-label">${k}</span>
			<span class="ftd-legend-val">${v}</span>
		</div>
	`).join("");

	document.getElementById("ftd-pie-area").innerHTML = `
		<div class="ftd-pie-wrap">
			<svg viewBox="0 0 160 160" width="150" height="150">${paths}</svg>
			<div class="ftd-legend">${legend}</div>
		</div>`;
}

// ─────────────────────────────────────────────
// 3. STAGE BAR
// ─────────────────────────────────────────────
function render_stage_bar(d) {
	let stages = d.stage_summary || [];
	if (!stages.length) {
		document.getElementById("ftd-stage-bar").innerHTML = empty("No stage data");
		return;
	}
	let bars = stages.map(s => `
		<div class="ftd-bar-row">
			<div class="ftd-bar-label" title="${s.stage}">${s.stage}</div>
			<div class="ftd-bar-track">
				<div class="ftd-bar-fill" style="width:${s.avg_pct}%"></div>
			</div>
			<div class="ftd-bar-pct">${s.avg_pct}%</div>
		</div>
	`).join("");
	document.getElementById("ftd-stage-bar").innerHTML = `<div class="ftd-bars">${bars}</div>`;
}

// ─────────────────────────────────────────────
// 4. TRANSACTION TABLE
// ─────────────────────────────────────────────
function render_txn_table(d) {
	let data = d.transactions || [];
	document.getElementById("ftd-txn-badge").textContent = d.total_transactions + " total";
	if (!data.length) {
		document.getElementById("ftd-txn-table").innerHTML = empty("No transactions");
		return;
	}
	let rows = data.map(t => `
		<tr>
			<td><a class="ftd-link" href="/app/ft-project-stages/${t.project_number}">${t.project_number||"—"}</a></td>
			<td>${t.stages||"—"}</td>
			<td>${t.date||"—"}</td>
			<td class="ftd-add">+${t.addition||0}</td>
			<td class="ftd-sub">-${t.subtraction||0}</td>
			<td>
				<div class="ftd-mini-bar-wrap">
					<div class="ftd-mini-bar" style="width:${t.work_completed||0}%"></div>
					<span>${t.work_completed||0}%</span>
				</div>
			</td>
		</tr>
	`).join("");
	document.getElementById("ftd-txn-table").innerHTML = `
		<table class="ftd-table">
			<thead><tr><th>Project</th><th>Stage</th><th>Date</th><th>Add</th><th>Sub</th><th>Done</th></tr></thead>
			<tbody>${rows}</tbody>
		</table>`;
}

// ─────────────────────────────────────────────
// 5. PROJECT PROGRESS
// ─────────────────────────────────────────────
function render_proj_progress(d) {
	let data = d.projects || [];
	if (!data.length) {
		document.getElementById("ftd-proj-progress").innerHTML = empty("No projects");
		return;
	}
	let pc = { "Order Received":"#3b82f6","Material Planning":"#8b5cf6","WIP":"#f59e0b","Completed":"#10b981","Cancelled":"#ef4444" };
	let pr = { High:"#ef4444", Medium:"#f59e0b", Low:"#10b981" };
	let html = data.map(p => {
		let pct   = p.percentage_completed || 0;
		let color = pc[p.status] || "#3b82f6";
		let prio  = p.priority || "";
		return `
		<div class="ftd-proj-row">
			<div class="ftd-proj-top">
				<a class="ftd-link ftd-proj-name" href="/app/ft-project/${p.name}">${p.name}</a>
				<div style="display:flex;gap:5px;align-items:center">
					${prio ? `<span class="ftd-badge" style="background:${pr[prio]}20;color:${pr[prio]}">${prio}</span>` : ""}
					<span class="ftd-badge" style="background:${color}20;color:${color}">${p.status||"—"}</span>
					<b style="font-size:13px">${pct}%</b>
				</div>
			</div>
			<div class="ftd-proj-track">
				<div class="ftd-proj-fill" style="width:${pct}%;background:${color}"></div>
			</div>
			<div class="ftd-proj-meta">${fmt(p.total_weight||0,2)} Kg</div>
		</div>`;
	}).join("");
	document.getElementById("ftd-proj-progress").innerHTML = html;
}

// ─────────────────────────────────────────────
// 6. DRAWING TABLE
// ─────────────────────────────────────────────
// function render_draw_table(d) {
// 	let data = d.drawings || [];
// 	document.getElementById("ftd-draw-badge").textContent = d.total_drawings + " total";
// 	if (!data.length) {
// 		document.getElementById("ftd-draw-table").innerHTML = empty("No drawings");
// 		return;
// 	}
// 	let rows = data.map(dr => `
// 		<tr>
// 			<td>${dr.drawing_number||dr.name}</td>
// 			<td><a class="ftd-link" href="/app/ft-project/${dr.project_number}">${dr.project_number||"—"}</a></td>
// 			<td>${dr.customer_name||"—"}</td>
// 			<td class="ftd-num">${fmt(dr.unit_weight||0,3)}</td>
// 		</tr>
// 	`).join("");
// 	document.getElementById("ftd-draw-table").innerHTML = `
// 		<table class="ftd-table">
// 			<thead><tr><th>Drawing No</th><th>Project</th><th>Customer</th><th>Unit Wt (Kg)</th></tr></thead>
// 			<tbody>${rows}</tbody>
// 		</table>`;
// }
function render_draw_table(d) {
	let data = d.drawings || [];
	document.getElementById("ftd-draw-badge").textContent = d.total_drawings + " total";
	if (!data.length) {
		document.getElementById("ftd-draw-table").innerHTML = empty("No drawings");
		return;
	}

	// Store data globally for filtering
	window._ftd_drawings = data;

	let filter_bar = `
		<div class="ftd-draw-filter">
			<input
				type="text"
				id="ftd-draw-search"
				class="ftd-draw-input"
				placeholder="🔍  Search drawing no, project, customer..."
				oninput="ftd_filter_drawings()"
			/>
		</div>
	`;

	document.getElementById("ftd-draw-table").innerHTML = filter_bar + `
		<div id="ftd-draw-table-inner" class="ftd-table-wrap"></div>
	`;

	ftd_render_draw_rows(data);
}

function ftd_render_draw_rows(data) {
	if (!data.length) {
		document.getElementById("ftd-draw-table-inner").innerHTML = empty("No matching drawings");
		return;
	}
	let rows = data.map(dr => `
		<tr>
			<td>${dr.drawing_number || dr.name}</td>
			<td><a class="ftd-link" href="/app/ft-project/${dr.project_number}">${dr.project_number || "—"}</a></td>
			<td>${dr.customer_name || "—"}</td>
			<td class="ftd-num">${fmt(dr.unit_weight || 0, 3)}</td>
		</tr>
	`).join("");
	document.getElementById("ftd-draw-table-inner").innerHTML = `
		<table class="ftd-table">
			<thead><tr><th>Drawing No</th><th>Project</th><th>Customer</th><th>Unit Wt (Kg)</th></tr></thead>
			<tbody>${rows}</tbody>
		</table>`;
}

window.ftd_filter_drawings = function () {
	let txt = (document.getElementById("ftd-draw-search")?.value || "").toLowerCase();
	let data = window._ftd_drawings || [];
	let filtered = data.filter(d =>
		(d.drawing_number || "").toLowerCase().includes(txt) ||
		(d.project_number || "").toLowerCase().includes(txt) ||
		(d.customer_name  || "").toLowerCase().includes(txt)
	);
	ftd_render_draw_rows(filtered);
};

// ─────────────────────────────────────────────
// 7. ADDITION vs SUBTRACTION
// ─────────────────────────────────────────────
function render_add_sub(d) {
	let stages = d.stage_summary || [];
	if (!stages.length) {
		document.getElementById("ftd-add-sub").innerHTML = empty("No data");
		return;
	}
	let max_val = Math.max(...stages.map(s => Math.max(s.addition, s.subtraction)), 1);
	let bars = stages.map(s => `
		<div class="ftd-as-row">
			<div class="ftd-as-label" title="${s.stage}">${s.stage}</div>
			<div class="ftd-as-bars">
				<div class="ftd-as-bar-wrap">
					<div class="ftd-as-fill ftd-as-add" style="width:${(s.addition/max_val)*100}%"></div>
					<span class="ftd-as-num">${s.addition}</span>
				</div>
				<div class="ftd-as-bar-wrap">
					<div class="ftd-as-fill ftd-as-sub" style="width:${(s.subtraction/max_val)*100}%"></div>
					<span class="ftd-as-num">${s.subtraction}</span>
				</div>
			</div>
		</div>
	`).join("");
	document.getElementById("ftd-add-sub").innerHTML = `
		<div class="ftd-as-legend">
			<span><span class="ftd-dot" style="background:#10b981"></span> Addition</span>
			<span><span class="ftd-dot" style="background:#ef4444"></span> Subtraction</span>
		</div>
		<div class="ftd-as-list">${bars}</div>`;
}

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────
function fmt(n, dec) {
	return Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: dec, maximumFractionDigits: dec });
}
function empty(msg) { return `<p class="ftd-empty">${msg}</p>`; }
function skeletons(n) { return Array(n).fill(`<div class="ftd-card ftd-skeleton"></div>`).join(""); }

// ─────────────────────────────────────────────
// CSS
// ─────────────────────────────────────────────
function load_dashboard_css() {
	if (document.getElementById("ftd-style")) return;
	let s = document.createElement("style");
	s.id = "ftd-style";
	s.textContent = `
.ftd-wrap { font-family:'Segoe UI',system-ui,sans-serif; padding:20px; background:#f1f5f9; min-height:100vh; color:#1e293b; }

/* Header */
.ftd-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; flex-wrap:wrap; gap:12px; }
.ftd-header-left { display:flex; align-items:center; gap:14px; }
.ftd-logo { width:48px; height:48px; background:linear-gradient(135deg,#3b82f6,#8b5cf6); border-radius:12px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:18px; color:#fff; box-shadow:0 4px 14px #3b82f640; }
.ftd-title { font-size:22px; font-weight:800; margin:0; letter-spacing:-0.5px; }
.ftd-subtitle { font-size:12px; color:#64748b; margin:0; }
.ftd-header-right { display:flex; align-items:center; gap:10px; }
.ftd-select { padding:8px 14px; border-radius:8px; border:1.5px solid #e2e8f0; background:#fff; font-size:13px; color:#334155; cursor:pointer; }
.ftd-refresh-btn { display:flex; align-items:center; gap:6px; padding:8px 18px; border-radius:8px; background:linear-gradient(135deg,#3b82f6,#6366f1); color:#fff; border:none; cursor:pointer; font-size:13px; font-weight:700; box-shadow:0 2px 8px #3b82f640; }
.ftd-refresh-btn:hover { opacity:.88; }

/* Cards */
.ftd-cards-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px; }
@media(max-width:900px){.ftd-cards-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:500px){.ftd-cards-grid{grid-template-columns:1fr;}}
.ftd-card { background:#fff; border-radius:14px; padding:20px; display:flex; align-items:center; gap:14px; position:relative; overflow:hidden; box-shadow:0 1px 4px #0001; border:1.5px solid #e2e8f0; transition:transform .15s,box-shadow .15s; }
.ftd-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px #0002; }
.ftd-card-bar { position:absolute; left:0; top:0; bottom:0; width:4px; border-radius:14px 0 0 14px; }
.ftd-card-icon { font-size:28px; }
.ftd-card-body { flex:1; }
.ftd-card-label { font-size:11px; color:#64748b; margin:0 0 4px; text-transform:uppercase; letter-spacing:.5px; }
.ftd-card-value { font-size:24px; font-weight:800; margin:0; color:#1e293b; }
.ftd-skeleton { background:linear-gradient(90deg,#e2e8f0 25%,#f8fafc 50%,#e2e8f0 75%); background-size:200% 100%; animation:ftd-sh 1.4s infinite; height:88px; }
@keyframes ftd-sh{0%{background-position:200%}100%{background-position:-200%}}

/* Layout grids */
.ftd-main-grid { display:grid; grid-template-columns:340px 1fr; gap:16px; margin-bottom:16px; }
@media(max-width:900px){.ftd-main-grid{grid-template-columns:1fr;}}
.ftd-col-left,.ftd-col-right { display:flex; flex-direction:column; gap:16px; }
.ftd-bottom-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media(max-width:900px){.ftd-bottom-grid{grid-template-columns:1fr;}}

/* Panel */
.ftd-panel { background:#fff; border-radius:14px; padding:18px; border:1.5px solid #e2e8f0; box-shadow:0 1px 4px #0001; }
.ftd-panel-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
.ftd-panel-title { font-size:12px; font-weight:700; color:#334155; text-transform:uppercase; letter-spacing:.5px; }
.ftd-panel-badge { font-size:11px; background:#f1f5f9; color:#64748b; padding:3px 10px; border-radius:20px; border:1px solid #e2e8f0; }
.ftd-chart-wrap { min-height:80px; }

/* Pie */
.ftd-pie-wrap { display:flex; align-items:center; gap:20px; flex-wrap:wrap; }
.ftd-legend { display:flex; flex-direction:column; gap:7px; flex:1; }
.ftd-legend-item { display:flex; align-items:center; gap:8px; font-size:12px; }
.ftd-legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.ftd-legend-label { flex:1; color:#475569; }
.ftd-legend-val { font-weight:700; color:#1e293b; }

/* Bar */
.ftd-bars { display:flex; flex-direction:column; gap:10px; }
.ftd-bar-row { display:flex; align-items:center; gap:10px; }
.ftd-bar-label { font-size:12px; color:#475569; width:110px; flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ftd-bar-track { flex:1; height:10px; background:#f1f5f9; border-radius:99px; overflow:hidden; }
.ftd-bar-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); transition:width .6s ease; }
.ftd-bar-pct { font-size:12px; font-weight:700; color:#334155; width:36px; text-align:right; }

/* Table */

.ftd-table { width:100%; border-collapse:collapse; font-size:12.5px; }
.ftd-table thead tr { background:#f8fafc; position:sticky; top:0; }
.ftd-table th { padding:9px 12px; text-align:left; font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.4px; border-bottom:1.5px solid #e2e8f0; white-space:nowrap; }
.ftd-table td { padding:8px 12px; border-bottom:1px solid #f1f5f9; color:#334155; white-space:nowrap; }
.ftd-table tbody tr:hover { background:#f8fafc; }
.ftd-num { text-align:right; font-variant-numeric:tabular-nums; }
.ftd-add { color:#10b981; font-weight:700; }
.ftd-sub { color:#ef4444; font-weight:700; }
.ftd-mini-bar-wrap { display:flex; align-items:center; gap:8px; min-width:100px; }
.ftd-mini-bar { height:6px; border-radius:99px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); flex:1; max-width:80px; }
.ftd-mini-bar-wrap span { font-size:11px; font-weight:700; color:#475569; }

/* Project progress */
.ftd-progress-list { display:flex; flex-direction:column; gap:12px; }
.ftd-proj-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; }
.ftd-proj-name { font-size:13px; font-weight:700; }
.ftd-proj-track { height:8px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-bottom:3px; }
.ftd-proj-fill { height:100%; border-radius:99px; transition:width .6s ease; }
.ftd-proj-meta { font-size:11px; color:#94a3b8; }
.ftd-badge { font-size:10px; font-weight:700; padding:2px 8px; border-radius:20px; }

/* Add-Sub */
.ftd-as-legend { display:flex; gap:16px; font-size:12px; margin-bottom:10px; color:#475569; }
.ftd-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:4px; }
.ftd-as-list { display:flex; flex-direction:column; gap:8px; }
.ftd-as-row { display:flex; align-items:center; gap:10px; }
.ftd-as-label { font-size:12px; color:#475569; width:110px; flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ftd-as-bars { flex:1; display:flex; flex-direction:column; gap:3px; }
.ftd-as-bar-wrap { display:flex; align-items:center; gap:6px; }
.ftd-as-fill { height:8px; border-radius:99px; min-width:2px; transition:width .6s; }
.ftd-as-add { background:#10b981; }
.ftd-as-sub { background:#ef4444; }
.ftd-as-num { font-size:11px; font-weight:700; color:#334155; width:32px; }

/* Misc */
.ftd-link { color:#3b82f6; text-decoration:none; font-weight:600; }
.ftd-link:hover { text-decoration:underline; }
.ftd-empty { font-size:13px; color:#94a3b8; text-align:center; padding:20px 0; }



/* Drawing Filter */
.ftd-draw-filter {
	margin-bottom: 10px;
}
.ftd-draw-input {
	width: 100%;
	padding: 8px 14px;
	border-radius: 8px;
	border: 1.5px solid #e2e8f0;
	font-size: 13px;
	color: #334155;
	background: #f8fafc;
	box-sizing: border-box;
	outline: none;
	transition: border-color 0.2s;
}
.ftd-draw-input:focus {
	border-color: #3b82f6;
	background: #fff;
}

#ftd-draw-table-inner {
    max-height: 240px;
    overflow-y: auto;
    overflow-x: auto;
}
#ftd-draw-table-inner .ftd-table thead tr {
    position: sticky !important;
    top: 0 !important;
    z-index: 2;
    background: #f8fafc !important;
}
    .ftd-table-wrap { overflow-x: auto; max-height: 280px; overflow-y: auto; }

#ftd-draw-table { overflow: visible !important; max-height: none !important; }

#ftd-draw-table-inner {
    max-height: 240px;
    overflow-y: auto;
    overflow-x: hidden;
}

#ftd-draw-table-inner .ftd-table { table-layout: fixed; width: 100%; }

#ftd-draw-table-inner .ftd-table thead tr {
    position: sticky !important;
    top: 0 !important;
    z-index: 2;
    background: #f8fafc !important;
    box-shadow: 0 1px 0 #e2e8f0;
}

#ftd-draw-table-inner .ftd-table th:nth-child(1),
#ftd-draw-table-inner .ftd-table td:nth-child(1) { width: 32%; }

#ftd-draw-table-inner .ftd-table th:nth-child(2),
#ftd-draw-table-inner .ftd-table td:nth-child(2) { width: 14%; }

#ftd-draw-table-inner .ftd-table th:nth-child(3),
#ftd-draw-table-inner .ftd-table td:nth-child(3) { width: 36%; }

#ftd-draw-table-inner .ftd-table th:nth-child(4),
#ftd-draw-table-inner .ftd-table td:nth-child(4) { width: 18%; text-align: right; }

#ftd-draw-table-inner .ftd-table td {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
    /* NAYA — add karo */
#ftd-draw-table-inner {
    max-height: 240px;
    overflow-y: auto;
    overflow-x: auto;
}
#ftd-draw-table-inner .ftd-table thead tr {
    position: sticky !important;
    top: 0 !important;
    z-index: 2;
    background: #f8fafc !important;
}
`;
	document.head.appendChild(s);
}