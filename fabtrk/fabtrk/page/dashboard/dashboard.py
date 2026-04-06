import frappe

@frappe.whitelist()
def get_dashboard_data():
    return {
        "total_projects": 3,
        "total_stages": 15,
        "avg_completion": 64,
        "completed": 1,
        "projects": [
            {
                "name": "Refinery Module A",
                "progress": 92,
                "status": "On Track",
                "color": "#4caf50"
            },
            {
                "name": "Pipeline Segment B",
                "progress": 44,
                "status": "Delayed",
                "color": "#ff9800"
            },
            {
                "name": "Structural Frame C",
                "progress": 100,
                "status": "Completed",
                "color": "#8bc34a"
            }
        ]
    }