# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

import frappe
import json


@frappe.whitelist()
def get_tracking_summary(projects=None):
    """
    Get complete tracking summary - Projects, Drawings, Transactions, Stock
    """
    project_list = []
    if projects:
        try:
            project_list = json.loads(projects) if isinstance(projects, str) else projects
        except Exception:
            project_list = [projects]

    proj_filter = {}
    if project_list:
        proj_filter["name"] = ["in", project_list]
    else:
        proj_filter["is_active"] = 1

    # ── 1. PROJECTS SUMMARY
    projects = frappe.db.get_all(
        "FT Project",
        filters=proj_filter,
        fields=["name", "status", "percentage_completed", "total_weight", "customer_name", "project_type"],
        order_by="modified desc"
    )
    
    total_projects = len(projects)
    total_weight = sum(p.get("total_weight") or 0 for p in projects)
    
    # Status breakdown
    status_counts = {}
    for p in projects:
        status = p.get("status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    completed_projects = len([p for p in projects if p.get("status") == "Completed"])
    ongoing_projects = len([p for p in projects if p.get("status") in ["Order Received", "Material Planning", "WIP"]])

    # ── 2. DRAWINGS
    draw_filter = {}
    if project_list:
        draw_filter["project_number"] = ["in", project_list]

    drawings = frappe.db.get_all(
        "FT Add Drawing",
        filters=draw_filter,
        fields=["name", "drawing_number", "project_number", "unit_weight", "drawing_description"],
        order_by="modified desc"
    )
    total_drawings = len(drawings)
    total_drawing_weight = sum(d.get("unit_weight") or 0 for d in drawings)

    # ── 3. TRANSACTIONS
    txn_filter = {}
    if project_list:
        txn_filter["project_number"] = ["in", project_list]

    transactions = frappe.db.get_all(
        "FT Transaction",
        filters=txn_filter,
        fields=["name", "project_number", "stages", "date", "addition", "subtraction", "work_completed"],
        order_by="date desc"
    )
    total_transactions = len(transactions)

    # ── 4. STAGE-WISE SUMMARY
    stage_summary = {}
    for t in transactions:
        stage = t.get("stages") or "Unknown"
        if stage not in stage_summary:
            stage_summary[stage] = {
                "count": 0,
                "avg_pct": 0,
                "addition": 0,
                "subtraction": 0
            }
        stage_summary[stage]["count"] += 1
        stage_summary[stage]["avg_pct"] += t.get("work_completed") or 0
        stage_summary[stage]["addition"] += t.get("addition") or 0
        stage_summary[stage]["subtraction"] += t.get("subtraction") or 0
    
    for stage in stage_summary:
        if stage_summary[stage]["count"] > 0:
            stage_summary[stage]["avg_pct"] = round(stage_summary[stage]["avg_pct"] / stage_summary[stage]["count"], 1)

    # ── 5. PO DRAWINGS (Amount Tracking)
    po_filter = {}
    if project_list:
        po_filter["project_number"] = ["in", project_list]

    po_drawings = frappe.db.get_all(
        "FT Po Drawing",
        filters=po_filter,
        fields=["name", "total_weight", "required_qty"],
    )
    po_total_weight = sum(p.get("total_weight") or 0 for p in po_drawings)
    po_total_qty = sum(p.get("required_qty") or 0 for p in po_drawings)
    po_total_amount = 0

    # ── 6. RAW MATERIAL STOCK
    raw_materials = frappe.db.get_all(
        "FT Stock RM List",
        fields=["name", "section_type", "grade", "stock_rm_type"],
    )
    total_raw_materials = len(raw_materials)

    # ── 7. CUSTOMERS
    customers = frappe.db.get_all(
        "FT Customer",
        fields=["name", "customer_name"],
    )
    total_customers = len(customers)

    # ── 8. MONTHLY TRACKING
    monthly_targets = frappe.db.get_all(
        "FT Monthly Target",
        fields=["name", "year", "select_month"],
    )
    
    monthly_achievements = frappe.db.get_all(
        "FT Monthly Achievement",
        fields=["name", "year", "select_month"],
    )

    return {
        # Summary
        "total_projects": total_projects,
        "completed_projects": completed_projects,
        "ongoing_projects": ongoing_projects,
        "total_drawings": total_drawings,
        "total_weight": round(float(total_weight), 2),
        "total_drawing_weight": round(float(total_drawing_weight), 2),
        "total_transactions": total_transactions,
        "total_customers": total_customers,
        "total_raw_materials": total_raw_materials,
        "po_total_weight": round(float(po_total_weight), 2),
        "po_total_qty": int(po_total_qty),
        "po_total_amount": round(float(po_total_amount), 2),
        
        # Status breakdown
        "status_counts": status_counts,
        "stage_summary": stage_summary,
        
        # Top records
        "projects": [dict(p) for p in projects[:8]],
        "drawings": [dict(d) for d in drawings[:8]],
        "transactions": [dict(t) for t in transactions[:10]],
        "raw_materials": [dict(r) for r in raw_materials[:5]],
        
        # Counts
        "monthly_targets_count": len(monthly_targets),
        "monthly_achievements_count": len(monthly_achievements),
    }


@frappe.whitelist()
def get_project_tracking(project_name):
    """
    Get detailed tracking for specific project
    """
    
    # Project details
    project = frappe.get_doc("FT Project", project_name)
    
    # Project transactions
    transactions = frappe.db.get_all(
        "FT Transaction",
        filters={"project_number": project_name},
        fields=["name", "stages", "date", "work_completed", "addition", "subtraction"],
        order_by="date desc"
    )
    
    # Project drawings
    drawings = frappe.db.get_all(
        "FT Add Drawing",
        filters={"project_number": project_name},
        fields=["name", "drawing_number", "unit_weight", "drawing_description"],
    )
    
    # Project stages
    stages = frappe.db.get_all(
        "FT Project Stages",
        filters={"project_number": project_name},
        fields=["name", "date"],
    )
    
    # PO drawings for this project
    po_drawings = frappe.db.get_all(
        "FT Po Drawing",
        filters={"project_number": project_name},
        fields=["name", "total_weight", "required_qty"],
    )
    
    po_amount = 0
    drawing_weight = sum(d.get("unit_weight") or 0 for d in drawings)
    
    return {
        "project": project.as_dict(),
        "transactions": [dict(t) for t in transactions],
        "drawings": [dict(d) for d in drawings],
        "stages": [dict(s) for s in stages],
        "po_drawings": [dict(p) for p in po_drawings],
        "total_drawing_weight": round(float(drawing_weight), 2),
        "po_total_amount": round(float(po_amount), 2),
    }


@frappe.whitelist()
def get_active_projects_list():
    """
    Get list of active projects for filter
    """
    projects = frappe.db.get_all(
        "FT Project",
        filters={"is_active": 1},
        fields=["name", "customer_name", "status", "percentage_completed"],
        order_by="name asc"
    )
    return projects
