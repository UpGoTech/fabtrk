frappe.pages['transaction-dashboard'].on_page_load = function (wrapper) {

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Transaction Dashboard',
        single_column: true
    });

    // ── CSS inject ──────────────────────────────────────────────────────────
    if (!document.getElementById('td-dashboard-style')) {
        var style = document.createElement('style');
        style.id = 'td-dashboard-style';
        style.innerHTML = `
            .td-wrap { padding: 20px; }
            .td-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; flex-wrap:wrap; gap:10px; }
            .td-title  { font-size:20px; font-weight:500; margin:0; color:var(--text-color); }
            .td-header select { font-size:13px; padding:5px 10px; border-radius:6px; border:1px solid var(--border-color); background:var(--control-bg); color:var(--text-color); }

            .td-metric-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:10px; margin-bottom:20px; }
            .td-mc       { background:var(--fg-color); border:1px solid var(--border-color); border-radius:8px; padding:14px 12px; }
            .td-mc-label { font-size:11px; color:var(--text-muted); margin-bottom:6px; text-transform:uppercase; letter-spacing:0.03em; }
            .td-mc-val   { font-size:24px; font-weight:500; color:var(--text-color); }

            .td-chart-row  { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px; }
            .td-chart-card { background:var(--fg-color); border:1px solid var(--border-color); border-radius:10px; padding:16px; }

            .td-card { background:var(--fg-color); border:1px solid var(--border-color); border-radius:10px; padding:16px; }
            .td-sec-title { font-size:11px; font-weight:500; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:10px; }

            .td-legend-row { display:flex; gap:14px; flex-wrap:wrap; margin-top:8px; font-size:12px; color:var(--text-muted); align-items:center; }
            .td-leg-dot    { width:10px; height:10px; border-radius:2px; display:inline-block; margin-right:3px; vertical-align:middle; }

            .td-proj-card  { background:var(--fg-color); border:1px solid var(--border-color); border-radius:10px; padding:16px; margin-bottom:14px; }
            .td-proj-head  { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; flex-wrap:wrap; gap:8px; }
            .td-proj-title { font-size:15px; font-weight:500; color:var(--text-color); }
            .td-proj-id    { font-size:12px; font-weight:400; color:var(--text-muted); margin-left:6px; }
            .td-proj-sub   { font-size:12px; color:var(--text-muted); margin-top:4px; line-height:1.6; }
            .td-pct-big    { font-size:24px; font-weight:500; margin-top:4px; }

            .td-prog-wrap { background:var(--border-color); border-radius:4px; height:8px; margin:6px 0 3px; overflow:hidden; }
            .td-prog-bar  { height:8px; border-radius:4px; transition:width 0.5s ease; }

            .td-mini-prog { display:inline-block; width:60px; height:5px; background:var(--border-color); border-radius:3px; vertical-align:middle; margin-left:6px; overflow:hidden; }
            .td-mini-bar  { display:block; height:5px; border-radius:3px; }

            .td-stage-table    { width:100%; border-collapse:collapse; font-size:13px; margin-top:6px; }
            .td-stage-table th { text-align:left; padding:7px 8px; border-bottom:1px solid var(--border-color); font-size:11px; color:var(--text-muted); font-weight:500; background:var(--subtle-fg); }
            .td-stage-table td { padding:7px 8px; border-bottom:1px solid var(--border-color); color:var(--text-color); }
            .td-stage-table tr:last-child td { border-bottom:none; }
            .td-stage-table tr:hover td { background:var(--subtle-fg); }

            .td-sum-table    { width:100%; border-collapse:collapse; font-size:13px; }
            .td-sum-table th { text-align:left; padding:8px 10px; border-bottom:1px solid var(--border-color); font-size:11px; color:var(--text-muted); font-weight:500; background:var(--subtle-fg); white-space:nowrap; }
            .td-sum-table td { padding:8px 10px; border-bottom:1px solid var(--border-color); color:var(--text-color); }
            .td-sum-table tr:last-child td { border-bottom:none; }

            .td-badge       { display:inline-block; font-size:11px; font-weight:500; padding:2px 9px; border-radius:4px; }
            .td-badge-green { background:#EAF3DE; color:#3B6D11; }
            .td-badge-blue  { background:#E6F1FB; color:#185FA5; }
            .td-badge-red   { background:#FCEBEB; color:#A32D2D; }
            .td-badge-amber { background:#FAEEDA; color:#854F0B; }
            .td-badge-gray  { background:#F1EFE8; color:#5F5E5A; }

            .td-stage-pill { display:inline-block; font-size:11px; padding:2px 9px; border-radius:20px; font-weight:500; }
            .td-stage-done { background:#EAF3DE; color:#3B6D11; }
            .td-stage-prog { background:#FAEEDA; color:#854F0B; }
            .td-stage-pend { background:#F1EFE8; color:#5F5E5A; }

            .td-empty { text-align:center; padding:40px; color:var(--text-muted); font-size:14px; }

            @media (max-width:1100px) { .td-metric-grid { grid-template-columns:repeat(3,1fr); } }
            @media (max-width:800px)  { .td-chart-row   { grid-template-columns:1fr; } .td-metric-grid { grid-template-columns:repeat(2,1fr); } }
        `;
        document.head.appendChild(style);
    }

    // ── HTML inject ─────────────────────────────────────────────────────────
    $(wrapper).find('.page-content').html(`
        <div class="td-wrap">

            <div class="td-header">
                <h1 class="td-title">Project Tracking Dashboard</h1>
                <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                    <select id="td-status-filter">
                        <option value="all">All Statuses</option>
                        <option value="Completed">Completed</option>
                        <option value="On Track">On Track</option>
                        <option value="Delayed">Delayed</option>
                        <option value="Not Started">Not Started</option>
                    </select>
                    <button class="btn btn-sm btn-default" id="td-refresh-btn">&#8635; Refresh</button>
                </div>
            </div>

            <div class="td-metric-grid">
                <div class="td-mc"><div class="td-mc-label">Total Projects</div><div class="td-mc-val" id="td-m-total">—</div></div>
                <div class="td-mc"><div class="td-mc-label">Avg Completion</div><div class="td-mc-val" id="td-m-avg">—</div></div>
                <div class="td-mc"><div class="td-mc-label">Completed</div><div class="td-mc-val" id="td-m-done">—</div></div>
                <div class="td-mc"><div class="td-mc-label">Total Stages</div><div class="td-mc-val" id="td-m-stages">—</div></div>
                <div class="td-mc"><div class="td-mc-label">Total Target Units</div><div class="td-mc-val" id="td-m-target">—</div></div>
                <div class="td-mc"><div class="td-mc-label">Total Completed Units</div><div class="td-mc-val" id="td-m-completed">—</div></div>
            </div>

            <div class="td-chart-row">
                <div class="td-chart-card">
                    <div class="td-sec-title">Project Completion %</div>
                    <div style="position:relative;height:220px;">
                        <canvas id="td-bar-chart"></canvas>
                    </div>
                </div>
                <div class="td-chart-card">
                    <div class="td-sec-title">Projects by Status</div>
                    <div style="position:relative;height:180px;">
                        <canvas id="td-donut-chart"></canvas>
                    </div>
                    <div class="td-legend-row" id="td-donut-legend"></div>
                </div>
            </div>

            <div class="td-sec-title" style="margin:4px 0 10px;">Project Details</div>
            <div id="td-project-cards"></div>

            <div class="td-card" style="margin-top:16px;">
                <div class="td-sec-title">All Projects Summary</div>
                <div style="overflow-x:auto;">
                    <table class="td-sum-table">
                        <thead>
                            <tr>
                                <th>Project ID</th>
                                <th>Project Name</th>
                                <th>Customer</th>
                                <th>Stages</th>
                                <th>Target Units</th>
                                <th>Completed Units</th>
                                <th>Completion %</th>
                                <th>Status</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                            </tr>
                        </thead>
                        <tbody id="td-summary-tbody"></tbody>
                    </table>
                </div>
            </div>

        </div>
    `);

    // ── Events ───────────────────────────────────────────────────────────────
    window._tdData = [];

    $(wrapper).on('click', '#td-refresh-btn', function () {
        tdLoad();
    });

    $(wrapper).on('change', '#td-status-filter', function () {
        tdApplyFilter();
    });

    // ── Load Chart.js then data ───────────────────────────────────────────────
    if (typeof Chart !== 'undefined') {
        tdLoad();
    } else {
        frappe.require(
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js',
            function () { tdLoad(); }
        );
    }
};


