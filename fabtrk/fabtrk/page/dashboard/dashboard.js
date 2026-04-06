frappe.pages['dashboard'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Project Progress Dashboard',
        single_column: true
    });

    load_dashboard(page);
};

function load_dashboard(page) {

    frappe.call({
        method: "fabtrk.fabtrk.page.dashboard.dashboard.get_dashboard_data",
        callback: function(r) {

            let data = r.message;

            $(page.body).html(`
                <div style="padding:20px">

                    <!-- TOP CARDS -->
                    <div style="display:flex; gap:20px; margin-bottom:20px;">
                        ${card("Total Projects", data.total_projects)}
                        ${card("Total Stages", data.total_stages)}
                        ${card("Avg Completion", data.avg_completion + "%")}
                        ${card("Completed", data.completed)}
                    </div>

                    <!-- CHARTS -->
                    <div style="display:flex; gap:20px;">
                        <div id="bar-chart" style="flex:1;"></div>
                        <div id="donut-chart" style="flex:1;"></div>
                    </div>

                    <!-- PROJECT LIST -->
                    <h3 style="margin-top:30px;">All Projects</h3>
                    <div id="project-list"></div>

                </div>
            `);

            render_charts();
            render_projects(data.projects);
        }
    });
}

// ✅ CARD UI
function card(title, value) {
    return `
        <div style="flex:1; padding:15px; background:#1e1e1e; border-radius:10px;">
            <h4 style="color:#aaa">${title}</h4>
            <h2 style="color:white">${value}</h2>
        </div>
    `;
}

// ✅ CHARTS
function render_charts() {

    new frappe.Chart("#bar-chart", {
        data: {
            labels: ["Refinery", "Pipeline", "Structural"],
            datasets: [{
                values: [60, 30, 100]
            }]
        },
        type: 'bar',
        height: 250,
        colors: ['#4caf50']
    });

    new frappe.Chart("#donut-chart", {
        data: {
            labels: ["Done", "In Progress", "Pending"],
            datasets: [{
                values: [40, 30, 30]
            }]
        },
        type: 'donut',
        height: 250,
        colors: ['#4caf50', '#ff9800', '#ccc']
    });
}

// ✅ PROJECT LIST UI
function render_projects(projects) {

    let html = "";

    projects.forEach(p => {

        html += `
            <div style="background:#1e1e1e; padding:15px; margin-top:15px; border-radius:10px;">
                
                <div style="display:flex; justify-content:space-between;">
                    <h4 style="color:white">${p.name}</h4>
                    <span style="color:${p.color}">${p.status}</span>
                </div>

                <div style="background:#333; height:8px; border-radius:5px; margin-top:10px;">
                    <div style="width:${p.progress}%; background:${p.color}; height:8px; border-radius:5px;"></div>
                </div>

                <div style="margin-top:5px; color:#aaa;">
                    ${p.progress}%
                </div>

            </div>
        `;
    });

    $("#project-list").html(html);
}