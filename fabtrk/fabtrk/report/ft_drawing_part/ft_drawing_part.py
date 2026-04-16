import frappe
from frappe.utils import get_url
 
def execute(filters=None):
    filters = filters or {}
 
    columns = [
        {"label": "Item",            "fieldname": "item_name",       "width": 400},
        {"label": "Total Entries",   "fieldname": "item_count",      "fieldtype": "Int",   "width": 110, "align": "center"},
        {"label": "Total Projects",  "fieldname": "project_count",   "fieldtype": "Int",   "width": 130, "align": "center"},
        {"label": "PO Required Qty", "fieldname": "po_required_qty", "fieldtype": "Int",   "width": 150, "align": "center"},
        {"label": "PO Total Weight", "fieldname": "po_total_weight", "fieldtype": "Float", "width": 150, "align": "center"},
        {"label": "Total Surface A","fieldname": "total_surface_area","fieldtype": "Data", "width": 150, },
        {"label": "Details",         "fieldname": "view",            "fieldtype": "HTML",  "width": 100, "align": "center"},
    ]
 
    # ---------------- filter CONDITIONS  ----------------
    conditions = ""
    values = {}
 
    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))
 
    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))
 
    if filters.get("po_no"):
        conditions += " AND dp.po_no IN %(po_no)s"
        values["po_no"] = tuple(int(p) for p in filters.get("po_no"))
 
    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))
 
    if filters.get("stock_rm_type"):
        conditions += " AND rm.stock_rm_type IN %(stock_rm_type)s"
        values["stock_rm_type"] = tuple(filters.get("stock_rm_type"))
 
    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"
 
 
 
    # # ---------------- MAIN QUERY ----------------
    query = f"""
    SELECT
        dp.item AS item,
        rm.computed_name AS item_name,
        COALESCE(CAST(st.sort_key AS UNSIGNED), 9999) AS sort_key,
        CAST(REGEXP_SUBSTR(rm.computed_name, '[0-9]+') AS UNSIGNED) AS item_sort,
        COUNT(dp.name) AS item_count,
        COUNT(DISTINCT p.name) AS project_count,
        SUM(COALESCE(dp.quantity, 0)) AS quantity,
        SUM(COALESCE(dp.lenght, 0)) AS lenght,
        SUM(COALESCE(dp.width, 0)) AS width,
        SUM(COALESCE(dp.total_weight, 0)) AS total_weight,
        SUM(COALESCE(dp.quantity, 0) * COALESCE(pod.required_qty, 0)) AS po_required_qty_raw,
        SUM(COALESCE(dp.total_weight, 0) * COALESCE(pod.required_qty, 0)) AS po_total_weight_raw,
        SUM(COALESCE(dp.single_unit_surface_area, 0)) AS single_unit_surface_area_raw,
        SUM(COALESCE(dp.total_surface_area, 0)) AS total_surface_area_raw
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
    LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
    LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type
    LEFT JOIN `tabFT Po Drawing` pod
        ON pod.project_number = p.name
        AND pod.drawing_number = ad.name
    WHERE 1=1
        {conditions}
    GROUP BY dp.item, rm.computed_name, st.sort_key
    HAVING dp.item IS NOT NULL
    ORDER BY sort_key ASC, item_sort ASC
    """
 
    data = frappe.db.sql(query, values, as_dict=True) or []
 
    for i, row in enumerate(data, start=1):
        row["item_count"]   = row.get("item_count") or 0
        row["project_count"] = row.get("project_count") or 0
        row["quantity"]     = row.get("quantity") or 0
        row["lenght"]       = row.get("lenght") or 0
        row["width"]        = row.get("width") or 0
        row["total_weight"]  = row.get("total_weight") or 0
        row["item_name"]    = row.get("item_name") or "-"
        row["po_required_qty"] = int(float(row.get("po_required_qty_raw") or 0))
        row["po_total_weight"] = round(float(row.get("po_total_weight_raw") or 0), 3)
        row["single_unit_surface_area"] = round(float(row.get("single_unit_surface_area_raw") or 0), 3)
        row["total_surface_area"] = round(float(row.get("total_surface_area_raw") or 0), 3)
 
        row["view"] = f"""
            <div class="d-grid gap-2 col-6 mx-auto">
                <button class="btn btn-xs btn-info view-btn"
                    data-item="{row.get('item') or ''}">
                    Details
                </button>
            </div>
        """
 
 
    # ---------------- SUMMARY ----------------
    project_count_query = """
        SELECT COUNT(DISTINCT p.name)
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
        WHERE 1=1
    """
    project_count_values = {}
 
    if filters.get("project_number"):
        project_count_query += " AND p.name IN %(project_number)s"
        project_count_values["project_number"] = tuple(filters.get("project_number"))
 
    if filters.get("drawing_number"):
        project_count_query += " AND ad.name IN %(drawing_number)s"
        project_count_values["drawing_number"] = tuple(filters.get("drawing_number"))
 
    if filters.get("is_active"):
        project_count_query += " AND p.is_active = 1"
 
    total_projects = frappe.db.sql(project_count_query, project_count_values)[0][0] or 0
 
    drawing_query = f"""
    SELECT COUNT(DISTINCT ad.name)
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    WHERE 1=1
        {" AND p.name IN %(project_number)s" if filters.get("project_number") else ""}
        {" AND ad.name IN %(drawing_number)s" if filters.get("drawing_number") else ""}
        {" AND p.is_active = 1" if filters.get("is_active") else ""}
    """
    drawing_values = {k: v for k, v in values.items() if k in ["project_number", "drawing_number"]}
    total_drawings = frappe.db.sql(drawing_query, drawing_values)[0][0] or 0
 
    total_drawing_parts = sum(d.get("item_count", 0) for d in data)
    total_weight_parts  = sum(d.get("total_weight", 0) for d in data)
 
    project_conditions = ""
    project_values = {}
    if filters.get("project_number"):
        project_conditions += " AND name IN %(project_number)s"
        project_values["project_number"] = tuple(filters.get("project_number"))
    if filters.get("is_active"):
        project_conditions += " AND is_active = 1"
 
    project_total_weight = frappe.db.sql(
        f"SELECT SUM(total_weight) FROM `tabFT Project` WHERE 1=1 {project_conditions}",
        project_values
    )
    project_total_weight = project_total_weight[0][0] if project_total_weight and project_total_weight[0][0] else 0
 
    po_conditions = ""
    po_values = {}
 
    if filters.get("project_number"):
        po_conditions += " AND pod.project_number IN %(project_number)s"
        po_values["project_number"] = tuple(filters.get("project_number"))
 
    if filters.get("drawing_number"):
        po_conditions += " AND pod.drawing_number IN %(drawing_number)s"
        po_values["drawing_number"] = tuple(filters.get("drawing_number"))
 
    po_summary = frappe.db.sql(f"""
        SELECT
            COUNT(pod.name) as total_line_items,
            SUM(COALESCE(pod.required_qty, 0)) as total_required_qty,
            SUM(COALESCE(pod.total_weight, 0)) as total_weight
        FROM `tabFT Po Drawing` pod
        WHERE 1=1 {po_conditions}
    """, po_values, as_dict=True)
 
    total_po_drawings     = po_summary[0]["total_line_items"] or 0
    total_required_qty_po = po_summary[0]["total_required_qty"] or 0
    total_weight_po_items = po_summary[0]["total_weight"] or 0
 
    po_count_conditions = "WHERE dp.po_no IS NOT NULL AND dp.po_no != 0"
    po_count_values = {}
 
    if filters.get("project_number"):
        po_count_conditions += " AND p.name IN %(project_number)s"
        po_count_values["project_number"] = tuple(filters.get("project_number"))
 
    if filters.get("drawing_number"):
        po_count_conditions += " AND ad.name IN %(drawing_number)s"
        po_count_values["drawing_number"] = tuple(filters.get("drawing_number"))
 
    if filters.get("po_no"):
        po_count_conditions += " AND dp.po_no IN %(po_no)s"
        po_count_values["po_no"] = tuple(int(p) for p in filters.get("po_no"))
 
    if filters.get("is_active"):
        po_count_conditions += " AND p.is_active = 1"
 
    po_no_summary = frappe.db.sql(f"""
        SELECT
            COUNT(DISTINCT dp.po_no) AS total_po_count,
            SUM(COALESCE(dp.total_weight, 0)) AS total_po_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        {po_count_conditions}
    """, po_count_values, as_dict=True)
 
    total_po_count  = po_no_summary[0]["total_po_count"]  or 0
    total_po_weight = po_no_summary[0]["total_po_weight"] or 0
 
    rounded_total_po_weight = round(total_po_weight, 3)
    rounded_required_qty    = round(total_required_qty_po, 3)
    # total_weight_po_items   = rounded_total_po_weight * rounded_required_qty
    total_weight_po_items = grand_po_total_weight = sum(d.get("po_total_weight", 0) for d in data)
 
    drawing_balance_for_customer = (project_total_weight or 0) - total_weight_po_items
 
    grand_po_required_qty = sum(d.get("po_required_qty", 0) for d in data)
    grand_po_total_weight = sum(d.get("po_total_weight", 0.0) for d in data)
 
    formatted_total_po_weight              = "{:,.3f}".format(total_po_weight)
    formatted_project_total_weight         = "{:,.3f}".format(project_total_weight)
    formatted_total_weight_po_items        = "{:,.3f}".format(round(total_weight_po_items, 3))
    formatted_total_weight_parts           = "{:,.3f}".format(total_weight_parts)
    formatted_drawing_balance_for_customer = "{:,.3f}".format(drawing_balance_for_customer)
    formatted_grand_po_total_weight        = "{:,.3f}".format(grand_po_total_weight)
 
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
                        <p>Project Total No of Line Items</p>
                        <span>{total_po_drawings}</span>
                    </div>
                    <div class="section-content-count">
                        <p>Total Required Qty<br>As per Po Drawing</p>
                        <span>{int(total_required_qty_po)}</span>
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight of Line Items<br>Assign to Project(Kg)</p>
                        <span>{formatted_total_weight_po_items}</span>
                    </div>
                </div>
 
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total PO Numbers</p>
                        <span>{total_po_count}</span>
                    </div>
                    <div class="section-content-count">
                        <p>Total No of Drawing Parts</p>
                        <span>{total_drawing_parts}</span>
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per PO (Kg)</p>
                        <span>{formatted_total_po_weight}</span>
                    </div>
                </div>
 
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Total No of Drawings</p>
                        <span>{total_drawings}</span>
                    </div>
                </div>
 
                <div class="summary-section">
                    <div class="section-content-count">
                        <p>Drawing Balance for Customer(Kg)</p>
                        <span>{formatted_drawing_balance_for_customer}</span>
                    </div>
                </div>
            </div>
            """,
            "datatype": "HTML",
        }
    ]
 
    # # GRAND TOTAL ROW
    # if data:
    #     grand_total_entries    = sum(float(d.get("item_count") or 0) for d in data)
    #     grand_po_req_qty_total = sum(float(d.get("po_required_qty") or 0) for d in data)
    #     grand_po_wt_total      = sum(float(d.get("po_total_weight") or 0) for d in data)
 
    #     data.append({
    #         "sr_no":           None,
    #         "item_name":       "TOTAL",
    #         "item_count":      grand_total_entries,
    #         "po_required_qty": grand_po_req_qty_total,
    #         "po_total_weight": grand_po_wt_total,
    #         "view":            ""
    #     })
 
    return columns, data, None, None, report_summary
  
# ---------------- PO Number dropdown ──────────────────────────────────────────────────────
@frappe.whitelist()
def get_po_numbers(txt="", drawings=None, projects=None, is_active=0):
    import json
 
    if isinstance(drawings, str):
        try: drawings = json.loads(drawings)
        except: drawings = []
    if isinstance(projects, str):
        try: projects = json.loads(projects)
        except: projects = []
 
    drawings  = drawings or []
    projects  = projects or []
    is_active = int(is_active or 0)
 
    conditions = "WHERE dp.po_no IS NOT NULL AND dp.po_no != 0"
    values = {}
 
    if drawings:
        conditions += " AND dp.drawing_number IN %(drawings)s"
        values["drawings"] = tuple(drawings)
    elif projects:
        conditions += """
            AND dp.drawing_number IN (
                SELECT name FROM `tabFT Add Drawing`
                WHERE project_number IN %(projects)s
            )
        """
        values["projects"] = tuple(projects)
    elif is_active:
        conditions += """
            AND dp.drawing_number IN (
                SELECT ad.name FROM `tabFT Add Drawing` ad
                INNER JOIN `tabFT Project` p ON p.name = ad.project_number
                WHERE p.is_active = 1
            )
        """
 
    if txt:
        conditions += " AND CAST(dp.po_no AS CHAR) LIKE %(txt)s"
        values["txt"] = f"%{txt}%"
 
    rows = frappe.db.sql(f"""
        SELECT DISTINCT dp.po_no
        FROM `tabFT Drawing Parts` dp
        {conditions}
        ORDER BY dp.po_no ASC
    """, values, as_list=True)
 
    return [str(r[0]) for r in rows if r[0]]
 
 
# ----------------- Details button ──────────────────────────────────────────────────────────
@frappe.whitelist()
def get_item_details(project, item, drawing_numbers=None, project_numbers=None,po_numbers=None):
    from collections import defaultdict
    import json

    # ✅ Base condition — sirf item filter
    conditions = " WHERE dp.item = %s "
    values = [item]

    # ✅ project_numbers — report filter se aaye multiple projects
    if project_numbers:
        if isinstance(project_numbers, str):
            try:
                project_numbers = json.loads(project_numbers)
            except:
                project_numbers = []
        if project_numbers:
            conditions += f" AND p.name IN %s "
            values.append(tuple(project_numbers))
    elif project:
        # single project (backward compat)
        conditions += " AND p.name = %s "
        values.append(project)
        
        
    # ✅ drawing_numbers filter
    if drawing_numbers:
        drawing_numbers = frappe.parse_json(drawing_numbers)
        if drawing_numbers:
            conditions += " AND ad.name IN %s "
            values.append(tuple(drawing_numbers))
 
    # ✅ po_numbers filter
    if po_numbers:
        if isinstance(po_numbers, str):
            try:
                parsed_po = json.loads(po_numbers)
            except:
                parsed_po = []
        else:
            parsed_po = list(po_numbers)
        if parsed_po:
            conditions += " AND dp.po_no IN %s "
            values.append(tuple(int(p) for p in parsed_po))
            
            
    rows = frappe.db.sql(f"""
        SELECT
            p.name AS project_number,
            dp.po_no AS po_no,
            pod.po_serial_no AS po_serial_no,
            ad.drawing_number AS drawing_number,
            dp.position_no AS position_no,
            dp.part_no AS part_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight,
            dp.single_unit_surface_area,
            dp.total_surface_area,
            COALESCE(pod.required_qty, 0) AS required_qty
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        {conditions}
        ORDER BY
            COALESCE(CAST(pod.po_serial_no AS UNSIGNED), 0) ASC,
            ad.drawing_number ASC
    """, tuple(values), as_dict=True)
 
    grouped = defaultdict(lambda: {
        "project_number": "",
        "po_no": "",
        "po_serial_no": "",
        "drawing_number": "",
        "position_no": "",
        "part_no": "",
        "quantity": 0,
        "lenght": 0,
        "width": 0,
        "single_weight": 0,
        "total_weight": 0,
        "single_unit_surface_area": 0.0,
        "total_surface_area": 0.0,
        "required_qty": 0,
        "po_existing_qty": 0,
        "po_required_qty": 0,
        "po_item_total_weight": 0.0,
        "entry_count": 0
    })
 
    for d in rows:
        key = (
            d.get("project_number"),
            d.get("po_no"),
            d.get("po_serial_no"),
            d.get("drawing_number"),
            d.get("position_no"),
            d.get("part_no"),
            d.get("quantity"),
            d.get("lenght"),
            d.get("width"),
            d.get("single_weight"),
            d.get("total_weight"),
        )
 
        grouped[key]["project_number"] = d.get("project_number")
        grouped[key]["po_no"]          = d.get("po_no") or ""
        grouped[key]["po_serial_no"]   = d.get("po_serial_no")
        grouped[key]["drawing_number"] = d.get("drawing_number")
        grouped[key]["position_no"]    = d.get("position_no")
        grouped[key]["part_no"]        = d.get("part_no")
        grouped[key]["quantity"]       = d.get("quantity")
        grouped[key]["lenght"]         = d.get("lenght")
        grouped[key]["width"]          = d.get("width")
        grouped[key]["single_weight"]  = d.get("single_weight")
        grouped[key]["total_weight"]   = d.get("total_weight")
        grouped[key]["single_unit_surface_area"] = round(float(d.get("single_unit_surface_area") or 0), 3)
        grouped[key]["total_surface_area"] = round(float(d.get("total_surface_area") or 0), 3)
 
        # ✅ per-row required_qty aur calculation — as-it-is (image mein sahi tha)
        req_qty = int(d.get("required_qty") or 0)
        qty     = int(d.get("quantity") or 0)
        tw      = float(d.get("total_weight") or 0.0)
        
        grouped[key]["required_qty"]         = req_qty
        grouped[key]["po_existing_qty"]      = req_qty   
        grouped[key]["po_required_qty"]      = qty * req_qty
        grouped[key]["po_item_total_weight"] = round(tw * req_qty, 3)
        grouped[key]["entry_count"] += 1
 
    rows = list(grouped.values())
 
    grand_total_weight              = 0
    grand_total_qty                 = 0
    grand_total_length              = 0
    grand_total_width               = 0
    grand_po_existing_qty = 0 
    grand_po_required_qty           = 0
    grand_po_item_total_weight      = 0.0
    grand_single_unit_surface_area = 0.0
    grand_total_surface_area = 0.0
 
    serial_no = 1
    for d in rows:
        d["serial_no"] = serial_no
        serial_no += 1
        grand_total_weight         += d.get("total_weight") or 0
        grand_total_qty            += d.get("quantity") or 0
        grand_total_length         += d.get("lenght") or 0
        grand_total_width          += d.get("width") or 0
        grand_po_existing_qty += d.get("po_existing_qty") or 0
        grand_po_required_qty           += d.get("po_required_qty") or 0
        grand_po_item_total_weight      += d.get("po_item_total_weight") or 0.0
        grand_single_unit_surface_area += float(d.get("single_unit_surface_area") or 0.0)
        grand_total_surface_area += float(d.get("total_surface_area") or 0.0)
 
    rows.append({
        "serial_no":                    "",
        "project_number":               "<b>Total</b>",
        "po_no":                        "",
        "po_serial_no":                 "",
        "drawing_number":               "",
        "position_no":                  "",
        "part_no":                      "",
        "entry_count":                  "",
        "quantity":                     grand_total_qty,
        "lenght":                       grand_total_length,
        "width":                        grand_total_width,
        "single_weight":                "",
        "total_weight":                 grand_total_weight,
        "single_unit_surface_area":     round(grand_single_unit_surface_area, 3),
        "total_surface_area":           round(grand_total_surface_area, 3),
        "required_qty":                 "",
        "po_existing_qty": grand_po_existing_qty,  # ← po_required_qty se pehle
        "po_required_qty":              grand_po_required_qty,
        "po_item_total_weight":         round(grand_po_item_total_weight, 3),
        "_is_total_row":                True,
    })
 
    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item
    return {"item_name": item_name, "data": rows}


# 11 ---------------- EXCEL EXPORT — Summary ----------------
@frappe.whitelist()
def download_item_excel(filters, columns=None):
    import frappe
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from io import BytesIO

    filters = frappe.parse_json(filters)
    columns = frappe.parse_json(columns) if columns else []

    # ── Agar columns empty hain to default use karo ──
    if not columns:
        columns = [
            {"fieldname": "item_name",       "label": "Item",            "fieldtype": "Data"},
            {"fieldname": "item_count",       "label": "Total Entries",   "fieldtype": "Int"},
            {"fieldname": "project_count",    "label": "Total Projects",  "fieldtype": "Int"},
            {"fieldname": "po_required_qty",  "label": "PO Required Qty", "fieldtype": "Int"},
            {"fieldname": "po_total_weight",  "label": "PO Total Weight", "fieldtype": "Float"},
        ]

    conditions = ""
    values = {}

    projects = filters.get("project_number") or []
    if projects:
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(projects)

    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("po_no"):
        conditions += " AND dp.po_no IN %(po_no)s"
        values["po_no"] = tuple(int(p) for p in filters.get("po_no"))

    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    if filters.get("stock_rm_type"):
        conditions += " AND rm.stock_rm_type IN %(stock_rm_type)s"
        values["stock_rm_type"] = tuple(filters.get("stock_rm_type"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    # ── Main data query ──
    data = frappe.db.sql(f"""
        SELECT
            dp.item AS item,
            rm.computed_name AS item_name,
            COUNT(dp.name) AS item_count,
            COUNT(DISTINCT p.name) AS project_count,
            SUM(COALESCE(dp.quantity, 0)) AS quantity,
            SUM(COALESCE(dp.lenght, 0)) AS lenght,
            SUM(COALESCE(dp.width, 0)) AS width,
            SUM(COALESCE(dp.total_weight, 0)) AS total_weight,
            SUM(COALESCE(dp.quantity, 0) * COALESCE(pod.required_qty, 0)) AS po_required_qty_raw,
            SUM(COALESCE(dp.total_weight, 0) * COALESCE(pod.required_qty, 0)) AS po_total_weight_raw
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
        LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
        LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        WHERE 1=1 {conditions}
        GROUP BY dp.item, rm.computed_name
        HAVING dp.item IS NOT NULL
        ORDER BY rm.computed_name ASC
    """, values, as_dict=True) or []

    # ── Field value normalize karo ──
    for row in data:
        row["item_count"]      = int(row.get("item_count") or 0)
        row["project_count"]   = int(row.get("project_count") or 0)
        row["quantity"]        = int(row.get("quantity") or 0)
        row["lenght"]          = round(float(row.get("lenght") or 0), 3)
        row["width"]           = round(float(row.get("width") or 0), 3)
        row["total_weight"]    = round(float(row.get("total_weight") or 0), 3)
        row["item_name"]       = row.get("item_name") or "-"
        row["po_required_qty"] = int(float(row.get("po_required_qty_raw") or 0))
        row["po_total_weight"] = round(float(row.get("po_total_weight_raw") or 0), 3)

    # ── Excel banana ──
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary Report"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    total_font  = Font(bold=True, color="FFFFFF")
    total_fill  = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin")
    )
    center = Alignment(horizontal="center", vertical="center")
    left   = Alignment(horizontal="left",   vertical="center")

    TOTAL_COLS = len(columns) + 1  # +1 for Sr No

    # ── Row 1: Title ──
    heading_text = (
        "Item Wise Summary: " + ", ".join(projects)
        if projects else "All Item Wise Summary"
    )
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=TOTAL_COLS)
    heading_cell = ws.cell(row=1, column=1, value=heading_text)
    heading_cell.font      = Font(bold=True, size=14, color="FFFFFF")
    heading_cell.alignment = center
    heading_cell.fill      = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    ws.row_dimensions[1].height = 28

    # ── Row 3: Headers ──
    ws.cell(row=3, column=1, value="Sr No").font = header_font
    ws.cell(row=3, column=1).fill      = header_fill
    ws.cell(row=3, column=1).border    = border
    ws.cell(row=3, column=1).alignment = center

    for col_idx, col in enumerate(columns, 2):
        cell = ws.cell(row=3, column=col_idx, value=col.get("label", ""))
        cell.font      = header_font
        cell.fill      = header_fill
        cell.border    = border
        cell.alignment = center

    # ── Float fields detect karo ──
    float_fieldnames = set()
    for col in columns:
        ft = (col.get("fieldtype") or "").lower()
        if ft in ["float", "currency", "percent"]:
            float_fieldnames.add(col.get("fieldname"))

    # ── Data rows ──
    row_no = 4
    sr = 1
    grand_totals = {col["fieldname"]: 0 for col in columns}

    for d in data:
        ws.cell(row=row_no, column=1, value=sr).border    = border
        ws.cell(row=row_no, column=1).alignment = center

        for col_idx, col in enumerate(columns, 2):
            fn  = col.get("fieldname")
            val = d.get(fn, "")
            cell = ws.cell(row=row_no, column=col_idx, value=val)
            cell.border    = border
            cell.alignment = left if fn == "item_name" else center
            if fn in float_fieldnames:
                cell.number_format = '#,##0.000'

            # Grand total accumulate karo (numeric fields ke liye)
            if isinstance(val, (int, float)):
                grand_totals[fn] = grand_totals.get(fn, 0) + val

        row_no += 1
        sr     += 1

    # ── Total row ──
    ws.cell(row=row_no, column=1, value="Total").font      = total_font
    ws.cell(row=row_no, column=1).fill      = total_fill
    ws.cell(row=row_no, column=1).border    = border
    ws.cell(row=row_no, column=1).alignment = center

    for col_idx, col in enumerate(columns, 2):
        fn  = col.get("fieldname")
        val = grand_totals.get(fn, "")
        if not isinstance(val, (int, float)):
            val = ""
        cell = ws.cell(row=row_no, column=col_idx, value=val if val else "")
        cell.font      = total_font
        cell.fill      = total_fill
        cell.border    = border
        cell.alignment = center
        if fn in float_fieldnames and val:
            cell.number_format = '#,##0.000'

    # ── Column widths ──
    ws.column_dimensions["A"].width = 8
    for col_idx, col in enumerate(columns, 2):
        fn = col.get("fieldname", "")
        if fn == "item_name":
            w = 50
        elif fn in ["po_total_weight", "total_weight"]:
            w = 18
        else:
            w = 16
        from openpyxl.utils import get_column_letter
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    ws.freeze_panes = "A4"

    # ── Save & respond ──
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response["filename"]    = "Summary_Report.xlsx"
    frappe.response["filecontent"] = file_stream.getvalue()
    frappe.response["type"]        = "binary"


#12 three sheet Excel
@frappe.whitelist()
def get_all_details_for_export(filters, columns=None):

    import openpyxl
    from io import BytesIO
    from frappe.utils.file_manager import save_file
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    filters = frappe.parse_json(filters)

    # ✅ JS se aaye dynamic columns — Summary sheet ke liye
    if columns:
        summary_columns = frappe.parse_json(columns) if isinstance(columns, str) else columns
    else:
        summary_columns = [
            {"fieldname": "item_name",       "label": "Item",            "fieldtype": "Data"},
            {"fieldname": "item_count",      "label": "Total Entries",   "fieldtype": "Int"},
            {"fieldname": "project_count",   "label": "Total Projects",  "fieldtype": "Int"},
            {"fieldname": "po_required_qty", "label": "PO Required Qty", "fieldtype": "Int"},
            {"fieldname": "po_total_weight", "label": "PO Total Weight", "fieldtype": "Float"},
        ]

    SKIP_TOTAL_FIELDNAMES = {"project_count", "item_name", "view"}

    # ── Filter Conditions ─────────────────────────────────────────
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("po_no"):
        conditions += " AND dp.po_no IN %(po_no)s"
        values["po_no"] = tuple(int(p) for p in filters.get("po_no"))

    if filters.get("item"):
        conditions += " AND dp.item IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    if filters.get("stock_rm_type"):
        conditions += " AND rm.stock_rm_type IN %(stock_rm_type)s"
        values["stock_rm_type"] = tuple(filters.get("stock_rm_type"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    # ── Sheet 2: Summary data ──────────────────────────────────────
    summary_data = frappe.db.sql(f"""
        SELECT
            dp.item AS item,
            rm.computed_name AS item_name,
            COALESCE(CAST(st.sort_key AS UNSIGNED), 9999) AS sort_key,
            CAST(REGEXP_SUBSTR(rm.computed_name, '[0-9]+') AS UNSIGNED) AS item_sort,
            COUNT(dp.name)                                         AS item_count,
            COUNT(DISTINCT p.name)                                 AS project_count,
            SUM(COALESCE(dp.quantity, 0))                          AS quantity,
            SUM(COALESCE(dp.lenght, 0))                            AS lenght,
            SUM(COALESCE(dp.width, 0))                             AS width,
            SUM(COALESCE(dp.total_weight, 0))                      AS total_weight,
            SUM(COALESCE(dp.quantity, 0) * COALESCE(pod.required_qty, 0))     AS po_required_qty_raw,
            SUM(COALESCE(dp.total_weight, 0) * COALESCE(pod.required_qty, 0)) AS po_total_weight_raw
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
        LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
        LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        WHERE 1=1 {conditions}
        GROUP BY dp.item, rm.computed_name, st.sort_key
        HAVING dp.item IS NOT NULL
        ORDER BY sort_key ASC, item_sort ASC
    """, values, as_dict=True) or []

    for row in summary_data:
        row["item_count"]      = int(row.get("item_count") or 0)
        row["project_count"]   = int(row.get("project_count") or 0)
        row["quantity"]        = int(row.get("quantity") or 0)
        row["lenght"]          = round(float(row.get("lenght") or 0), 3)
        row["width"]           = round(float(row.get("width") or 0), 3)
        row["total_weight"]    = round(float(row.get("total_weight") or 0), 3)
        row["item_name"]       = row.get("item_name") or "-"
        row["po_required_qty"] = int(float(row.get("po_required_qty_raw") or 0))
        row["po_total_weight"] = round(float(row.get("po_total_weight_raw") or 0), 3)

    # ── Sheet 3: Detail data ───────────────────────────────────────
    # ✅ FIX: po_item_total_weight = SUM(total_weight) × required_qty
    #         (UI ke get_item_details se match — total_weight × req_qty)
    detail_data = frappe.db.sql(f"""
        SELECT
            COALESCE(p.name, 'No Project')     AS project,
            rm.computed_name                    AS item_name,
            dp.po_no                            AS po_no,
            pod.po_serial_no                    AS po_serial_no,
            ad.drawing_number                   AS drawing_number,
            dp.position_no                      AS position_no,
            dp.part_no                          AS part_no,
            COUNT(dp.name)                      AS entry_count,
            IFNULL(SUM(dp.quantity),  0)        AS quantity,
            IFNULL(SUM(dp.lenght),    0)        AS lenght,
            IFNULL(SUM(dp.width),     0)        AS width,
            IFNULL(AVG(dp.single_weight), 0)    AS single_weight,
            IFNULL(SUM(dp.total_weight),  0)    AS total_weight,
            COALESCE(pod.required_qty, 0)       AS required_qty,
            COALESCE(pod.required_qty, 0) * IFNULL(SUM(dp.total_weight), 0)  AS po_item_total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
        LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        WHERE dp.item IS NOT NULL {conditions}
        GROUP BY
            p.name, rm.computed_name, dp.po_no, pod.po_serial_no,
            ad.drawing_number, dp.position_no, dp.part_no, pod.required_qty
        ORDER BY p.name, ad.drawing_number, dp.po_no
    """, values, as_dict=True) or []

    # ── Sheet 1: PO Drawing data ──────────────────────────────────
    po_cond   = ""
    po_values = {}
    if filters.get("project_number"):
        po_cond += " AND pod.project_number IN %(project_number)s"
        po_values["project_number"] = tuple(filters.get("project_number"))
    if filters.get("drawing_number"):
        po_cond += " AND pod.drawing_number IN %(drawing_number)s"
        po_values["drawing_number"] = tuple(filters.get("drawing_number"))

    po_drawing_data = frappe.db.sql(f"""
        SELECT
            COALESCE(pod.project_number, 'No Project') AS project,
            ad.drawing_number,
            pod.po_serial_no,
            pod.po_description,
            IFNULL(pod.unit_weight,  0) AS unit_weight,
            IFNULL(pod.required_qty, 0) AS required_qty,
            IFNULL(pod.total_weight, 0) AS total_weight
        FROM `tabFT Po Drawing` pod
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = pod.drawing_number
        WHERE 1=1 {po_cond}
        ORDER BY project
    """, po_values, as_dict=True) or []

    # ── Excel Styles ──────────────────────────────────────────────
    wb = openpyxl.Workbook()

    thin        = Side(style="thin")
    border      = Border(left=thin, right=thin, top=thin, bottom=thin)
    center      = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align  = Alignment(horizontal="left",   vertical="center", wrap_text=True)
    num3        = "#,##0.000"

    title_font  = Font(size=14, bold=True, color="FFFFFF")
    title_fill  = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="2F75B5")
    total_font  = Font(bold=True, color="FFFFFF")
    total_fill  = PatternFill("solid", fgColor="2F75B5")

    float_fns = set()
    for col in summary_columns:
        ft = (col.get("fieldtype") or "").lower()
        if ft in ["float", "currency", "percent"]:
            float_fns.add(col.get("fieldname"))

    # SHEET 1: Drawing PO List
    ws1 = wb.active
    ws1.title = "Drawing PO List"

    po_headers = ["Sr No", "Project Number", "Drawing Number", "Po Serial No",
                  "PO Description", "Unit Weight", "Required Qty", "Total Weight"]
    N1 = len(po_headers)

    ws1.merge_cells(start_row=1, start_column=1, end_row=1, end_column=N1)
    t = ws1.cell(row=1, column=1, value="PO Summary")
    t.font = title_font; t.fill = title_fill; t.alignment = center

    for col, h in enumerate(po_headers, 1):
        c = ws1.cell(row=3, column=col, value=h)
        c.font = header_font; c.fill = header_fill; c.border = border; c.alignment = center

    ws1.freeze_panes = "A4"
    rn = 4; sr = 1; t_unit = t_req = t_wt = 0

    for d in po_drawing_data:
        vals = [sr, d.project, d.drawing_number, d.po_serial_no,
                d.po_description, d.unit_weight, d.required_qty, d.total_weight]
        for col, val in enumerate(vals, 1):
            c = ws1.cell(row=rn, column=col, value=val)
            c.border = border; c.alignment = center
            if col >= 6: c.number_format = num3
        t_unit += d.unit_weight or 0
        t_req  += d.required_qty or 0
        t_wt   += d.total_weight or 0
        rn += 1; sr += 1

    for col, val in enumerate(["Total", "", "", "", "", t_unit, t_req, t_wt], 1):
        c = ws1.cell(row=rn, column=col, value=val)
        c.font = total_font; c.fill = total_fill; c.border = border; c.alignment = center
        if col >= 6: c.number_format = num3

    for i, w in enumerate([8, 20, 30, 15, 40, 18, 18, 20], 1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    # ════════════════════════════════════════════
    # SHEET 2: Summary — Dynamic columns
    # ════════════════════════════════════════════
    ws2 = wb.create_sheet("Summary")

    N2 = len(summary_columns) + 1
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=N2)
    t = ws2.cell(row=1, column=1, value="Item Wise Summary")
    t.font = title_font; t.fill = title_fill; t.alignment = center

    ws2.cell(row=3, column=1, value="Sr No").font = header_font
    ws2.cell(row=3, column=1).fill = header_fill
    ws2.cell(row=3, column=1).border = border
    ws2.cell(row=3, column=1).alignment = center

    for col_idx, col in enumerate(summary_columns, 2):
        c = ws2.cell(row=3, column=col_idx, value=col.get("label", ""))
        c.font = header_font; c.fill = header_fill
        c.border = border; c.alignment = center

    ws2.freeze_panes = "A4"
    rn = 4; sr = 1
    grand_totals = {col["fieldname"]: 0 for col in summary_columns}

    for d in summary_data:
        ws2.cell(row=rn, column=1, value=sr).border = border
        ws2.cell(row=rn, column=1).alignment = center

        for col_idx, col in enumerate(summary_columns, 2):
            fn  = col.get("fieldname")
            val = d.get(fn, "")
            c   = ws2.cell(row=rn, column=col_idx, value=val)
            c.border    = border
            c.alignment = left_align if fn == "item_name" else center
            if fn in float_fns:
                c.number_format = num3
            if fn not in SKIP_TOTAL_FIELDNAMES and isinstance(val, (int, float)):
                grand_totals[fn] = grand_totals.get(fn, 0) + val

        rn += 1; sr += 1

    ws2.cell(row=rn, column=1, value="Total").font = total_font
    ws2.cell(row=rn, column=1).fill = total_fill
    ws2.cell(row=rn, column=1).border = border
    ws2.cell(row=rn, column=1).alignment = center

    for col_idx, col in enumerate(summary_columns, 2):
        fn = col.get("fieldname")
        if fn in SKIP_TOTAL_FIELDNAMES:
            val = ""
        else:
            val = grand_totals.get(fn, "")
            val = val if isinstance(val, (int, float)) and val else ""

        c = ws2.cell(row=rn, column=col_idx, value=val or "")
        c.font = total_font; c.fill = total_fill
        c.border = border; c.alignment = center
        if fn in float_fns and val:
            c.number_format = num3

    ws2.column_dimensions["A"].width = 8
    for col_idx, col in enumerate(summary_columns, 2):
        fn = col.get("fieldname", "")
        w  = 50 if fn == "item_name" else (20 if "weight" in fn.lower() else 16)
        ws2.column_dimensions[get_column_letter(col_idx)].width = w

    # ════════════════════════════════════════════
    # SHEET 3: Details
    # ✅ FIX: po_item_total_weight = total_weight × required_qty
    # ════════════════════════════════════════════
    ws3 = wb.create_sheet("Details")

    detail_headers = [
        "Sr No", "Project No", "PO No", "Po Serial No", "Drawing",
        "Item No / Position No", "Mark No", "Entry Count",
        "Qty", "Length", "Width", "Single Weight", "Total Weight",
        "PO Required Qty", "PO Total Weight",
    ]
    N3 = len(detail_headers)

    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=N3)
    t = ws3.cell(row=1, column=1, value="Item Wise Detail Report")
    t.font = title_font; t.fill = title_fill; t.alignment = center

    detail_hfill = PatternFill("solid", fgColor="1F4E79")
    po_req_hfont = Font(bold=True, color="FFD700")
    po_wt_hfont  = Font(bold=True, color="7EC8E3")

    for col, h in enumerate(detail_headers, 1):
        c = ws3.cell(row=3, column=col, value=h)
        if col == 14:   c.font = po_req_hfont
        elif col == 15: c.font = po_wt_hfont
        else:           c.font = header_font
        c.fill = detail_hfill; c.border = border; c.alignment = center

    ws3.freeze_panes = "A4"
    rn = 4; sr = 1
    t_qty = t_len = t_wid = t_swt = t_twt = t_po_req = t_po_wt = 0

    for d in detail_data:
        po_no    = d.get("po_no") or ""
        qty      = int(d.get("quantity") or 0)
        lenght   = round(float(d.get("lenght") or 0), 3)
        width    = round(float(d.get("width") or 0), 3)
        s_wt     = round(float(d.get("single_weight") or 0), 3)
        t_wt_val = round(float(d.get("total_weight") or 0), 3)
        req_qty  = int(d.get("required_qty") or 0)
        # ✅ FIX: SQL se aaya po_item_total_weight = total_weight × required_qty
        po_wt    = round(float(d.get("po_item_total_weight") or 0), 3)
        # ✅ FIX: po_req = qty × required_qty (UI se same)
        po_req   = qty * req_qty

        vals = [
            sr, d.get("project"), po_no, d.get("po_serial_no"),
            d.get("drawing_number"), d.get("position_no"), d.get("part_no"),
            int(d.get("entry_count") or 0),
            qty, lenght, width, s_wt, t_wt_val, po_req, po_wt,
        ]

        for col, val in enumerate(vals, 1):
            c = ws3.cell(row=rn, column=col, value=val)
            c.border    = border
            c.alignment = left_align if col in [2, 5] else center
            if col in [10, 11, 12, 13, 15]:
                c.number_format = num3
            if col == 14 and val and val > 0:
                c.font = Font(color="C55A11", bold=True)
            elif col == 15 and val and val > 0:
                c.font = Font(color="1A7ABF", bold=True)

        t_qty    += qty;      t_len    += lenght
        t_wid    += width;    t_swt    += s_wt
        t_twt    += t_wt_val; t_po_req += po_req
        t_po_wt  += po_wt
        rn += 1; sr += 1

    total_vals = [
        "Total", "", "", "", "", "", "", "",
        t_qty, round(t_len,3), round(t_wid,3),
        round(t_swt,3), round(t_twt,3), t_po_req, round(t_po_wt,3),
    ]
    for col, val in enumerate(total_vals, 1):
        c = ws3.cell(row=rn, column=col, value=val)
        c.font = total_font; c.fill = total_fill
        c.border = border; c.alignment = center
        if col in [10, 11, 12, 13, 15]:
            c.number_format = num3

    detail_widths = [7, 18, 14, 14, 28, 22, 12, 14, 10, 22, 22, 22, 18, 18, 18]
    for i, w in enumerate(detail_widths, 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ── Save ─────────────────────────────────────────────────────
    stream = BytesIO()
    wb.save(stream); stream.seek(0)

    file_doc = save_file(
        "FT_Drawing_Part_Report.xlsx",
        stream.getvalue(),
        None, None,
        is_private=0
    )
    return file_doc.file_url


#13 item details EXCEL
@frappe.whitelist()
def download_item_details_excel(filters):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from collections import defaultdict

    filters   = frappe.parse_json(filters)
    item      = filters.get("item")
    project   = filters.get("project")

    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    # ── Dynamic conditions ────────────────────────────────────────
    conditions = "WHERE dp.item = %(item)s"
    sql_values = {"item": item}

    if project:
        conditions += " AND ad.project_number = %(project)s"
        sql_values["project"] = project

    # ── Data query ────────────────────────────────────────────────
    # ✅ FIX: po_total_wt_calc = total_weight × required_qty  (UI se same)
    data = frappe.db.sql(f"""
        SELECT
            p.name            AS project_number,
            dp.po_no          AS po_no,
            pod.po_serial_no  AS po_serial_no,
            ad.drawing_number AS drawing,
            dp.position_no,
            dp.part_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight,
            COALESCE(pod.required_qty, 0)                                              AS po_required_qty,
            COALESCE(pod.required_qty, 0) * COALESCE(dp.quantity,      0)             AS po_req_qty_calc,
            COALESCE(pod.required_qty, 0) * COALESCE(dp.total_weight,  0)             AS po_total_wt_calc
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad  ON ad.name  = dp.drawing_number
        LEFT JOIN `tabFT Project` p       ON p.name   = ad.project_number
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number  = p.name
            AND pod.drawing_number = ad.name
        {conditions}
        ORDER BY
            CAST(pod.po_serial_no AS UNSIGNED) ASC,
            ad.drawing_number ASC
    """, sql_values, as_dict=True)

    # ── Group duplicate rows ──────────────────────────────────────
    grouped = defaultdict(lambda: {
        "project_number": "", "po_no": "", "po_serial_no": "", "drawing": "",
        "position_no": "", "part_no": "", "quantity": 0,
        "lenght": 0, "width": 0, "single_weight": 0, "total_weight": 0,
        "po_required_qty": 0, "po_item_total_weight": 0.0, "entry_count": 0
    })

    for d in data:
        key = (
            d.get("project_number"), d.get("po_no"), d.get("po_serial_no"),
            d.get("drawing"), d.get("position_no"), d.get("part_no"),
            d.get("quantity"), d.get("lenght"), d.get("width"),
            d.get("single_weight"), d.get("total_weight"),
        )
        g = grouped[key]
        g["project_number"]  = d.get("project_number")
        g["po_no"]           = d.get("po_no") or ""
        g["po_serial_no"]    = d.get("po_serial_no")
        g["drawing"]         = d.get("drawing")
        g["position_no"]     = d.get("position_no")
        g["part_no"]         = d.get("part_no")
        g["quantity"]        = d.get("quantity")
        g["lenght"]          = d.get("lenght")
        g["width"]           = d.get("width")
        g["single_weight"]   = d.get("single_weight")
        g["total_weight"]    = d.get("total_weight")

        # ✅ FIX: po_req_qty_calc aur po_total_wt_calc use karo
        g["po_required_qty"]      = max(g["po_required_qty"],
                                        int(d.get("po_req_qty_calc") or 0))
        g["po_item_total_weight"] = max(g["po_item_total_weight"],
                                        float(d.get("po_total_wt_calc") or 0))
        g["entry_count"] += 1

    data = list(grouped.values())

    # ── Excel Setup ───────────────────────────────────────────────
    wb  = openpyxl.Workbook()
    ws  = wb.active
    ws.title = "Item Details"

    thin        = Side(style="thin")
    full_border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center      = Alignment(horizontal="center", vertical="center")
    left_align  = Alignment(horizontal="left",   vertical="center")
    num3        = "#,##0.000"

    hdr_fill     = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    hdr_font     = Font(bold=True, size=12, color="FFFFFF")
    po_req_hfont = Font(bold=True, size=12, color="FFD700")
    po_wt_hfont  = Font(bold=True, size=12, color="7EC8E3")
    data_font    = Font(size=11)
    total_font   = Font(bold=True, size=12, color="FFFFFF")
    total_fill   = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")

    # ── Title ─────────────────────────────────────────────────────
    TOTAL_COLS = 15
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=TOTAL_COLS)
    tc           = ws.cell(row=1, column=1, value=f"Item Details - {item_name}")
    tc.font      = Font(bold=True, size=14)
    tc.alignment = Alignment(horizontal="center", vertical="center")

    # ── Headers ───────────────────────────────────────────────────
    headers = [
        "Sr No", "Project No", "PO No", "Po Serial No", "Drawing",
        "Item No / Position No", "Mark No", "Entry Count",
        "Qty", "Length", "Width", "Single Weight", "Total Weight",
        "PO Required Qty", "PO Total Weight",
    ]

    for col, h in enumerate(headers, 1):
        c           = ws.cell(row=2, column=col, value=h)
        c.fill      = hdr_fill
        c.border    = full_border
        c.alignment = center
        if col == 14:   c.font = po_req_hfont
        elif col == 15: c.font = po_wt_hfont
        else:           c.font = hdr_font

    ws.freeze_panes = "A3"

    # ── Data rows ─────────────────────────────────────────────────
    row_no    = 3
    serial_no = 1
    t_qty = t_len = t_wid = t_swt = t_twt = t_po_req = t_po_wt = 0

    for d in data:
        qty    = int(d.get("quantity")              or 0)
        lenght = round(float(d.get("lenght")        or 0), 3)
        width  = round(float(d.get("width")         or 0), 3)
        s_wt   = round(float(d.get("single_weight") or 0), 3)
        t_wt   = round(float(d.get("total_weight")  or 0), 3)
        po_req = int(d.get("po_required_qty")       or 0)
        po_wt  = round(float(d.get("po_item_total_weight") or 0), 3)
        ec     = int(d.get("entry_count")           or 0)

        row_vals = [
            serial_no, d.get("project_number"), d.get("po_no"),
            d.get("po_serial_no"), d.get("drawing"), d.get("position_no"),
            d.get("part_no"), ec, qty, lenght, width, s_wt, t_wt, po_req, po_wt,
        ]

        for col, val in enumerate(row_vals, 1):
            c           = ws.cell(row=row_no, column=col, value=val)
            c.font      = data_font
            c.border    = full_border
            c.alignment = left_align if col in [2, 5] else center
            if col in [10, 11, 12, 13, 15]:
                c.number_format = num3
            if col == 14 and po_req > 0:
                c.font = Font(size=11, color="C55A11", bold=True)
            elif col == 15 and po_wt > 0:
                c.font = Font(size=11, color="1A7ABF", bold=True)

        t_qty    += qty;    t_len    += lenght
        t_wid    += width;  t_swt    += s_wt
        t_twt    += t_wt;   t_po_req += po_req
        t_po_wt  += po_wt
        row_no   += 1;      serial_no += 1

    # ── Total row ─────────────────────────────────────────────────
    total_vals = [
        "Total", "", "", "", "", "", "", "",
        t_qty, round(t_len,3), round(t_wid,3),
        round(t_swt,3), round(t_twt,3), t_po_req, round(t_po_wt,3),
    ]
    for col, val in enumerate(total_vals, 1):
        c           = ws.cell(row=row_no, column=col, value=val)
        c.fill      = total_fill
        c.border    = full_border
        c.alignment = center
        if col in [10, 11, 12, 13, 15]: c.number_format = num3
        if col == 14:   c.font = Font(bold=True, size=12, color="FFD700")
        elif col == 15: c.font = Font(bold=True, size=12, color="7EC8E3")
        else:           c.font = total_font

    # ── Column widths ─────────────────────────────────────────────
    col_widths = [7, 18, 16, 14, 28, 22, 12, 14, 10, 20, 18, 20, 18, 18, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 32

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response["filename"]    = "Item_Details.xlsx"
    frappe.response["filecontent"] = file_stream.getvalue()
    frappe.response["type"]        = "download"


# --------------------- GENERATE JSON FOR NESTING CENTER      contours and PO quantity calculation ---------------
@frappe.whitelist()
def export_nesting_json(filters=None):
    import json
    import random

    def get_random_color():
        """Generate random color for each part"""
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def create_rectangle_contour(length, width):
        """Create rectangle contour with 4 vertices"""
        return {
            "Type": "LoopBulge",
            "Data": {
                "Vertices": [
                    {"X": 0, "Y": 0, "B": 0},
                    {"X": length, "Y": 0, "B": 0},
                    {"X": length, "Y": width, "B": 0},
                    {"X": 0, "Y": width, "B": 0}
                ]
            }
        }

    filters = frappe.parse_json(filters)
    project = filters.get("project")
    item = filters.get("item")
    
    # Get report filters from the request
    report_filters = filters.get("report_filters", {})
    
    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    # ── Step 1: Build conditions based on report filters ──
    conditions = ""
    values = {"project": project, "item": item}
    
    # Drawing numbers filter
    drawing_numbers = report_filters.get("drawing_number", [])
    if drawing_numbers:
        conditions += " AND ad.name IN %(drawing_numbers)s"
        values["drawing_numbers"] = tuple(drawing_numbers)
    
    # PO numbers filter
    po_numbers = report_filters.get("po_no", [])
    if po_numbers:
        conditions += " AND dp.po_no IN %(po_numbers)s"
        values["po_numbers"] = tuple(po_numbers)
    
    # Is active filter
    if report_filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    # ── Step 2: global_required_qty with SAME filters ──
    po_global_conditions = "WHERE pod.project_number = %(project)s"
    po_global_values = {"project": project}
    
    if drawing_numbers:
        po_global_conditions += " AND pod.drawing_number IN %(drawing_numbers)s"
        po_global_values["drawing_numbers"] = tuple(drawing_numbers)
    
    po_global_result = frappe.db.sql(f"""
        SELECT SUM(COALESCE(pod.required_qty, 0))
        FROM `tabFT Po Drawing` pod
        {po_global_conditions}
    """, po_global_values)

    global_required_qty = int(po_global_result[0][0] or 0) if po_global_result else 0

    # ── Step 3: Drawing Parts fetch karo WITH FILTERS ──
    rows = frappe.db.sql(f"""
        SELECT
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.part_no,
            ad.drawing_number,
            dp.po_no
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        WHERE ad.project_number = %(project)s 
        AND dp.item = %(item)s
        {conditions}
        ORDER BY ad.drawing_number, dp.po_no
    """, values, as_dict=True)

    # Debug log
    frappe.log_error(f"JSON Export: Found {len(rows)} rows for item {item} with drawing filters {drawing_numbers}", "Nesting Export")

    # ── Step 4: Create parts with CORRECT rectangle contours ──
    parts = []
    
    for idx, row in enumerate(rows):
        length = float(row.lenght or 0)
        width = float(row.width or 0)
        qty = int(row.quantity or 0)
        part_no = row.part_no or f"Part_{idx + 1}"
        
        # If width is 0, use length as width (square)
        if width == 0:
            width = length
        
        # Calculate PO required quantity
        po_qty = qty * global_required_qty if global_required_qty > 0 else qty
        
        # ✅ CORRECT: Create rectangle contour using the function
        contours = [create_rectangle_contour(length, width)]
        
        # Create unique part name
        unique_part_name = f"{part_no}_{length}x{width}"
        
        parts.append({
            "Quantity": po_qty,
            "Contours": contours,
            "RefPt": {"X": 0, "Y": 0},
            "Name": unique_part_name,
            "Colour": get_random_color()
        })

    # ── Step 5: RawPlates configuration ──
    if rows:
        max_length = max((row.get("lenght", 0) or 0 for row in rows), default=12000)
        max_width = max((row.get("width", 0) or 0 for row in rows), default=1000)
    else:
        max_length = 12000
        max_width = 600
    
    # Sheet size calculation
    sheet_length = max(12000, max_length)
    sheet_width = max(600, max_width * 2) if max_width > 0 else 600

    raw_plates = [{
        "Quantity": 10,
        "RectangularShape": {
            "Length": str(sheet_length),
            "Width": str(sheet_width)
        },
        "Name": f"Sheet {sheet_length}x{sheet_width}"
    }]

    # ── Step 6: Final JSON structure ──
    data = {
        "Settings": {
            "DimensionLimit": None,
            "DistancePartPart": "0",
            "DistancePartRawPlate": "0",
            "MirrorControl": "Allow",
            "NestingInHoles": True,
            "RotationControl": "Free",
            "SortRawPlates": True,
            "GroupLayouts": True,
            "PlacementDirection": "LeftDown",
            "RotationTwist": {"Deg": 0},
            "NestingMode": "General",
            "SettingsStrips": {"Sorting": "Length"},
            "LayoutDuplicationAuto": False
        },
        "Problem": {
            "Parts": parts,
            "RawPlates": raw_plates
        },
        "StopConditions": {
            "AllPartsNested": False,
            "Scrap": False,
            "ScrapValue": 0,
            "Scrap2": False,
            "Scrap2Value": 0,
            "SmartStop": False,
            "Timeout": True,
            "TimeoutValue": 300
        }
    }

    # ── Step 7: Return JSON file for download ──
    frappe.response["filename"] = f"nesting_{item_name}_{len(parts)}parts.json"
    frappe.response["filecontent"] = json.dumps(data, indent=4)
    frappe.response["type"] = "download"


# --------------------- NESTING REPORT SAVE & FETCH ---------------------
@frappe.whitelist()
def save_nesting_report(item, project, sheets, nested_parts, scrap, pdf_url=""):
    try:
        existing = frappe.db.get_value(
            "FT Nesting Report",
            {"item": item, "project": project},
            "name"
        )

        if existing:
            doc = frappe.get_doc("FT Nesting Report", existing)
        else:
            doc = frappe.new_doc("FT Nesting Report")
            doc.item    = item
            doc.project = project

        doc.sheets       = sheets
        doc.nested_parts = nested_parts
        doc.scrap        = scrap
        doc.pdf_url      = pdf_url

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "name": doc.name}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "save_nesting_report Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_nesting_report(item, project):
    try:
        name = frappe.db.get_value(
            "FT Nesting Report",
            {"item": item, "project": project},
            "name"
        )

        if not name:
            return {"found": False}

        doc = frappe.get_doc("FT Nesting Report", name)

        return {
            "found":        True,
            "sheets":       doc.sheets       or "—",
            "nested_parts": doc.nested_parts or "—",
            "scrap":        doc.scrap        or "—",
            "pdf_url":      doc.pdf_url      or "",
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_nesting_report Error")
        return {"found": False, "error": str(e)}

# --------------------- GENERATE JSON FOR NESTING CENTER ---------------------


# ---------------------- Snapshot Save with drawing number -------------
@frappe.whitelist()
def save_row_data(sr_no, project, item_name, item_count, quantity, lenght, width,
                  total_weight, po_required_qty=0, po_total_weight=0, drawing_number=None):
    import json
    from frappe.utils import now_datetime

    timestamp = now_datetime().strftime("%d/%m/%Y (%H:%M:%S)")

    # ── Step 1: Get item ID once (reused later) ──────────────────
    item_id = frappe.db.get_value(
        "FT Stock RM List", {"computed_name": item_name}, "name"
    )
    if not item_id:
        return {"status": "error", "msg": f"Item '{item_name}' not found in Stock RM List."}

    # ── Step 2: Fetch existing revisions (lightweight) ───────────
    filters = {"item": item_name}
    if project:
        filters["project_number"] = project

    existing_docs = frappe.get_all(
        "FT Store Revision Data",
        filters=filters,
        fields=["name"],
        order_by="creation asc"
    )

    clean_item = item_name.replace(" ", "-").replace("/", "-")

    # ── Step 3: FAST live aggregate check ────────────────────────
    # Only 5 numbers — no JOINs on drawing detail, very fast
    if project:
        live_agg = frappe.db.sql("""
            SELECT
                COUNT(dp.name)                   AS total_entries,
                SUM(COALESCE(dp.quantity,  0))   AS total_qty,
                SUM(COALESCE(dp.lenght,    0))   AS total_length,
                SUM(COALESCE(dp.width,     0))   AS total_width,
                SUM(COALESCE(dp.total_weight,0)) AS total_weight
            FROM `tabFT Drawing Parts` dp
            INNER JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
            WHERE ad.project_number = %(project)s
              AND dp.item = %(item_id)s
        """, {"project": project, "item_id": item_id}, as_dict=True)
    else:
        live_agg = frappe.db.sql("""
            SELECT
                COUNT(dp.name)                   AS total_entries,
                SUM(COALESCE(dp.quantity,  0))   AS total_qty,
                SUM(COALESCE(dp.lenght,    0))   AS total_length,
                SUM(COALESCE(dp.width,     0))   AS total_width,
                SUM(COALESCE(dp.total_weight,0)) AS total_weight
            FROM `tabFT Drawing Parts` dp
            WHERE dp.item = %(item_id)s
        """, {"item_id": item_id}, as_dict=True)

    live = live_agg[0] if live_agg and live_agg[0] else {}

    new_entry = {
        "timestamp":       timestamp,
        "total_entries":   float(live.get("total_entries") or 0),
        "total_qty":       float(live.get("total_qty")     or 0),
        "total_length":    float(live.get("total_length")  or 0),
        "total_width":     float(live.get("total_width")   or 0),
        "total_weight":    float(live.get("total_weight")  or 0),
        "po_required_qty": float(po_required_qty or 0),
        "po_total_weight": float(po_total_weight or 0),
    }

    # ── Step 4: No-change check against last saved revision ──────
    # Done BEFORE any heavy query — exit fast if nothing changed
    if existing_docs:
        last_doc = frappe.db.get_value(
            "FT Store Revision Data",
            existing_docs[-1].name,
            "revision_log"
        )
        try:
            revision_log = json.loads(last_doc or "[]")
        except:
            revision_log = []

        if revision_log:
            last = revision_log[-1]
            changed = any([
                float(last.get("total_entries") or 0) != new_entry["total_entries"],
                float(last.get("total_qty")     or 0) != new_entry["total_qty"],
                float(last.get("total_length")  or 0) != new_entry["total_length"],
                float(last.get("total_width")   or 0) != new_entry["total_width"],
                float(last.get("total_weight")  or 0) != new_entry["total_weight"],
            ])
            if not changed:
                # ← Exit immediately, no drawing detail fetch needed
                return {
                    "status": "success",
                    "msg":    "The Data is the same, there has been no change."
                }
    else:
        revision_log = []

    # ── Step 5: Fetch drawing detail rows (only if change detected) ──
    if project:
        drawing_rows = frappe.db.sql("""
            SELECT
                p.name                                                        AS project_number,
                dp.po_no                                                      AS po_no,
                pod.po_serial_no                                              AS po_serial_no,
                ad.drawing_number                                             AS drawing_number,
                dp.position_no                                                AS position_no,
                dp.part_no                                                    AS part_no,
                dp.quantity,
                dp.lenght,
                dp.width,
                dp.single_weight,
                dp.total_weight,
                COALESCE(pod.required_qty, 0)                                 AS required_qty,
                COALESCE(pod.required_qty, 0) * COALESCE(dp.quantity,     0) AS po_required_qty,
                COALESCE(pod.required_qty, 0) * COALESCE(dp.total_weight, 0) AS po_item_total_weight
            FROM `tabFT Drawing Parts` dp
            INNER JOIN `tabFT Add Drawing` ad ON ad.name  = dp.drawing_number
            INNER JOIN `tabFT Project` p      ON p.name   = ad.project_number
            LEFT  JOIN `tabFT Po Drawing` pod
                ON pod.project_number  = p.name
                AND pod.drawing_number = ad.name
            WHERE p.name = %(project)s
              AND dp.item = %(item_id)s
            ORDER BY ad.drawing_number ASC, dp.po_no ASC
        """, {"project": project, "item_id": item_id}, as_dict=True) or []
    else:
        drawing_rows = frappe.db.sql("""
            SELECT
                p.name                                                        AS project_number,
                dp.po_no                                                      AS po_no,
                pod.po_serial_no                                              AS po_serial_no,
                ad.drawing_number                                             AS drawing_number,
                dp.position_no                                                AS position_no,
                dp.part_no                                                    AS part_no,
                dp.quantity,
                dp.lenght,
                dp.width,
                dp.single_weight,
                dp.total_weight,
                COALESCE(pod.required_qty, 0)                                 AS required_qty,
                COALESCE(pod.required_qty, 0) * COALESCE(dp.quantity,     0) AS po_required_qty,
                COALESCE(pod.required_qty, 0) * COALESCE(dp.total_weight, 0) AS po_item_total_weight
            FROM `tabFT Drawing Parts` dp
            LEFT  JOIN `tabFT Add Drawing` ad ON ad.name  = dp.drawing_number
            LEFT  JOIN `tabFT Project` p      ON p.name   = ad.project_number
            LEFT  JOIN `tabFT Po Drawing` pod
                ON pod.project_number  = p.name
                AND pod.drawing_number = ad.name
            WHERE dp.item = %(item_id)s
            ORDER BY ad.drawing_number ASC, dp.po_no ASC
        """, {"item_id": item_id}, as_dict=True) or []

    # ── Step 6: Build new parent doc name ────────────────────────
    revision_log.append(new_entry)
    next_revision = len(existing_docs) + 1
    new_name = f"Revision-{next_revision}-{clean_item}-{str(sr_no).zfill(3)}"

    # ── Step 7: INSERT parent doc ─────────────────────────────────
    frappe.db.sql("""
        INSERT INTO `tabFT Store Revision Data`
            (name, sr_no, project_number, item, drawing_number,
             total_entries, total_qty, total_length, total_width, total_weight,
             revision_log, owner, creation, modified, modified_by, docstatus)
        VALUES
            (%(name)s, %(sr_no)s, %(project_number)s, %(item)s, %(drawing_number)s,
             %(total_entries)s, %(total_qty)s, %(total_length)s, %(total_width)s, %(total_weight)s,
             %(revision_log)s, %(owner)s, NOW(), NOW(), %(owner)s, 0)
        ON DUPLICATE KEY UPDATE
            total_entries = VALUES(total_entries),
            total_qty     = VALUES(total_qty),
            total_length  = VALUES(total_length),
            total_width   = VALUES(total_width),
            total_weight  = VALUES(total_weight),
            revision_log  = VALUES(revision_log),
            modified      = NOW(),
            modified_by   = VALUES(modified_by)
    """, {
        "name":           new_name,
        "sr_no":          sr_no,
        "project_number": project or "",
        "item":           item_name,
        "drawing_number": drawing_number or "",
        "total_entries":  new_entry["total_entries"],
        "total_qty":      new_entry["total_qty"],
        "total_length":   new_entry["total_length"],
        "total_width":    new_entry["total_width"],
        "total_weight":   new_entry["total_weight"],
        "revision_log":   json.dumps(revision_log),
        "owner":          frappe.session.user,
    })

    # ── Step 8: BULK INSERT child rows (single query) ─────────────
    # Instead of N separate INSERTs → one INSERT with N value tuples
    if drawing_rows:
        owner = frappe.session.user

        # Build VALUES tuples
        values_list = []
        params      = {}

        for idx, r in enumerate(drawing_rows, 1):
            k = str(idx)
            child_name = f"{new_name}-DD-{str(idx).zfill(4)}"
            values_list.append(f"""(
                %(name_{k})s, %(parent_{k})s,
                'FT Store Revision Data', 'drawing_details', %(idx_{k})s,
                %(project_number_{k})s, %(drawing_number_{k})s,
                %(po_no_{k})s, %(po_serial_no_{k})s,
                %(position_no_{k})s, %(part_no_{k})s,
                %(quantity_{k})s, %(lenght_{k})s, %(width_{k})s,
                %(single_weight_{k})s, %(total_weight_{k})s,
                %(po_required_qty_{k})s, %(po_item_total_weight_{k})s,
                %(owner_{k})s, NOW(), NOW(), %(owner_{k})s, 0
            )""")
            params.update({
                f"name_{k}":                child_name,
                f"parent_{k}":              new_name,
                f"idx_{k}":                 idx,
                f"project_number_{k}":      str(r.get("project_number") or ""),
                f"drawing_number_{k}":      str(r.get("drawing_number") or ""),
                f"po_no_{k}":               str(r.get("po_no") or ""),
                f"po_serial_no_{k}":        str(r.get("po_serial_no") or ""),
                f"position_no_{k}":         str(r.get("position_no") or ""),
                f"part_no_{k}":             str(r.get("part_no") or ""),
                f"quantity_{k}":            int(r.get("quantity") or 0),
                f"lenght_{k}":              round(float(r.get("lenght") or 0), 3),
                f"width_{k}":               round(float(r.get("width") or 0), 3),
                f"single_weight_{k}":       round(float(r.get("single_weight") or 0), 3),
                f"total_weight_{k}":        round(float(r.get("total_weight") or 0), 3),
                f"po_required_qty_{k}":     int(r.get("po_required_qty") or 0),
                f"po_item_total_weight_{k}":round(float(r.get("po_item_total_weight") or 0), 3),
                f"owner_{k}":               owner,
            })

        # Split into chunks of 500 to avoid query size limits
        CHUNK = 500
        all_tuples = list(zip(values_list, [
            {k: v for k, v in params.items() if k.endswith(f"_{str(i)}")}
            for i in range(1, len(drawing_rows) + 1)
        ]))

        chunk_params = {}
        chunk_vals   = []
        flush_count  = 0

        for vt, p in all_tuples:
            chunk_vals.append(vt)
            chunk_params.update(p)
            flush_count += 1

            if flush_count >= CHUNK:
                frappe.db.sql(f"""
                    INSERT INTO `tabFT Revision Drawing Detail`
                        (name, parent, parenttype, parentfield, idx,
                         project_number, drawing_number, po_no, po_serial_no,
                         position_no, part_no,
                         quantity, lenght, width, single_weight, total_weight,
                         po_required_qty, po_item_total_weight,
                         owner, creation, modified, modified_by, docstatus)
                    VALUES {", ".join(chunk_vals)}
                """, chunk_params)
                chunk_vals   = []
                chunk_params = {}
                flush_count  = 0

        # Remaining rows
        if chunk_vals:
            frappe.db.sql(f"""
                INSERT INTO `tabFT Revision Drawing Detail`
                    (name, parent, parenttype, parentfield, idx,
                     project_number, drawing_number, po_no, po_serial_no,
                     position_no, part_no,
                     quantity, lenght, width, single_weight, total_weight,
                     po_required_qty, po_item_total_weight,
                     owner, creation, modified, modified_by, docstatus)
                VALUES {", ".join(chunk_vals)}
            """, chunk_params)

    frappe.db.commit()
    return {"status": "success", "msg": "✅ Data saved successfully!"}
 
@frappe.whitelist()
def compare_row_data(sr_no, project, item_name, item_count, quantity, lenght, width, total_weight):
    import json
    from frappe.utils import now_datetime
 
    all_saved = frappe.db.get_all(
        "FT Store Revision Data",
        filters={"item": item_name},
        fields=["project_number", "revision_log", "total_entries",
                "total_qty", "total_length", "total_width", "total_weight"]
    )
    if not all_saved:
        return {"status": "error", "msg": "No saved data found, First save the data"}
 
    item_id = frappe.db.get_value("FT Stock RM List", {"computed_name": item_name}, "name")
    if item_id:
        drawing_rows = frappe.db.sql("""
            SELECT DISTINCT ad.drawing_number
            FROM `tabFT Drawing Parts` dp
            LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
            WHERE dp.item = %s AND ad.drawing_number IS NOT NULL
            ORDER BY ad.drawing_number ASC
        """, (item_id,), as_list=True)
        drawing_list = [r[0] for r in drawing_rows if r[0]]
    else:
        drawing_list = []
 
    drawing_str = ", ".join(sorted(drawing_list))
    all_projects = [d.project_number for d in all_saved if d.project_number]
 
    if not all_projects and item_id:
        proj_rows = frappe.db.sql("""
            SELECT DISTINCT ad.project_number
            FROM `tabFT Drawing Parts` dp
            LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
            WHERE dp.item = %s AND ad.project_number IS NOT NULL
            ORDER BY ad.project_number ASC
        """, (item_id,), as_list=True)
        all_projects = [r[0] for r in proj_rows if r[0]]
 
    max_rev_count = 0
    for d in all_saved:
        try:
            log = json.loads(d.revision_log or "[]")
            max_rev_count = max(max_rev_count, len(log))
        except: pass
 
    fields = ["total_entries", "total_qty", "total_length", "total_width", "total_weight",
              "po_required_qty", "po_total_weight"]
 
    revision_sums = []
    for ri in range(max_rev_count):
        rev_sum = {f: 0.0 for f in fields}
        rev_sum["timestamp"] = ""
        for d in all_saved:
            try:
                log = json.loads(d.revision_log or "[]")
                if ri < len(log):
                    for f in fields: rev_sum[f] += float(log[ri].get(f) or 0)
                    if log[ri].get("timestamp"): rev_sum["timestamp"] = log[ri]["timestamp"]
            except: pass
        revision_sums.append(rev_sum)
 
    db_sum = frappe.db.sql("""
        SELECT SUM(CAST(total_entries AS DECIMAL(20,3))) as total_entries,
            SUM(CAST(total_qty AS DECIMAL(20,3))) as total_qty,
            SUM(CAST(total_length AS DECIMAL(20,3))) as total_length,
            SUM(CAST(total_width AS DECIMAL(20,3))) as total_width,
            SUM(CAST(total_weight AS DECIMAL(20,3))) as total_weight
        FROM `tabFT Store Revision Data` WHERE item = %(item)s
    """, {"item": item_name}, as_dict=True)
 
    current_values = (
        {f: float(db_sum[0].get(f) or 0) for f in ["total_entries","total_qty","total_length","total_width","total_weight"]}
        if db_sum and db_sum[0] else {f: 0.0 for f in fields}
    )
    if revision_sums:
        last_rev = revision_sums[-1]
        current_values["po_required_qty"] = last_rev.get("po_required_qty", 0.0)
        current_values["po_total_weight"] = last_rev.get("po_total_weight", 0.0)
    else:
        current_values["po_required_qty"] = 0.0
        current_values["po_total_weight"] = 0.0
 
    current_timestamp = now_datetime().strftime("%d/%m/%Y (%H:%M:%S)")
 
    return {
        "status": "success", "revision_log": revision_sums,
        "current": current_values, "current_timestamp": current_timestamp,
        "project": ", ".join(all_projects), "project_count": len(all_projects),
        "item_name": item_name, "drawing_numbers": drawing_str,
    }

@frappe.whitelist()
def export_compare_snapshot_excel(snapshot_data):
    import json
    import openpyxl
    from io import BytesIO
    from frappe.utils.file_manager import save_file
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    snapshot_data = frappe.parse_json(snapshot_data)

    fields = ["total_entries", "total_qty", "total_length", "total_width", "total_weight",
              "po_required_qty", "po_total_weight"]
    field_labels = {
        "total_entries":   "Total Entries",
        "total_qty":       "Total Qty",
        "total_length":    "Total Length",
        "total_width":     "Total Width",
        "total_weight":    "Total Weight",
        "po_required_qty": "PO Required Qty",
        "po_total_weight": "PO Total Weight",
    }

    row_compare_fields = [
        "quantity", "lenght", "width", "single_weight",
        "total_weight", "po_required_qty", "po_item_total_weight"
    ]
    row_field_labels = {
        "quantity":             "Qty",
        "lenght":               "Length",
        "width":                "Width",
        "single_weight":        "Single Weight",
        "total_weight":         "Total Weight",
        "po_required_qty":      "PO Required Qty",
        "po_item_total_weight": "PO Total Weight",
    }

    max_revisions = 0
    for item_data in snapshot_data:
        max_revisions = max(max_revisions, len(item_data.get("revision_log") or []))

    wb = openpyxl.Workbook()

    thin           = Side(style="thin")
    border         = Border(left=thin, right=thin, top=thin, bottom=thin)
    center         = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align     = Alignment(horizontal="left",   vertical="center", wrap_text=True)
    num3           = "#,##0.000"

    title_font     = Font(bold=True, size=14, color="FFFFFF")
    title_fill     = PatternFill("solid", fgColor="1F4E79")
    header_font    = Font(bold=True, size=11, color="FFFFFF")
    header_fill    = PatternFill("solid", fgColor="2F75B5")
    diff_hfill     = PatternFill("solid", fgColor="7B2D8B")
    diff_hfont     = Font(bold=True, size=11, color="FFFFFF")
    changed_font   = Font(bold=True, color="C55A11")
    normal_font    = Font(size=11, color="333333")
    diff_pos_font  = Font(bold=True, color="1A7ABF")
    diff_neg_font  = Font(bold=True, color="C00000")
    diff_zero_font = Font(size=11, color="888888")
    yellow_fill    = PatternFill("solid", fgColor="FFF8E1")
    diff_pos_fill  = PatternFill("solid", fgColor="E8F4FD")
    diff_neg_fill  = PatternFill("solid", fgColor="FFE8E8")
    white_fill     = PatternFill("solid", fgColor="FFFFFF")

    # ════════════════════════════════════════════════════════════
    # SHEET 1: Compare Snapshot
    # ════════════════════════════════════════════════════════════
    ws1 = wb.active
    ws1.title = "Compare Snapshot"
    total_cols = 5 + max_revisions + 1

    ws1.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    tc = ws1.cell(row=1, column=1, value="Revision History — Grouped by Item")
    tc.font = title_font; tc.fill = title_fill; tc.alignment = center
    ws1.row_dimensions[1].height = 26

    headers = ["Projects", "Item", "Drawing Numbers", "Project Count", "Field"]
    for i in range(max_revisions):
        headers.append(f"Revision {i + 1}")
    headers.append("Difference\n(Rev 1 - Rev 2)")

    for col, h in enumerate(headers, 1):
        is_diff = col == total_cols
        c = ws1.cell(row=2, column=col, value=h)
        c.font = diff_hfont if is_diff else header_font
        c.fill = diff_hfill if is_diff else header_fill
        c.border = border; c.alignment = center
    ws1.row_dimensions[2].height = 30

    data_row = 3
    for item_data in snapshot_data:
        if item_data.get("status") != "success": continue
        project         = item_data.get("project", "")
        item_name_val   = item_data.get("item_name", "")
        drawing_numbers = item_data.get("drawing_numbers", "")
        project_count   = item_data.get("project_count", 0)
        revision_log    = item_data.get("revision_log") or []
        current         = item_data.get("current") or {}
        rev1 = revision_log[0] if len(revision_log) > 0 else None
        rev2 = revision_log[1] if len(revision_log) > 1 else None
        start_row = data_row

        for fi, f in enumerate(fields):
            row_num  = data_row + fi
            rev1_val = float(rev1.get(f) or 0) if rev1 else None
            rev2_val = float(rev2.get(f) or 0) if rev2 else None
            diff_val = (rev2_val - rev1_val) if (rev1_val is not None and rev2_val is not None) else None
            last     = revision_log[-1] if revision_log else None
            last_val = float(last.get(f) or 0) if last else None
            row_fill = yellow_fill if (last_val is not None and last_val != float(current.get(f) or 0)) else white_fill

            fixed_cols = [
                (project         if fi == 0 else "", Font(bold=True, size=10, color="1F4E79"), center,     row_fill),
                (item_name_val   if fi == 0 else "", Font(size=10),                            left_align, row_fill),
                (drawing_numbers if fi == 0 else "", Font(size=9, color="555555"),             left_align, row_fill),
                (project_count   if fi == 0 else "", Font(bold=True, size=13, color="2F75B5"), center,     row_fill),
                (field_labels[f],                    Font(bold=True, size=11),                 center,     row_fill),
            ]
            for col_idx, (val, fnt, algn, fil) in enumerate(fixed_cols, 1):
                c = ws1.cell(row=row_num, column=col_idx, value=val)
                c.font = fnt; c.border = border; c.alignment = algn; c.fill = fil

            for ri in range(max_revisions):
                col_num = 6 + ri
                if ri < len(revision_log):
                    rev      = revision_log[ri]
                    rev_val  = float(rev.get(f) or 0)
                    prev_val = float(revision_log[ri - 1].get(f) or 0) if ri > 0 else None
                    rev_chg  = prev_val is not None and prev_val != rev_val
                    c = ws1.cell(row=row_num, column=col_num,
                                 value=f"{rev_val}\n{rev.get('timestamp', '')}")
                    c.font = changed_font if rev_chg else normal_font
                    c.border = border; c.alignment = center; c.fill = row_fill
                else:
                    c = ws1.cell(row=row_num, column=col_num, value="-")
                    c.font = Font(color="CCCCCC"); c.border = border
                    c.alignment = center; c.fill = row_fill

            diff_col = 6 + max_revisions
            if diff_val is None:
                dd, df, dfi = "0.000\n(No Changes)", diff_zero_font, white_fill
            elif diff_val > 0:
                dd, df, dfi = f"+{diff_val:.3f}\n(▲ Increased)", diff_pos_font, diff_pos_fill
            elif diff_val < 0:
                dd, df, dfi = f"{diff_val:.3f}\n(▼ Decreased)", diff_neg_font, diff_neg_fill
            else:
                dd, df, dfi = "0.000\n(No Change)", diff_zero_font, white_fill

            c = ws1.cell(row=row_num, column=diff_col, value=dd)
            c.font = df; c.border = border; c.alignment = center; c.fill = dfi

        for r in range(start_row, start_row + len(fields)):
            ws1.row_dimensions[r].height = 38
        data_row += len(fields)

    col_widths_s1 = [30, 38, 35, 14, 16] + [22] * max_revisions + [22]
    for i, w in enumerate(col_widths_s1, 1):
        ws1.column_dimensions[get_column_letter(i)].width = w
    ws1.freeze_panes = "A3"

    # ════════════════════════════════════════════════════════════
    # Fetch drawing detail rows
    # ════════════════════════════════════════════════════════════
    def make_row_key(r):
        return (
            str(r.get("drawing_number") or ""),
            str(r.get("position_no") or ""),
            str(r.get("part_no") or ""),
        )

    def get_detail_rows(doc_name):
        return frappe.db.sql("""
            SELECT drawing_number, position_no, part_no, project_number,
                   po_no, po_serial_no,
                   quantity, lenght, width, single_weight, total_weight,
                   po_required_qty, po_item_total_weight
            FROM `tabFT Revision Drawing Detail`
            WHERE parent = %(parent)s
            ORDER BY idx ASC
        """, {"parent": doc_name}, as_dict=True) or []

    all_item_names = [d.get("item_name", "") for d in snapshot_data if d.get("status") == "success"]
    all_display_rows = []

    for item_name in all_item_names:
        rev_docs = frappe.get_all(
            "FT Store Revision Data",
            filters={"item": item_name},
            fields=["name", "creation"],
            order_by="creation desc",
            limit=2
        )
        if not rev_docs:
            continue

        curr_rows = get_detail_rows(rev_docs[0].name)

        if len(rev_docs) == 1:
            for curr_row in curr_rows:
                all_display_rows.append({
                    "item_name": item_name, "curr": curr_row,
                    "prev": None, "changed_fields": [],
                    "is_first_save": True, "is_new_row": False,
                })
        else:
            prev_rows = get_detail_rows(rev_docs[1].name)
            prev_map  = {make_row_key(r): r for r in prev_rows}
            for curr_row in curr_rows:
                key      = make_row_key(curr_row)
                prev_row = prev_map.get(key, None)
                if prev_row is None:
                    changed_fields = row_compare_fields[:]
                    is_new_row = True
                else:
                    changed_fields = [
                        f for f in row_compare_fields
                        if round(float(prev_row.get(f) or 0), 3) != round(float(curr_row.get(f) or 0), 3)
                    ]
                    is_new_row = False
                all_display_rows.append({
                    "item_name": item_name, "curr": curr_row,
                    "prev": prev_row, "changed_fields": changed_fields,
                    "is_first_save": False, "is_new_row": is_new_row,
                })

    FILL_CHANGED    = PatternFill("solid", fgColor="FFE0B2")
    FILL_NEW_ROW    = PatternFill("solid", fgColor="C8E6C9")
    FILL_FIRST_SAVE = PatternFill("solid", fgColor="E3F2FD")
    FILL_NORMAL_A   = PatternFill("solid", fgColor="FAFAFA")
    FILL_NORMAL_B   = PatternFill("solid", fgColor="F0F4F8")
    FILL_CHG_CELL   = PatternFill("solid", fgColor="FF9800")
    FONT_CHG_CELL   = Font(bold=True, size=11, color="FFFFFF")

    # ════════════════════════════════════════════════════════════
    # SHEET 2 — Drawing Wise Detail
    # ════════════════════════════════════════════════════════════
    ws2 = wb.create_sheet("Drawing Wise Detail")

    FIELD_COL_MAP = {
        7: "quantity", 8: "lenght", 9: "width", 10: "single_weight",
        11: "total_weight", 12: "po_required_qty", 13: "po_item_total_weight",
    }

    s2_headers = [
        "Sr No", "Item", "Project", "Drawing", "Position No", "Mark No",
        "Qty", "Length", "Width", "Single Weight", "Total Weight",
        "PO Required Qty", "PO Total Weight", "🔍 View Change",
    ]
    N2 = len(s2_headers)

    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=N2)
    tc2 = ws2.cell(row=1, column=1,
                   value="Drawing Wise Detail  |  🟠 Orange Row = Changed  |  Click '🔍 View Change' for Before & After Detail")
    tc2.font = title_font; tc2.fill = title_fill; tc2.alignment = center
    ws2.row_dimensions[1].height = 28

    ws2.merge_cells(start_row=2, start_column=1, end_row=2, end_column=N2)
    lg = ws2.cell(row=2, column=1,
                  value="🔵 First Save   |   🟠 Changed Row (darker orange = changed field)   |   🟢 New Row Added   |   ⬜ No Change")
    lg.font = Font(size=10, italic=True, color="333333")
    lg.fill = PatternFill("solid", fgColor="E3F2FD")
    lg.alignment = center; lg.border = border
    ws2.row_dimensions[2].height = 18

    for col, h in enumerate(s2_headers, 1):
        c = ws2.cell(row=3, column=col, value=h)
        c.fill = PatternFill("solid", fgColor="1F4E79")
        c.border = border; c.alignment = center
        c.font = Font(bold=True, size=11, color="FFD700") if col == N2 else header_font
    ws2.row_dimensions[3].height = 24
    ws2.freeze_panes = "A4"

    s2_row = 4
    s3_row = 2
    unch_idx = 0

    # ════════════════════════════════════════════════════════════
    # SHEET 3 — Change Detail (clean card layout like Image 2)
    # ════════════════════════════════════════════════════════════
    ws3 = wb.create_sheet("Change Detail")

    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
    tc3 = ws3.cell(row=1, column=1, value="Change Detail — Before & After")
    tc3.font = title_font; tc3.fill = title_fill; tc3.alignment = center
    ws3.row_dimensions[1].height = 28

    # Blank row after title
    ws3.row_dimensions[2].height = 8
    s3_row = 3

    s3_has_content = False

    # Column widths Sheet 3
    s3_col_widths = [18, 22, 18, 16, 16, 18]
    for i, w in enumerate(s3_col_widths, 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ════════════════════════════════════════════════════════════
    # Fill Sheet 2 rows + Sheet 3 cards
    # ════════════════════════════════════════════════════════════
    for idx, entry in enumerate(all_display_rows, 1):
        item_name   = entry["item_name"]
        curr        = entry["curr"]
        prev        = entry["prev"]
        chg_fields  = entry["changed_fields"]
        is_first    = entry.get("is_first_save", False)
        is_new_row  = entry.get("is_new_row", False)
        has_changes = len(chg_fields) > 0
        s3_anchor   = s3_row

        # ── Sheet 2 row fill ──
        if is_first:
            row_fill = FILL_FIRST_SAVE
        elif is_new_row:
            row_fill = FILL_NEW_ROW
        elif has_changes:
            row_fill = FILL_CHANGED
        else:
            unch_idx += 1
            row_fill = FILL_NORMAL_A if unch_idx % 2 == 0 else FILL_NORMAL_B

        curr_vals = [
            idx, item_name,
            curr.get("project_number", ""),
            curr.get("drawing_number", ""),
            curr.get("position_no", ""),
            curr.get("part_no", ""),
            int(curr.get("quantity") or 0),
            round(float(curr.get("lenght") or 0), 3),
            round(float(curr.get("width") or 0), 3),
            round(float(curr.get("single_weight") or 0), 3),
            round(float(curr.get("total_weight") or 0), 3),
            int(curr.get("po_required_qty") or 0),
            round(float(curr.get("po_item_total_weight") or 0), 3),
            "🔍 View Change" if has_changes else "✅ No Change",
        ]

        for col, val in enumerate(curr_vals, 1):
            c = ws2.cell(row=s2_row, column=col, value=val)
            c.border    = border
            c.alignment = left_align if col in [2, 3, 4] else center
            fn = FIELD_COL_MAP.get(col)

            if col == N2:
                if has_changes:
                    c.hyperlink = f"#'Change Detail'!A{s3_anchor}"
                    c.font = Font(bold=True, size=11, color="1565C0", underline="single")
                    c.fill = PatternFill("solid", fgColor="BBDEFB")
                else:
                    c.font = Font(size=11, color="388E3C")
                    c.fill = PatternFill("solid", fgColor="E8F5E9")
            elif fn and fn in chg_fields and has_changes:
                c.fill = FILL_CHG_CELL
                c.font = FONT_CHG_CELL
            else:
                c.fill = row_fill
                if has_changes:    c.font = Font(bold=True, size=11, color="5D4037")
                elif is_first:     c.font = Font(size=11, color="1565C0")
                elif is_new_row:   c.font = Font(bold=True, size=11, color="1B5E20")
                else:              c.font = Font(size=11, color="444444")

            if col in [8, 9, 10, 11, 13]:
                c.number_format = num3

        ws2.row_dimensions[s2_row].height = 20
        s2_row += 1

        # ── Sheet 3 card: only changed rows ──────────────────────
        if not has_changes:
            continue

        s3_has_content = True

        # ── Card Row 1: Sr No badge + Item Name ──────────────────
        badge_val = f"# {idx}" + ("  🆕" if is_new_row else "")
        badge_c = ws3.cell(row=s3_row, column=1, value=badge_val)
        badge_c.font      = Font(bold=True, size=12, color="FFFFFF")
        badge_c.fill      = PatternFill("solid", fgColor="1B5E20" if is_new_row else "1F4E79")
        badge_c.alignment = center
        badge_c.border    = border

        ws3.merge_cells(start_row=s3_row, start_column=2,
                        end_row=s3_row,   end_column=6)
        item_c = ws3.cell(row=s3_row, column=2, value=item_name)
        item_c.font      = Font(bold=True, size=12, color="FFFFFF")
        item_c.fill      = PatternFill("solid", fgColor="2E7D32" if is_new_row else "263238")
        item_c.alignment = Alignment(horizontal="left", vertical="center")
        item_c.border    = border
        ws3.row_dimensions[s3_row].height = 24
        s3_row += 1

        # ── Card Row 2: Drawing | Position | Mark ────────────────
        LABEL_FILL = PatternFill("solid", fgColor="37474F")
        VALUE_FILL = PatternFill("solid", fgColor="546E7A")
        LABEL_FONT = Font(bold=True, size=10, color="B0BEC5")
        VALUE_FONT = Font(bold=True, size=10, color="FFFFFF")

        info_pairs = [
            ("Drawing",  str(curr.get("drawing_number") or "—")),
            ("Position", str(curr.get("position_no")    or "—")),
            ("Mark",     str(curr.get("part_no")         or "—")),
        ]
        col_idx = 1
        for lbl, val in info_pairs:
            lc = ws3.cell(row=s3_row, column=col_idx, value=lbl)
            lc.font = LABEL_FONT; lc.fill = LABEL_FILL
            lc.alignment = center; lc.border = border
            col_idx += 1
            vc = ws3.cell(row=s3_row, column=col_idx, value=val)
            vc.font = VALUE_FONT; vc.fill = VALUE_FILL
            vc.alignment = center; vc.border = border
            col_idx += 1
        ws3.row_dimensions[s3_row].height = 20
        s3_row += 1

        # ── Card Row 3: Sub-headers ───────────────────────────────
        sub_headers = ["Field", "Before", "After", "Change", "% Change", "Status"]
        sub_fills   = [
            PatternFill("solid", fgColor="455A64"),  # Field
            PatternFill("solid", fgColor="BF360C"),  # Before — dark red
            PatternFill("solid", fgColor="1B5E20"),  # After  — dark green
            PatternFill("solid", fgColor="4A148C"),  # Change — purple
            PatternFill("solid", fgColor="0D47A1"),  # % Change — blue
            PatternFill("solid", fgColor="212121"),  # Status — near black
        ]
        for col, (h, fil) in enumerate(zip(sub_headers, sub_fills), 1):
            c = ws3.cell(row=s3_row, column=col, value=h)
            c.font = Font(bold=True, size=11, color="FFFFFF")
            c.fill = fil; c.border = border; c.alignment = center
        ws3.row_dimensions[s3_row].height = 22
        s3_row += 1

        # ── Card Rows 4+: One row per changed field ───────────────
        for f in row_compare_fields:
            if f not in chg_fields:
                continue

            pv = round(float((prev or {}).get(f) or 0), 3) if prev else 0.0
            cv = round(float(curr.get(f) or 0), 3)
            is_int_field = f in ("quantity", "po_required_qty")

            pv_disp   = int(pv) if is_int_field else pv
            cv_disp   = int(cv) if is_int_field else cv
            diff      = round(cv - pv, 3)
            diff_disp = int(diff) if is_int_field else diff
            diff_pfx  = "+" if diff > 0 else ""
            pct       = round((diff / pv * 100), 2) if pv != 0 else 100.0
            diff_clr  = "1B5E20" if diff > 0 else "B71C1C"

            if is_new_row:
                status    = "🆕 New Row"
                pv_disp   = "—"
                pct_disp  = "—"
            else:
                status    = f"{'▲' if diff > 0 else '▼'} {'Increased' if diff > 0 else 'Decreased'}"
                pct_disp  = f"{pct:+.1f}%"

            row_data = [
                # (value, font, fill)
                (row_field_labels.get(f, f),
                 Font(bold=True, size=11, color="37474F"),
                 PatternFill("solid", fgColor="ECEFF1")),

                (pv_disp,
                 Font(bold=True, size=11, color="BF360C"),
                 PatternFill("solid", fgColor="FFCCBC")),

                (cv_disp,
                 Font(bold=True, size=11, color="1B5E20"),
                 PatternFill("solid", fgColor="C8E6C9")),

                (f"{diff_pfx}{diff_disp}",
                 Font(bold=True, size=11, color=diff_clr),
                 PatternFill("solid", fgColor="F3E5F5")),

                (pct_disp,
                 Font(bold=True, size=10, color=diff_clr),
                 PatternFill("solid", fgColor="E8EAF6")),

                (status,
                 Font(bold=True, size=11, color=diff_clr),
                 PatternFill("solid", fgColor="E8F5E9") if diff > 0
                 else PatternFill("solid", fgColor="FFEBEE")),
            ]

            for col, (val, fnt, fil) in enumerate(row_data, 1):
                c = ws3.cell(row=s3_row, column=col, value=val)
                c.font = fnt; c.fill = fil
                c.border = border; c.alignment = center
                if col in [2, 3, 4] and not is_int_field and val != "—":
                    c.number_format = num3

            ws3.row_dimensions[s3_row].height = 22
            s3_row += 1

        # ── Blank spacer between cards ────────────────────────────
        for col in range(1, 7):
            sc = ws3.cell(row=s3_row, column=col, value="")
            sc.fill = PatternFill("solid", fgColor="ECEFF1")
        ws3.row_dimensions[s3_row].height = 10
        s3_row += 1

    # ── No data cases ─────────────────────────────────────────────
    if not all_display_rows:
        ws2.merge_cells(start_row=4, start_column=1, end_row=4, end_column=N2)
        c = ws2.cell(row=4, column=1,
                     value="No drawing detail data found. Please save a snapshot first.")
        c.font = Font(italic=True, size=12, color="888888")
        c.fill = PatternFill("solid", fgColor="F5F5F5")
        c.alignment = center

    if not s3_has_content:
        ws3.merge_cells(start_row=3, start_column=1, end_row=3, end_column=6)
        c = ws3.cell(row=3, column=1, value="✅  No field-level changes detected.")
        c.font = Font(italic=True, size=12, color="2E7D32")
        c.fill = PatternFill("solid", fgColor="E8F5E9")
        c.alignment = center

    # ── Column widths Sheet 2 ─────────────────────────────────────
    s2_widths = [7, 42, 18, 28, 18, 14, 10, 16, 14, 18, 18, 18, 18, 18]
    for i, w in enumerate(s2_widths, 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws3.freeze_panes = "A2"

    stream = BytesIO()
    wb.save(stream); stream.seek(0)
    file_doc = save_file("Compare_Snapshot.xlsx", stream.getvalue(), None, None, is_private=0)
    return file_doc.file_url
    
# ---------------------- Snapshot Save with drawing number -------------