// DATA LOAD
function tdLoad() {
    frappe.call({
        method: 'fabtrk.fabtrk.page.transaction_dashboard.transaction_dashboard.get_dashboard_data',
        freeze: true,
        freeze_message: 'Loading dashboard...',
        callback: function (r) {
            if (r.message && r.message.length) {
                window._tdData = r.message;
                tdRenderAll(r.message);
            } else {
                $('#td-project-cards').html(
                    '<div class="td-empty">No data found. Add transactions in FT Transaction.</div>'
                );
                console.warn('Dashboard: empty response', r);
            }
        },
        error: function (r) {
            frappe.msgprint('Dashboard API error — check F12 Console.');
            console.error('Dashboard error:', r);
        }
    });
}

function tdApplyFilter() {
    var sf = $('#td-status-filter').val() || 'all';
    var data = window._tdData || [];
    var filtered = sf === 'all'
        ? data
        : data.filter(function (p) {
            return (p.status || '').toLowerCase() === sf.toLowerCase();
        });
    tdRenderAll(filtered);
}

function tdRenderAll(data) {
    tdMetrics(data);
    tdBarChart(data);
    tdDonut(data);
    tdCards(data);
    tdTable(data);
}


// HELPERS
function tdColor(pct) {
    if (pct === 100) return '#639922';
    if (pct >= 60) return '#378ADD';
    if (pct > 0) return '#EF9F27';
    return '#B4B2A9';
}

