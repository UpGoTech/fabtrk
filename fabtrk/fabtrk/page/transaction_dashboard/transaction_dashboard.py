import frappe


@frappe.whitelist()
def get_dashboard_data(project=None, projects=None):
    import json

    # Multiple projects support
    project_list = []
    if projects:
        project_list = json.loads(projects) if isinstance(projects, str) else projects

    proj_filter = {}
    if project_list and len(project_list) > 0:
        proj_filter["name"] = ["in", project_list]
    elif project:
        proj_filter["name"] = project
    else:
        proj_filter["is_active"] = 1
        
        
        

    # ── 1. Projects
    projects = frappe.db.get_all(
        "FT Project",
        filters=proj_filter,
        fields=["name", "status", "priority", "percentage_completed", "total_weight", "excepted_start_date", "excepted_end_date"],
        # limit=0
    )

    total_projects    = len(projects)
    total_weight      = sum(p.get("total_weight") or 0 for p in projects)

    # Status counts for pie chart
    status_counts = {}
    for p in projects:
        s = p.get("status") or "Unknown"
        status_counts[s] = status_counts.get(s, 0) + 1

    # # ── 2. Drawings
    draw_filter = {}
    if project_list:
        draw_filter["project_number"] = ["in", project_list]
    elif project:
        draw_filter["project_number"] = project

    drawings = frappe.db.get_all(
        "FT Add Drawing",
        filters=draw_filter,
        fields=["name", "drawing_number", "project_number", "unit_weight", "customer_name"],
        order_by="modified desc",
        # limit=15
    )
    total_drawings = frappe.db.count("FT Add Drawing", filters=draw_filter)

    # ── 3. PO Drawings total weight
    po_filter = {}
    if project_list:
        po_filter["project_number"] = ["in", project_list]
    elif project:
        po_filter["project_number"] = project
        
        
    po_rows = frappe.db.get_all(
        "FT Po Drawing",
        filters=po_filter,
        fields=["total_weight", "required_qty"],
        # limit=0
    )
    po_total_weight = sum(p.get("total_weight") or 0 for p in po_rows)
    po_total_qty    = sum(p.get("required_qty") or 0 for p in po_rows)

    # ── 4. Transactions
    txn_filter = {}
    if project_list:
        txn_filter["project_number"] = ["in", project_list]
    elif project:
        txn_filter["project_number"] = project

    transactions = frappe.db.get_all(
        "FT Transaction",
        filters=txn_filter,
        fields=["name", "project_number", "stages", "date", "addition", "subtraction", "work_completed"],
        order_by="date desc",
        # limit=20
    )
    total_transactions = frappe.db.count("FT Transaction", filters=txn_filter)

    # ── 5. Stage-wise aggregation
    all_txn = frappe.db.get_all(
        "FT Transaction",
        filters=txn_filter,
        fields=["stages", "work_completed", "addition", "subtraction"],
        # limit=0
    )

    stage_map = {}
    for t in all_txn:
        s = t.get("stages") or "Unknown"
        if s not in stage_map:
            stage_map[s] = {"total_pct": 0, "count": 0, "addition": 0, "subtraction": 0}
        stage_map[s]["total_pct"]   += t.get("work_completed") or 0
        stage_map[s]["count"]       += 1
        stage_map[s]["addition"]    += t.get("addition") or 0
        stage_map[s]["subtraction"] += t.get("subtraction") or 0

    stage_summary = [
        {
            "stage":       s,
            "avg_pct":     round(v["total_pct"] / v["count"], 1) if v["count"] else 0,
            "addition":    v["addition"],
            "subtraction": v["subtraction"],
            "count":       v["count"],
        }
        for s, v in stage_map.items()
    ]
    stage_summary.sort(key=lambda x: x["avg_pct"], reverse=True)

    # ── 6. Project Stages list
    ps_filter = {}
    if project_list:
        ps_filter["project_number"] = ["in", project_list]
    elif project:
        ps_filter["project_number"] = project
        
        
        
    project_stages = frappe.db.get_all(
        "FT Project Stages",
        filters=ps_filter,
        fields=["name", "project_number", "date"],
        order_by="date desc",
        # limit=0
    )

    return {
        # Summary cards
        "total_projects":      total_projects,
        "total_drawings":      total_drawings,
        "total_weight":        round(float(total_weight), 3),
        "total_transactions":  total_transactions,
        "po_total_weight":     round(float(po_total_weight), 3),
        "po_total_qty":        int(po_total_qty),

        # Charts
        "status_counts":  status_counts,
        "stage_summary":  stage_summary,

        # Tables
        "projects":       [dict(p) for p in projects[:10]],
        "drawings":       [dict(d) for d in drawings],
        "transactions":   [dict(t) for t in transactions],
        "project_stages": [dict(ps) for ps in project_stages],
    }


@frappe.whitelist()
def get_active_projects():
    """Project filter dropdown ke liye"""
    return frappe.db.get_all(
        "FT Project",
        filters={"is_active": 1},
        fields=["name"],
        order_by="name asc",
        # limit=0
    )