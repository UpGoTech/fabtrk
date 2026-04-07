import frappe

@frappe.whitelist()
def get_dashboard_data():
    
    # Step 1: Saare FT Project Stages fetch karo (yeh parent doc hai)
    project_stages_list = frappe.get_all(
        "FT Project Stages",
        fields=["name", "project_number", "date"],
        order_by="project_number asc"
    )

    result = []

    for ps in project_stages_list:
        project_id = ps.get("project_number")
        if not project_id:
            continue

        # Step 2: Project details FT Project se
        project = frappe.get_value(
            "FT Project",
            project_id,
            ["project_name", "status", "customer_name",
             "percentage_completed", "excepted_start_date", "excepted_end_date"],
            as_dict=True
        ) or {}

        # Step 3: Is project ke stages (child table)
        stage_rows = frappe.get_all(
            "FT Project Stages Child",
            filters={"parent": ps["name"]},
            fields=["name", "stages_key", "stages"],
            order_by="stages_key asc"
        )

        stage_list = []
        total_target = 0
        total_completed = 0

        for row in stage_rows:
            stage_child_name = row.get("name")
            stage_link       = row.get("stages")

            # Stage master se naam
            stage_display_name = stage_link or "—"
            if stage_link:
                master_name = frappe.get_value(
                    "FT Stages Master", stage_link, "stages_master"
                )
                stage_display_name = master_name or stage_link

            # Step 4: FT Transaction se is stage ka data
            transactions = frappe.get_all(
                "FT Transaction",
                filters={
                    "project_number": ps["name"],
                    "stages": stage_child_name
                },
                fields=["addition", "subtraction", "work_completed", "date"],
                order_by="date asc"
            )

            # Total calculate karo
            total_addition    = sum(t.get("addition") or 0 for t in transactions)
            total_subtraction = sum(t.get("subtraction") or 0 for t in transactions)
            work_completed    = sum(t.get("work_completed") or 0 for t in transactions)

            # Target = total addition - total subtraction
            stage_target    = total_addition - total_subtraction
            stage_completed = work_completed
            stage_pct = round((stage_completed / stage_target) * 100) \
                        if stage_target > 0 else 0
            stage_pct = min(stage_pct, 100)

            total_target    += stage_target
            total_completed += stage_completed

            stage_list.append({
                "key":        row.get("stages_key") or 0,
                "name":       stage_display_name,
                "id":         stage_child_name,
                "target":     stage_target,
                "completed":  stage_completed,
                "remaining":  max(stage_target - stage_completed, 0),
                "pct":        stage_pct,
                "tx_count":   len(transactions)
            })

        # Overall project completion
        overall_pct = round((total_completed / total_target) * 100) \
                      if total_target > 0 else 0
        overall_pct = min(overall_pct, 100)

        # Status decide karo
        if overall_pct == 100:
            computed_status = "Completed"
        elif overall_pct >= 50:
            computed_status = "On Track"
        elif overall_pct > 0:
            computed_status = "Delayed"
        else:
            computed_status = "Not Started"

        result.append({
            "id":            project_id,
            "ps_name":       ps["name"],
            "name":          project.get("project_name") or project_id,
            "status":        project.get("status") or computed_status,
            "customer":      project.get("customer_name") or "—",
            "overall_pct":   overall_pct,
            "total_target":  total_target,
            "total_completed": total_completed,
            "start_date":    str(project.get("excepted_start_date") or "—"),
            "end_date":      str(project.get("excepted_end_date") or "—"),
            "stages":        stage_list,
            "total_stages":  len(stage_list)
        })

    return result



# import frappe

# @frappe.whitelist()
# def get_dashboard_data():

    # ── Top Tracking Counts ──────────────────────────────────────────────────
    total_projects  = frappe.db.count("FT Project")
    total_drawings  = frappe.db.count("FT Add Drawing")
    total_po        = frappe.db.count("FT Po Drawing")
    total_items     = frappe.db.count("FT Drawing Parts")

    active_projects = frappe.db.count("FT Project", filters={"is_active": 1})

    # ── Project Stages Loop ──────────────────────────────────────────────────
    project_stages_list = frappe.get_all(
        "FT Project Stages",
        fields=["name", "project_number", "date"],
        order_by="project_number asc"
    )

    result = []

    for ps in project_stages_list:
        project_id = ps.get("project_number")
        if not project_id:
            continue

        project = frappe.get_value(
            "FT Project",
            project_id,
            ["project_name", "status", "customer_name",
             "percentage_completed", "excepted_start_date", "excepted_end_date"],
            as_dict=True
        ) or {}

        stage_rows = frappe.get_all(
            "FT Project Stages Child",
            filters={"parent": ps["name"]},
            fields=["name", "stages_key", "stages"],
            order_by="stages_key asc"
        )

        stage_list = []
        total_target    = 0
        total_completed = 0

        for row in stage_rows:
            stage_child_name   = row.get("name")
            stage_link         = row.get("stages")
            stage_display_name = stage_link or "—"

            if stage_link:
                master_name = frappe.get_value(
                    "FT Stages Master", stage_link, "stages_master"
                )
                stage_display_name = master_name or stage_link

            transactions = frappe.get_all(
                "FT Transaction",
                filters={
                    "project_number": ps["name"],
                    "stages": stage_child_name
                },
                fields=["addition", "subtraction", "work_completed", "date"],
                order_by="date asc"
            )

            total_addition    = sum(t.get("addition")       or 0 for t in transactions)
            total_subtraction = sum(t.get("subtraction")    or 0 for t in transactions)
            work_completed    = sum(t.get("work_completed") or 0 for t in transactions)

            stage_target    = total_addition - total_subtraction
            stage_completed = work_completed
            stage_pct = round((stage_completed / stage_target) * 100) \
                        if stage_target > 0 else 0
            stage_pct = min(stage_pct, 100)

            total_target    += stage_target
            total_completed += stage_completed

            stage_list.append({
                "key":       row.get("stages_key") or 0,
                "name":      stage_display_name,
                "id":        stage_child_name,
                "target":    stage_target,
                "completed": stage_completed,
                "remaining": max(stage_target - stage_completed, 0),
                "pct":       stage_pct,
                "tx_count":  len(transactions)
            })

        overall_pct = round((total_completed / total_target) * 100) \
                      if total_target > 0 else 0
        overall_pct = min(overall_pct, 100)

        if overall_pct == 100:
            computed_status = "Completed"
        elif overall_pct >= 50:
            computed_status = "On Track"
        elif overall_pct > 0:
            computed_status = "Delayed"
        else:
            computed_status = "Not Started"

        result.append({
            "id":              project_id,
            "ps_name":         ps["name"],
            "name":            project.get("project_name") or project_id,
            "status":          project.get("status") or computed_status,
            "customer":        project.get("customer_name") or "—",
            "overall_pct":     overall_pct,
            "total_target":    total_target,
            "total_completed": total_completed,
            "start_date":      str(project.get("excepted_start_date") or "—"),
            "end_date":        str(project.get("excepted_end_date")   or "—"),
            "stages":          stage_list,
            "total_stages":    len(stage_list)
        })

    return {
        "tracking": {
            "total_projects":  total_projects,
            "active_projects": active_projects,
            "total_drawings":  total_drawings,
            "total_po":        total_po,
            "total_items":     total_items,
        },
        "projects": result
    }