function tdBadge(status) {
    var map = {
        'completed': 'td-badge-green',
        'on track': 'td-badge-blue',
        'delayed': 'td-badge-red',
        'not started': 'td-badge-gray',
        'open': 'td-badge-blue',
        'cancelled': 'td-badge-red',
        'on hold': 'td-badge-amber'
    };
    var cls = map[(status || '').toLowerCase()] || 'td-badge-gray';
    return '<span class="td-badge ' + cls + '">' + (status || '—') + '</span>';
}

function tdStagePill(pct) {
    if (pct === 100) return '<span class="td-stage-pill td-stage-done">Done</span>';
    if (pct > 0) return '<span class="td-stage-pill td-stage-prog">In Progress</span>';
    return '<span class="td-stage-pill td-stage-pend">Pending</span>';
}

// METRICS
function tdMetrics(data) {
    var avg = data.length
        ? Math.round(data.reduce(function (a, p) { return a + (p.overall_pct || 0); }, 0) / data.length)
        : 0;
    var done = data.filter(function (p) { return p.overall_pct === 100; }).length;
    var totalStages = data.reduce(function (a, p) { return a + (p.total_stages || 0); }, 0);
    var totalTgt = data.reduce(function (a, p) { return a + (p.total_target || 0); }, 0);
    var totalComp = data.reduce(function (a, p) { return a + (p.total_completed || 0); }, 0);

    $('#td-m-total').text(data.length);
    $('#td-m-avg').text(avg + '%');
    $('#td-m-done').text(done);
    $('#td-m-stages').text(totalStages);
    $('#td-m-target').text(totalTgt);
    $('#td-m-completed').text(totalComp);
}

