
import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 200},
        {"label": "Item", "fieldname": "item_name", "width": 400},
        {"label": "Total Entries", "fieldname": "item_count", "fieldtype": "Int", "width": 200,"align": "center"},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 200,"align": "center"},
        {"label": "Details", "fieldname": "view", "fieldtype": "HTML", "width":210,"align": "center"},
    ]

    # Conditions for main query
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))
        
    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))
        
    if filters.get("stock_rm_type"):
        conditions += " AND rm.stock_rm_type IN %(stock_rm_type)s"
        values["stock_rm_type"] = tuple(filters.get("stock_rm_type"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    # ---------------- MAIN DATA ----------------
    query = f"""
    SELECT
        p.name AS project_name,
        
        dp.item AS item_id,
        rm.computed_name AS item_name,
        COALESCE(CAST(st.sort_key AS UNSIGNED), 9999) AS sort_key,
        COUNT(dp.name) AS item_count,
        SUM(COALESCE(dp.total_weight, 0)) AS total_weight
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
    LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
    LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type

    WHERE 1=1
        {conditions}
    GROUP BY p.name, dp.item, rm.computed_name,st.sort_key
    
	HAVING 
		dp.item IS NOT NULL
		OR (
			dp.item IS NULL 
			AND NOT EXISTS (
				SELECT 1 
				FROM `tabFT Add Drawing` ad2
				INNER JOIN `tabFT Drawing Parts` dp2 
					ON dp2.drawing_number = ad2.name
				WHERE ad2.project_number = p.name
			)
		)
    ORDER BY p.name, 
        sort_key ASC
    """

    data = frappe.db.sql(query, values, as_dict=True) or []

    # Add Details Button and default values
    for row in data:
        row["item_count"] = row.get("item_count") or 0
        row["total_weight"] = row.get("total_weight") or 0
        row["item_name"] = row.get("item_name") or "-"
        row["view"] = f"""
                
        <div class="d-grid gap-2 col-6 mx-auto">
            <button class="btn btn-xs btn-info view-btn"
                data-project="{row.get('project_name')}"
                data-item="{row.get('item_id') or ''}">
                Details
            </button>
        </div>
       
        """

    # ---------------- SUMMARY ----------------
    total_projects = len({d["project_name"] for d in data if d.get("project_name")})

    # Total Drawings query – only join tabFT Add Drawing, do NOT include dp.item
    drawing_query = f"""
    SELECT COUNT(DISTINCT ad.name)
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    WHERE 1=1
        {" AND p.name IN %(project_number)s" if filters.get("project_number") else ""}
        {" AND ad.drawing_number IN %(drawing_number)s" if filters.get("drawing_number") else ""}
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
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    WHERE 1=1
        {" AND p.name IN %(project_number)s" if filters.get("project_number") else ""}
        {" AND ad.drawing_number IN %(drawing_number)s" if filters.get("drawing_number") else ""}
        {" AND p.is_active = 1" if filters.get("is_active") else ""}
    """
    total_weight_drawing = frappe.db.sql(drawing_weight_query, drawing_values)[0][0] or 0

    # isse card me kg ki value .000 me ari hai 
    formatted_project_total_weight = "{:,.3f}".format(project_total_weight)
    formatted_total_weight_drawing = "{:,.3f}".format(total_weight_drawing)
    formatted_total_weight_parts = "{:,.3f}".format(total_weight_parts)
    
    report_summary = [
        {
            "label": "",
            "value": f"""
            <div class="summary-container">
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total Projects</p>
                        <span>{total_projects}</span>                  
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Project(Kg)</p>
                        <span>{formatted_project_total_weight}</span>                   
                    </div>
                </div>
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Drawings</p>
                        <span>{total_drawings}</span>                    
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Drawing(Kg)</p>
                        <span>{formatted_total_weight_drawing}</span>                   
                    </div>
                </div>
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Drawing Parts</p>
                        <span>{total_drawing_parts}</span>                    
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Drawing Parts(Kg)</p>
                        <span>{formatted_total_weight_parts}</span>                    
                    </div>
                </div>
            </div>
            """,
            "datatype": "HTML",
        }
    ]

    return columns, data, None, None, report_summary

@frappe.whitelist()
def get_item_details(project, item, drawing_numbers=None):

    conditions = " WHERE p.name = %s AND dp.item = %s "
    values = [project, item]

    if drawing_numbers:
        drawing_numbers = frappe.parse_json(drawing_numbers)
        if drawing_numbers:
            conditions += " AND ad.drawing_number IN %s "
            values.append(tuple(drawing_numbers))

    rows = frappe.db.sql(f"""
        SELECT
            ad.drawing_number AS drawing_number,
            
            dp.position_no AS position_no,
            
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        {conditions}
        ORDER BY ad.drawing_number
    """, tuple(values), as_dict=True)

    grand_total = sum(d.get("total_weight", 0) for d in rows)

    rows.append({
        "drawing_number": "<b>Total</b>",        
        "position_no": "",        
        "quantity": "",
        "lenght": "",
        "width": "",
        "single_weight": "",
        "total_weight": grand_total
    })

    item_name = frappe.db.get_value(
        "FT Stock RM List", item, "computed_name"
    ) or item

    return {
        "item_name": item_name,
        "data": rows
    }


# ---------------- EXCEL EXPORT ALL DETAILS ----------------

@frappe.whitelist()
def get_all_details_for_export(filters):

    filters = frappe.parse_json(filters)
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item_name,
            ad.drawing_number,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
        WHERE 1=1 {conditions}
        ORDER BY p.name, ad.drawing_number
    """, values, as_dict=True)

    return data