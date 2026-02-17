
import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 150},
        {"label": "Item", "fieldname": "item_name", "width": 350},
        {"label": "Total Entries", "fieldname": "item_count", "fieldtype": "Int", "width": 150},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
        {"label": "View", "fieldname": "view", "fieldtype": "HTML", "width": 120},
    ]

    # Conditions for main query
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        # conditions += " AND ad.name IN %(drawing_number)s"
        conditions += " AND ad.drawing_number IN %(drawing_number)s"

        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    # ---------------- MAIN DATA ----------------
    query = f"""
    SELECT
        p.name AS project_name,
        dp.item AS item_id,
        rm.computed_name AS item_name,
        COUNT(dp.name) AS item_count,
        SUM(COALESCE(dp.total_weight, 0)) AS total_weight
    FROM `tabFT Project` p
    LEFT JOIN `tabAdd Drawing` ad ON ad.project_number = p.name
    LEFT JOIN `tabDrawing Parts` dp ON dp.drawing_number = ad.name
    LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
    WHERE 1=1
        {conditions}
    GROUP BY p.name, dp.item, rm.computed_name
	HAVING 
		dp.item IS NOT NULL
		OR (
			dp.item IS NULL 
			AND NOT EXISTS (
				SELECT 1 
				FROM `tabAdd Drawing` ad2
				INNER JOIN `tabDrawing Parts` dp2 
					ON dp2.drawing_number = ad2.name
				WHERE ad2.project_number = p.name
			)
		)
    ORDER BY p.name, dp.item
    """

    data = frappe.db.sql(query, values, as_dict=True) or []

    # Add View Button and default values
    for row in data:
        row["item_count"] = row.get("item_count") or 0
        row["total_weight"] = row.get("total_weight") or 0
        row["item_name"] = row.get("item_name") or "-"
        row["view"] = f"""
        <button class="btn btn-xs btn-primary view-btn"
            data-project="{row.get('project_name')}"
            data-item="{row.get('item_id') or ''}">
            View
        </button>
        """

    # ---------------- SUMMARY ----------------
    total_projects = len({d["project_name"] for d in data if d.get("project_name")})

    # Total Drawings query – only join tabAdd Drawing, do NOT include dp.item
    drawing_query = f"""
    SELECT COUNT(DISTINCT ad.name)
    FROM `tabFT Project` p
    LEFT JOIN `tabAdd Drawing` ad ON ad.project_number = p.name
    WHERE 1=1
        {" AND p.name IN %(project_number)s" if filters.get("project_number") else ""}
        {" AND ad.name IN %(drawing_number)s" if filters.get("drawing_number") else ""}
        {" AND p.is_active = 1" if filters.get("is_active") else ""}
    """
    # Only pass project_number and drawing_number values
    drawing_values = {k: v for k, v in values.items() if k in ["project_number", "drawing_number"]}
    total_drawings = frappe.db.sql(drawing_query, drawing_values)[0][0] or 0

    total_drawing_parts = sum(d.get("item_count", 0) for d in data)
    total_weight_parts = sum(d.get("total_weight", 0) for d in data)

    # Total Weight as per Project
    project_conditions = ""
    project_values = {}
    if filters.get("project_number"):
        project_conditions += " AND name IN %(project_number)s"
        project_values["project_number"] = tuple(filters.get("project_number"))
    if filters.get("is_active"):
        project_conditions += " AND is_active = 1"

    project_total_weight = frappe.db.sql(
        f"SELECT SUM(total_weight) FROM `tabFT Project` WHERE 1=1 {project_conditions}",
        project_values,
    )
    project_total_weight = project_total_weight[0][0] if project_total_weight and project_total_weight[0][0] else 0

    # Total Weight as per Drawing
    drawing_weight_query = f"""
    SELECT SUM(COALESCE(ad.total_weight, 0))
    FROM `tabFT Project` p
    LEFT JOIN `tabAdd Drawing` ad ON ad.project_number = p.name
    WHERE 1=1
        {" AND p.name IN %(project_number)s" if filters.get("project_number") else ""}
        {" AND ad.name IN %(drawing_number)s" if filters.get("drawing_number") else ""}
        {" AND p.is_active = 1" if filters.get("is_active") else ""}
    """
    total_weight_drawing = frappe.db.sql(drawing_weight_query, drawing_values)[0][0] or 0

    report_summary = [
        {"label": "Total Projects", "value": total_projects, "datatype": "Int"},
        {"label": "Total No of Drawings", "value": total_drawings, "datatype": "Int"},
        {"label": "Total No of Drawing Parts", "value": total_drawing_parts, "datatype": "Int"},
        
        {"label": "Total Weight as per Project", "value": project_total_weight, "datatype": "Float"},
        {"label": "Total Weight as per Drawing", "value": total_weight_drawing, "datatype": "Float"},
        {"label": "Total Weight as per Drawing Parts", "value": total_weight_parts, "datatype": "Float"},
    ]

    return columns, data, None, None, report_summary


# @frappe.whitelist()
# def get_item_details(project, item):
    # rows = frappe.db.sql(
    #     """
    #     SELECT
    #         dp.drawing_number,
    #         dp.quantity,
    #         dp.lenght,
    #         dp.width,
    #         dp.single_weight,
    #         dp.total_weight
    #     FROM `tabDrawing Parts` dp
    #     WHERE dp.project_number = %s
    #     AND dp.item = %s
    #     ORDER BY dp.drawing_number
    #     """,
    #     (project, item),
    #     as_dict=True,
    # )

    # grand_total = sum(d.get("total_weight", 0) for d in rows)

    # rows.append({
    #     "drawing_number": "<b>Total</b>",
    #     "quantity": "",
    #     "lenght": "",
    #     "width": "",
    #     "single_weight": "",
    #     "total_weight": f"<b>{grand_total}</b>"
    # })

    # return rows

@frappe.whitelist()
def get_item_details(project, item):

    # item ka computed_name
    item_name = frappe.db.get_value(
        "FT Stock RM List",
        item,
        "computed_name"
    ) or item

    rows = frappe.db.sql(
        """
        SELECT
            ad.drawing_number AS drawing_number,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabDrawing Parts` dp
        LEFT JOIN `tabAdd Drawing` ad 
            ON ad.name = dp.drawing_number
        WHERE dp.project_number = %s
        AND dp.item = %s
        ORDER BY ad.drawing_number
        """,
        (project, item),
        as_dict=True,
    )

    grand_total = sum(d.get("total_weight", 0) for d in rows)

    rows.append({
        "drawing_number": "<b>Total</b>",
        "quantity": "",
        "lenght": "",
        "width": "",
        "single_weight": "",
        "total_weight": f"<b>{grand_total}</b>"
    })

    return {
        "item_name": item_name,
        "data": rows
    }