// BAR CHART
var _tdBarInst = null;
function tdBarChart(data) {
    if (_tdBarInst) { _tdBarInst.destroy(); _tdBarInst = null; }
    var ctx = document.getElementById('td-bar-chart');
    if (!ctx || !data.length) return;

    _tdBarInst = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(function (p) {
                return p.name.length > 14 ? p.name.substring(0, 13) + '…' : p.name;
            }),
            datasets: [{
                data: data.map(function (p) { return p.overall_pct || 0; }),
                backgroundColor: data.map(function (p) { return tdColor(p.overall_pct || 0); }),
                borderRadius: 4,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    min: 0, max: 100,
                    ticks: { callback: function (v) { return v + '%'; } },
                    grid: { color: 'rgba(128,128,128,0.1)' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

// DONUT CHART
var _tdDonutInst = null;
function tdDonut(data) {
    if (_tdDonutInst) { _tdDonutInst.destroy(); _tdDonutInst = null; }
    var ctx = document.getElementById('td-donut-chart');
    if (!ctx || !data.length) return;

    var counts = {};
    data.forEach(function (p) {
        var s = p.status || 'Unknown';
        counts[s] = (counts[s] || 0) + 1;
    });
    var colors = ['#378ADD', '#639922', '#EF9F27', '#E24B4A', '#B4B2A9', '#7F77DD'];
    var labels = Object.keys(counts);
    var values = Object.values(counts);

    _tdDonutInst = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: { legend: { display: false } }
        }
    });

    $('#td-donut-legend').html(
        labels.map(function (l, i) {
            return '<span><span class="td-leg-dot" style="background:' + colors[i] + ';"></span>' + l + ' (' + values[i] + ')</span>';
        }).join('')
    );
}

// PROJECT CARDS
function tdCards(data) {
    if (!data || !data.length) {
        $('#td-project-cards').html('<div class="td-empty">No projects found.</div>');
        return;
    }

    var html = data.map(function (p) {
        var pct = p.overall_pct || 0;

        var stageRows = (p.stages || []).map(function (s) {
            return '<tr>'
                + '<td>' + (s.key || '') + '</td>'
                + '<td style="font-weight:500;">' + s.name + '</td>'
                + '<td>' + s.target + '</td>'
                + '<td>' + s.completed + '</td>'
                + '<td>' + s.remaining + '</td>'
                + '<td>'
                + '<span style="color:' + tdColor(s.pct) + ';font-weight:500;">' + s.pct + '%</span>'
                + '<span class="td-mini-prog"><span class="td-mini-bar" style="width:' + s.pct + '%;background:' + tdColor(s.pct) + ';"></span></span>'
                + '</td>'
                + '<td>' + tdStagePill(s.pct) + '</td>'
                + '<td style="color:var(--text-muted);">' + s.tx_count + ' entries</td>'
                + '</tr>';
        }).join('');

        return '<div class="td-proj-card">'
            + '<div class="td-proj-head">'
            + '<div>'
            + '<div class="td-proj-title">' + p.name + ' <span class="td-proj-id">' + p.id + '</span></div>'
            + '<div class="td-proj-sub">'
            + 'Customer: <strong>' + p.customer + '</strong>'
            + ' &nbsp;|&nbsp; ' + p.start_date + ' → ' + p.end_date
            + ' &nbsp;|&nbsp; Target(Addition): <strong>' + p.total_target + '</strong>'
            + ' &nbsp;|&nbsp; Done: <strong>' + p.total_completed + '</strong>'
            + '</div>'
            + '</div>'
            + '<div style="text-align:right;">'
            + tdBadge(p.status)
            + '<div class="td-pct-big" style="color:' + tdColor(pct) + ';">' + pct + '%</div>'
            + '</div>'
            + '</div>'
            + '<div class="td-prog-wrap"><div class="td-prog-bar" style="width:' + pct + '%;background:' + tdColor(pct) + ';"></div></div>'
            + '<div style="display:flex;justify-content:space-between;font-size:11px;color:#888;margin-bottom:12px;"><span>0%</span><span>100%</span></div>'
            + '<div class="td-sec-title">Stage Breakdown (' + p.total_stages + ' stages)</div>'
            + '<div style="overflow-x:auto;">'
            + '<table class="td-stage-table">'
            + '<thead><tr><th>Key</th><th>Stage Name</th><th>Target</th><th>Completed</th><th>Remaining</th><th>%</th><th>Status</th><th>Transactions</th></tr></thead>'
            + '<tbody>' + stageRows + '</tbody>'
            + '</table>'
            + '</div>'
            + '</div>';
    }).join('');

    $('#td-project-cards').html(html);
}

// SUMMARY TABLE
function tdTable(data) {
    var rows = (data || []).map(function (p) {
        return '<tr>'
            + '<td><a href="/app/ft-project/' + p.id + '" target="_blank" style="color:var(--primary);">' + p.id + '</a></td>'
            + '<td style="font-weight:500;">' + p.name + '</td>'
            + '<td>' + p.customer + '</td>'
            + '<td>' + p.total_stages + '</td>'
            + '<td>' + p.total_target + '</td>'
            + '<td>' + p.total_completed + '</td>'
            + '<td style="color:' + tdColor(p.overall_pct) + ';font-weight:500;">'
            + p.overall_pct + '%'
            + '<span class="td-mini-prog"><span class="td-mini-bar" style="width:' + p.overall_pct + '%;background:' + tdColor(p.overall_pct) + ';"></span></span>'
            + '</td>'
            + '<td>' + tdBadge(p.status) + '</td>'
            + '<td>' + p.start_date + '</td>'
            + '<td>' + p.end_date + '</td>'
            + '</tr>';
    }).join('');

    $('#td-summary-tbody').html(rows);
}



