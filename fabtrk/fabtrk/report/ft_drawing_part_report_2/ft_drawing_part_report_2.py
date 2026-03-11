 
import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 100},
        {"label": "Item", "fieldname": "item_name", "width": 420},
        {"label": "Total Entries", "fieldname": "item_count", "fieldtype": "Int", "width": 110, "align": "center"},
        {"label": "Total Qty", "fieldname": "quantity", "fieldtype": "Int", "width": 85, "align": "center"},
        {"label": "Total Length", "fieldname": "lenght", "fieldtype": "Float", "width": 110, "align": "center"},
        {"label": "Total Width", "fieldname": "width", "fieldtype": "Float", "width": 120, "align": "center"},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 110, "align": "center"},
        {"label": "Details", "fieldname": "view", "fieldtype": "HTML", "width": 130, "align": "center"},
    ]
 
           
    # ---------------- CONDITIONS ----------------
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.name IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("item"):
        conditions += " AND dp.item_id IN %(item)s"
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
        dp.item_id AS item_id,
        rm.computed_name AS item_name,
        COALESCE(CAST(st.sort_key AS UNSIGNED), 9999) AS sort_key,        
        CAST(REGEXP_SUBSTR(rm.computed_name, '[0-9]+') AS UNSIGNED) AS item_sort,        
        COUNT(dp.name) AS item_count,
        SUM(COALESCE(dp.quantity, 0)) AS quantity,
        SUM(COALESCE(dp.lenght, 0)) AS lenght,
        SUM(COALESCE(dp.width, 0)) AS width,
        SUM(COALESCE(dp.total_weight, 0)) AS total_weight
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
    LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
    LEFT JOIN `tabFT Section Type` st ON st.name = rm.stock_rm_type
    WHERE 1=1
        {conditions}
    GROUP BY p.name, dp.item_id, rm.computed_name, st.sort_key
    HAVING 
        dp.item_id IS NOT NULL
        OR (
            dp.item_id IS NULL
            AND NOT EXISTS (
                SELECT 1
                FROM `tabFT Add Drawing` ad2
                INNER JOIN `tabFT Drawing Parts` dp2 ON dp2.drawing_number = ad2.name
                WHERE ad2.project_number = p.name
            )
        )
    ORDER BY p.name, sort_key ASC,item_sort ASC
    """

    data = frappe.db.sql(query, values, as_dict=True) or []
    
    # -------------------------------------------------
    # If no data rows but drawing is selected,
    # show blank row instead of "Nothing to show"
    # -------------------------------------------------

    if not data and filters.get("drawing_number"):
        
        blank_projects = frappe.db.sql("""
            SELECT DISTINCT p.name
            FROM `tabFT Project` p
            LEFT JOIN `tabFT Add Drawing` ad 
                ON ad.project_number = p.name
            WHERE ad.name IN %(drawing_number)s
        """, {
            "drawing_number": tuple(filters.get("drawing_number"))
        }, as_dict=True)

        for proj in blank_projects:
            data.append({
                "project_name": proj.name,
                "item_name": "-",
                "item_count": 0,
                "quantity": 0,
                "lenght": 0,
                "width": 0,
                "total_weight": 0.000,
            })

    for row in data:
        row["item_count"] = row.get("item_count") or 0
        row["quantity"] = row.get("quantity") or 0
        row["lenght"] = row.get("lenght") or 0
        row["width"] = row.get("width") or 0
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
    # total_projects = len({d["project_name"] for d in data if d.get("project_name")})
    # ✅ FIXED: Total Projects (works even if drawing parts = 0)
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

    # Total Drawings
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
    total_weight_parts = sum(d.get("total_weight", 0) for d in data)

    # Project total weight
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

    # ---------------- PO Drawing Summary (FINAL FIX ADDED HERE) ----------------
    po_conditions = ""
    po_values = {}

    if filters.get("project_number"):
        po_conditions += " AND pod.project_number IN %(project_number)s"
        po_values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        po_conditions += """
            AND pod.drawing_number IN %(drawing_number)s
        """
        po_values["drawing_number"] = tuple(filters.get("drawing_number"))

    po_summary = frappe.db.sql(f"""
        SELECT
            COUNT(pod.name) as total_line_items,
            SUM(COALESCE(pod.total_weight,0)) as total_weight
        FROM `tabFT Po Drawing` pod
        WHERE 1=1 {po_conditions}
    """, po_values, as_dict=True)

    total_po_drawings = po_summary[0]["total_line_items"] or 0
    total_weight_po_items = po_summary[0]["total_weight"] or 0

    drawing_balance_for_customer = (project_total_weight or 0) - total_weight_po_items

    # ---------------- FORMAT ----------------
    formatted_project_total_weight = "{:,.3f}".format(project_total_weight)
    formatted_total_weight_po_items = "{:,.3f}".format(total_weight_po_items)
    formatted_total_weight_parts = "{:,.3f}".format(total_weight_parts)
    formatted_drawing_balance_for_customer = "{:,.3f}".format(drawing_balance_for_customer)

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
                        <p>Total Weight of Line Items<br>Assign to Project(Kg)</p>
                        <span>{formatted_total_weight_po_items}</span>
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
                        <p>Total No of Drawing Parts</p>
                        <span>{total_drawing_parts}</span>
                    </div>
                    <div class="section-content-count">
                        <p>Total Weight as per Drawing Parts(Kg)</p>
                        <span>{formatted_total_weight_parts}</span>
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
    return columns, data, None, None, report_summary
    # =====================================================
    # ✅ ADD GRAND TOTAL ROW (After Summary Calculation)
    # =====================================================

    if data:
        grand_total_entries = sum(float(d.get("item_count") or 0) for d in data)
        grand_total_weight = sum(float(d.get("total_weight") or 0) for d in data)
        grand_total_qty = sum(float(d.get("quantity") or 0) for d in data)
        grand_total_length = sum(float(d.get("lenght") or 0) for d in data)
        grand_total_width = sum(float(d.get("width") or 0) for d in data)
    
        data.append({
            "project_name": "TOTAL",
            "item_name": "",
            "item_count": grand_total_entries,
            "quantity": grand_total_qty,
            "lenght": grand_total_length,
            "width": grand_total_width,
            "total_weight": grand_total_weight,
            "view": ""
        })


    return columns, data, None, None, report_summary  

# ---------------- ITEM DETAILS ----------------
@frappe.whitelist()
def get_item_details(project, item, drawing_numbers=None):
    from collections import defaultdict

    conditions = " WHERE p.name = %s AND dp.item_id = %s "
    values = [project, item]

    if drawing_numbers:
        drawing_numbers = frappe.parse_json(drawing_numbers)
        if drawing_numbers:
            conditions += " AND ad.name IN %s "
            values.append(tuple(drawing_numbers))

    rows = frappe.db.sql(f"""
        SELECT
            p.name AS project_number,
            pod.po_serial_no AS po_serial_no,
            ad.drawing_number AS drawing_number,
            dp.position_no AS position_no,
            dp.part_no AS part_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        {conditions}
        ORDER BY 
            COALESCE(CAST(pod.po_serial_no AS UNSIGNED),0) ASC,
            ad.drawing_number ASC
    """, tuple(values), as_dict=True)

    # ---------------- GROUP SAME ROWS ----------------
    grouped = defaultdict(lambda: {
        "project_number": "",
        "po_serial_no": "",
        "drawing_number": "",
        "position_no": "",
        "part_no": "",
        "quantity": 0,
        "lenght": 0,
        "width": 0,
        "single_weight": 0,
        "total_weight": 0,
        "entry_count": 0
    })

    for d in rows:
        key = (
            d.get("project_number"),
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
        grouped[key]["po_serial_no"] = d.get("po_serial_no")
        grouped[key]["drawing_number"] = d.get("drawing_number")
        grouped[key]["position_no"] = d.get("position_no")
        grouped[key]["part_no"]        = d.get("part_no") 
        grouped[key]["quantity"] = d.get("quantity")
        grouped[key]["lenght"] = d.get("lenght")
        grouped[key]["width"] = d.get("width")
        grouped[key]["single_weight"] = d.get("single_weight")
        grouped[key]["total_weight"] = d.get("total_weight")

        grouped[key]["entry_count"] += 1

    rows = list(grouped.values())

    # ---------------- TOTAL CALCULATION ----------------
    grand_total_weight = 0
    grand_total_qty = 0
    grand_total_length = 0
    grand_total_width = 0

    serial_no = 1

    for d in rows:
        d["serial_no"] = serial_no
        serial_no += 1

        grand_total_weight += d.get("total_weight") or 0
        grand_total_qty += d.get("quantity") or 0
        grand_total_length += d.get("lenght") or 0
        grand_total_width += d.get("width") or 0

    # ---------------- TOTAL ROW ----------------
    rows.append({
        "serial_no": "",
        "project_number": "<b>Total</b>",
        "po_serial_no": "",
        "drawing_number": "",
        "position_no": "",
        "part_no": "",
        "entry_count": "",
        "quantity": grand_total_qty,
        "lenght": grand_total_length,
        "width": grand_total_width,
        "single_weight": "",
        "total_weight": grand_total_weight
    })

    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    return {"item_name": item_name, "data": rows}


# # ---------------- EXCEL EXPORT ----------------
# Only show Summary Details 
@frappe.whitelist()
def download_item_excel(filters):

    import frappe
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from io import BytesIO

    filters = frappe.parse_json(filters)

    conditions = ""
    values = {}

    projects = filters.get("project_number") or []

    if projects:
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(projects)

    data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            IFNULL(rm.computed_name,'-') as item,
            COUNT(dp.name) as total_entries,
            IFNULL(SUM(dp.quantity),0) as total_qty,
            IFNULL(SUM(dp.lenght),0) as total_length,
            IFNULL(SUM(dp.width),0) as total_width,
            IFNULL(SUM(dp.total_weight),0) as total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad 
            ON ad.project_number = p.name
        LEFT JOIN `tabFT Drawing Parts` dp 
            ON dp.drawing_number = ad.name
        LEFT JOIN `tabFT Stock RM List` rm 
            ON rm.name = dp.item_id
        WHERE 1=1 {conditions}
        GROUP BY p.name, rm.computed_name
        ORDER BY p.name
    """, values, as_dict=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary Report"

    headers = [
        "Sr No",
        "Project",
        "Item",
        "Total Entries",
        "Total Qty",
        "Total Length",
        "Total Width",
        "Total Weight"
    ]

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    center = Alignment(horizontal="center", vertical="center")
    left = Alignment(horizontal="left", vertical="center")

    # ===== Dynamic Heading =====

    if projects:
        heading_text = "Item Wise Summary Data for Projects: " + ", ".join(projects)
    else:
        heading_text = "All Item Wise Summary Data"

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)

    heading_cell = ws.cell(row=1, column=1, value=heading_text)
    heading_cell.font = Font(bold=True, size=16, color="FFFFFF")
    heading_cell.alignment = center
    heading_cell.fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

    row_no = 3

    # ===== Table Header =====

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=row_no, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center

    row_no += 1
    sr = 1

    total_entries = 0
    total_qty = 0
    total_length = 0
    total_width = 0
    total_weight = 0

    # ===== Data Rows =====

    for d in data:

        entries = d.get("total_entries") or 0
        qty = d.get("total_qty") or 0
        length = d.get("total_length") or 0
        width = d.get("total_width") or 0
        weight = d.get("total_weight") or 0

        row_vals = [
            sr,
            d.get("project"),
            d.get("item"),
            entries,
            qty,
            length,
            width,
            weight
        ]

        for col, val in enumerate(row_vals, 1):

            cell = ws.cell(row=row_no, column=col, value=val)
            cell.border = border
            cell.alignment = left if col in [2,3] else center

            if col in [6,7,8]:
                cell.number_format = '#,##0.000'

        total_entries += entries
        total_qty += qty
        total_length += length
        total_width += width
        total_weight += weight

        row_no += 1
        sr += 1

    # ===== Total Row =====

    total_font = Font(bold=True, color="FFFFFF")
    total_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    totals = [
        "Total",
        "",
        "",
        total_entries,
        total_qty,
        total_length,
        total_width,
        total_weight
    ]

    for col, val in enumerate(totals, 1):

        cell = ws.cell(row=row_no, column=col, value=val)
        cell.font = total_font
        cell.fill = total_fill
        cell.border = border
        cell.alignment = left if col == 1 else center

        if col in [6,7,8]:
            cell.number_format = '#,##0.000'

    # ===== Column Width =====

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 45
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 15
    ws.column_dimensions["G"].width = 15
    ws.column_dimensions["H"].width = 18

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response["filename"] = "Summary_Report.xlsx"
    frappe.response["filecontent"] = file_stream.getvalue()
    frappe.response["type"] = "binary"

# three sheet Excel
@frappe.whitelist()
def get_all_details_for_export(filters):

    import frappe
    import openpyxl
    from io import BytesIO
    from frappe.utils.file_manager import save_file
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    filters = frappe.parse_json(filters)

    conditions=""
    values={}

    if filters.get("project_number"):
        conditions+=" AND p.name IN %(project_number)s"
        values["project_number"]=tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions+=" AND ad.name IN %(drawing_number)s"
        values["drawing_number"]=tuple(filters.get("drawing_number"))

    # -----------------------------
    # SUMMARY DATA
    # -----------------------------

    # ---------- GET ALL PROJECTS ----------
    projects = frappe.db.sql("""
        SELECT name
        FROM `tabFT Project`
        ORDER BY name
    """, as_dict=1)

    # ---------- SUMMARY DATA ----------
    summary_data = frappe.db.sql("""
    SELECT
        p.name as project,
        COALESCE(rm.computed_name,'-') as item,
        COUNT(dp.name) as total_entries,
        IFNULL(SUM(dp.quantity),0) as total_qty,
        IFNULL(SUM(dp.lenght),0) as total_length,
        IFNULL(SUM(dp.width),0) as total_width,
        IFNULL(SUM(dp.total_weight),0) as total_weight
    FROM `tabFT Project` p
    LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
    LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
    GROUP BY p.name, item
    ORDER BY p.name
    """, as_dict=1)

    # -----------------------------
    # DETAIL DATA
    # -----------------------------

    detail_data = frappe.db.sql(f"""
        SELECT
            COALESCE(p.name,'No Project') as project,
            rm.computed_name as item_name,
            pod.po_serial_no,
            ad.drawing_number,
            dp.position_no,
            IFNULL(dp.quantity,0) as quantity,
            IFNULL(dp.lenght,0) as lenght,
            IFNULL(dp.width,0) as width,
            IFNULL(dp.single_weight,0) as single_weight,
            IFNULL(dp.total_weight,0) as total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
        LEFT JOIN (
            SELECT drawing_number,MIN(po_serial_no) as po_serial_no
            FROM `tabFT Po Drawing`
            GROUP BY drawing_number
        ) pod ON pod.drawing_number=ad.name
        WHERE 1=1 {conditions}
        ORDER BY project,ad.drawing_number
    """,values,as_dict=True)

    # ---------- MAP PROJECT DATA ----------
    summary_map = {}

    for d in summary_data:
        summary_map.setdefault(d.project, []).append(d)

    # -----------------------------
    # PO DRAWING DATA
    # -----------------------------

    po_drawing_data = frappe.db.sql("""
        SELECT
            COALESCE(pod.project_number,'No Project') as project,
            ad.drawing_number,
            pod.po_serial_no,
            pod.po_description,
            IFNULL(pod.unit_weight,0) as unit_weight,
            IFNULL(pod.required_qty,0) as required_qty,
            IFNULL(pod.total_weight,0) as total_weight
        FROM `tabFT Po Drawing` pod
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = pod.drawing_number
        ORDER BY project
    """,as_dict=True)

    # -----------------------------
    # EXCEL STYLE
    # -----------------------------

    wb=openpyxl.Workbook()

    header_font=Font(bold=True,color="FFFFFF")
    header_fill=PatternFill("solid",fgColor="2F75B5")

    title_font=Font(size=16,bold=True,color="FFFFFF")
    title_fill=PatternFill("solid",fgColor="1F4E79")

    total_font=Font(bold=True,color="FFFFFF")
    total_fill=PatternFill("solid",fgColor="2F75B5")

    thin=Side(style="thin")
    border=Border(left=thin,right=thin,top=thin,bottom=thin)

    center=Alignment(horizontal="center",vertical="center")
    left=Alignment(horizontal="left",vertical="center")

    num="#,##0.000"

    # ======================================================
    # SHEET 1 : DRAWING PO LIST
    # ======================================================

    ws1=wb.active
    ws1.title="Drawing PO List"

    headers=["Sr No","Project Number","Drawing Number","Po Serial No",
             "PO Description","Unit Weight","Required Qty","Total Weight"]

    ws1.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(headers))
    title=ws1.cell(row=1,column=1,value="PO Summary")
    title.font=title_font
    title.fill=title_fill
    title.alignment=center

    for col,h in enumerate(headers,1):
        c=ws1.cell(row=3,column=col,value=h)
        c.font=header_font
        c.fill=header_fill
        c.border=border
        c.alignment=center

    ws1.freeze_panes="A4"

    row=4
    sr=1

    t_unit=0
    t_qty=0
    t_weight=0

    for d in po_drawing_data:

        vals=[sr,d.project,d.drawing_number,d.po_serial_no,
              d.po_description,d.unit_weight,d.required_qty,d.total_weight]

        for col,val in enumerate(vals,1):

            c=ws1.cell(row=row,column=col,value=val)
            c.border=border
            c.alignment=center

            if col>=6:
                c.number_format=num

        t_unit+=d.unit_weight or 0
        t_qty+=d.required_qty or 0
        t_weight+=d.total_weight or 0

        row+=1
        sr+=1

    total_row=["Total","","","","",t_unit,t_qty,t_weight]

    for col,val in enumerate(total_row,1):

        c=ws1.cell(row=row,column=col,value=val)
        c.font=total_font
        c.fill=total_fill
        c.border=border
        c.alignment=center

        if col>=6:
            c.number_format=num

    widths=[8,20,30,15,40,18,18,20]

    for i,w in enumerate(widths,1):
        ws1.column_dimensions[get_column_letter(i)].width=w


    # ======================================================
    # SHEET 2 : SUMMARY
    # ======================================================

    ws2=wb.create_sheet("Summary")

    headers=["Sr No","Project","Item","Entries","Qty","Length","Width","Total Weight"]

    ws2.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(headers))
    title=ws2.cell(row=1,column=1,value="Project Item Summary")
    title.font=title_font
    title.fill=title_fill
    title.alignment=center

    for col,h in enumerate(headers,1):
        c=ws2.cell(row=3,column=col,value=h)
        c.font=header_font
        c.fill=header_fill
        c.border=border
        c.alignment=center

    ws2.freeze_panes="A4"

    row=4
    sr=1

    t_entries=t_qty=t_len=t_wid=t_wt=0

    for d in summary_data:

        vals=[sr,d.project,d.item,d.total_entries,
              d.total_qty,d.total_length,d.total_width,d.total_weight]

        for col,val in enumerate(vals,1):

            c=ws2.cell(row=row,column=col,value=val)
            c.border=border
            c.alignment=left if col in [2,3] else center

            if col>=5:
                c.number_format=num

        t_entries+=d.total_entries or 0
        t_qty+=d.total_qty or 0
        t_len+=d.total_length or 0
        t_wid+=d.total_width or 0
        t_wt+=d.total_weight or 0

        row+=1
        sr+=1

    totals=["Total","","",t_entries,t_qty,t_len,t_wid,t_wt]

    for col,val in enumerate(totals,1):

        c=ws2.cell(row=row,column=col,value=val)
        c.font=total_font
        c.fill=total_fill
        c.border=border
        c.alignment=center
        if col>=5:
            c.number_format=num

    widths=[8,20,45,15,15,18,18,20]

    for i,w in enumerate(widths,1):
        ws2.column_dimensions[get_column_letter(i)].width=w

    
    # ======================================================
    # SHEET 3 : DETAILS
    # ======================================================

    ws3=wb.create_sheet("Details")

    headers=["Sr No","Project","Item","PO Serial","Drawing",
             "Position","Qty","Length","Width","Single Weight","Total Weight"]

    ws3.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(headers))
    title=ws3.cell(row=1,column=1,value="Item Wise Summary")
    title.font=title_font
    title.fill=title_fill
    title.alignment=center

    for col,h in enumerate(headers,1):

        c=ws3.cell(row=3,column=col,value=h)
        c.font=header_font
        c.fill=header_fill
        c.border=border
        c.alignment=center

    ws3.freeze_panes="A4"

    row=4
    sr=1

    t_qty=t_len=t_wid=t_swt=t_twt=0

    for d in detail_data:

        vals=[sr,d.project,d.item_name,d.po_serial_no,
              d.drawing_number,d.position_no,d.quantity,
              d.lenght,d.width,d.single_weight,d.total_weight]

        for col,val in enumerate(vals,1):

            c=ws3.cell(row=row,column=col,value=val)
            c.border=border
            c.alignment=left if col in [2,3] else center

            if col>=7:
                c.number_format=num

        t_qty+=d.quantity or 0
        t_len+=d.lenght or 0
        t_wid+=d.width or 0
        t_swt+=d.single_weight or 0
        t_twt+=d.total_weight or 0

        row+=1
        sr+=1

    total_row=["Total","","","","","",t_qty,t_len,t_wid,t_swt,t_twt]

    for col,val in enumerate(total_row,1):

        c=ws3.cell(row=row,column=col,value=val)
        c.font=total_font
        c.fill=total_fill
        c.border=border
        c.alignment=center

        if col>=7:
            c.number_format=num

    widths=[8,20,40,15,30,15,12,18,18,18,20]

    for i,w in enumerate(widths,1):
        ws3.column_dimensions[get_column_letter(i)].width=w


    # -----------------------------
    # SAVE FILE
    # -----------------------------

    stream=BytesIO()
    wb.save(stream)
    stream.seek(0)

    file_doc=save_file(
        "FT_Drawing_Report.xlsx",
        stream.getvalue(),
        None,
        None,
        is_private=0
    )

    return file_doc.file_url

# item details EXCEL    
@frappe.whitelist()
def download_item_details_excel(filters):
    import frappe
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from collections import defaultdict

    filters = frappe.parse_json(filters)

    item = filters.get("item")
    project = filters.get("project")

    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    data = frappe.db.sql("""
        SELECT
            p.name as project_number,
            pod.po_serial_no,
            ad.drawing_number as drawing,
            dp.position_no,
            dp.part_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        WHERE dp.item_id = %(item)s
        AND ad.project_number = %(project)s
        ORDER BY 
            CAST(pod.po_serial_no AS UNSIGNED) ASC,
            ad.drawing_number ASC
    """, {"item": item, "project": project}, as_dict=True)

    # -------- GROUP SAME ROWS --------
    grouped = defaultdict(lambda: {
        "project_number": "",
        "po_serial_no": "",
        "drawing": "",
        "position_no": "",
        "part_no": "",
        "quantity": 0,
        "lenght": 0,
        "width": 0,
        "single_weight": 0,
        "total_weight": 0,
        "entry_count": 0
    })

    for d in data:
        key = (
            d.get("project_number"),
            d.get("po_serial_no"),
            d.get("drawing"),
            d.get("position_no"),
            d.get("part_no"),
            d.get("quantity"),
            d.get("lenght"),
            d.get("width"),
            d.get("single_weight"),
            d.get("total_weight"),
        )

        grouped[key]["project_number"] = d.get("project_number")
        grouped[key]["po_serial_no"] = d.get("po_serial_no")
        grouped[key]["drawing"] = d.get("drawing")
        grouped[key]["position_no"] = d.get("position_no")
        grouped[key]["part_no"] = d.get("part_no")
        grouped[key]["quantity"] = d.get("quantity")
        grouped[key]["lenght"] = d.get("lenght")
        grouped[key]["width"] = d.get("width")
        grouped[key]["single_weight"] = d.get("single_weight")
        grouped[key]["total_weight"] = d.get("total_weight")
        grouped[key]["entry_count"] += 1

    data = list(grouped.values())

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Item Details"
    
    # -------- ITEM HEADING --------
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11)

    title_cell = ws.cell(row=1, column=1)
    title_cell.value = f"Item Details - {item_name}"
    title_cell.font = Font(bold=True, size=16)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")


    headers = [
        "Sr No",
        "Project No",
        "Po Serial No",
        "Drawing",
        "Position No",
        "Part No",
        "Entry Count",
        "Qty",
        "Length",
        "Width",
        "Single Weight",
        "Total Weight"
    ]

    # -------- STYLES --------
    header_font = Font(bold=True, size=13, color="FFFFFF")
    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    data_font = Font(size=12)
    total_font = Font(bold=True, size=14)
    total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

    thin = Side(style="thin")
    center = Alignment(horizontal="center", vertical="center")
    full_border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # -------- HEADER --------
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = full_border
        cell.alignment = center

    row_no = 3
    serial_no = 1

    total_qty = total_length = total_width = total_weight = 0

    # -------- DATA ROWS --------
    for d in data:

        row_values = [
            serial_no,
            d.get("project_number"),
            d.get("po_serial_no"),
            d.get("drawing"),
            d.get("position_no"),
            d.get("part_no"),
            d.get("entry_count"),
            d.get("quantity"),
            d.get("lenght"),
            d.get("width"),
            d.get("single_weight"),
            d.get("total_weight"),
        ]

        total_qty += d.get("quantity") or 0
        total_length += d.get("lenght") or 0
        total_width += d.get("width") or 0
        total_weight += d.get("total_weight") or 0

        for col, val in enumerate(row_values, 1):
            cell = ws.cell(row=row_no, column=col, value=val)
            cell.font = data_font
            cell.border = full_border
            cell.alignment = center
            
            # Formatting for Single Weight (column 10)
            if col == 10:
                cell.number_format = '#,##0.000'

            # Formatting for Total Weight (column 11)
            if col == 11:
                cell.number_format = '#,##0.000'

        row_no += 1
        serial_no += 1

    # -------- TOTAL ROW --------
    for col in range(1, 13):
        cell = ws.cell(row=row_no, column=col)
        cell.fill = total_fill
        cell.alignment = center

        if col == 1:
            cell.value = "Total"
            cell.font = total_font
            cell.border = Border(left=thin, top=thin, bottom=thin)

        elif col == 8:
            cell.value = total_qty
            cell.font = total_font
            cell.border = Border(left=thin, top=thin, bottom=thin)

        elif col == 9:
            cell.value = total_length
            cell.font = total_font
            cell.border = Border(left=thin, top=thin, bottom=thin)

        elif col == 10:
            cell.value = total_width
            cell.font = total_font
            cell.border = Border(left=thin, top=thin, bottom=thin)

        elif col == 12:
            cell.value = total_weight
            cell.font = total_font
            cell.border = Border(right=thin, left=thin, top=thin, bottom=thin)
            cell.number_format = '#,##0.000'  

        else:
            cell.border = Border(left=thin, top=thin, bottom=thin)

    # -------- COLUMN WIDTH --------
    widths = [8, 18, 15, 30, 15, 12, 10, 12, 12, 12, 16, 16]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # -------- SAVE --------
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response['filename'] = "Item_Details.xlsx"
    frappe.response['filecontent'] = file_stream.getvalue()
    frappe.response['type'] = 'download'   
  


# item detail export import button

# ROW-LEVEL IMPORT
@frappe.whitelist()
def import_row_data(project, drawing_number, position_no, item):
    """
    Ye function ek specific row ka data import karta hai.
    Aap yahan apna actual import logic likhein.
    Abhi yeh ek placeholder hai jo success return karta hai.
    """
    try:
        # ── Yahan apna import logic likho ──
        # Example: kisi aur doctype mein data copy karna, status update karna, etc.

        existing = frappe.db.get_value(
            "FT Drawing Parts",
            {
                "drawing_number": drawing_number,
                "position_no": position_no,
                "item_id": item
            },
            "name"
        )

        if not existing:
            return {"status": "error", "msg": "Row not found in Drawing Parts"}

        # TODO: Yahan apna actual import action karo
        # frappe.db.set_value("FT Drawing Parts", existing, "some_field", some_value)
        # frappe.db.commit()

        return {
            "status": "success",
            "msg": f"Import successful for Drawing: {drawing_number}, Position: {position_no}"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "import_row_data Error")
        return {"status": "error", "msg": str(e)}


# ROW-LEVEL EXPORT (Single Row Excel Download)
@frappe.whitelist()
def export_row_excel(project, drawing_number, position_no, item):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    data = frappe.db.sql("""
        SELECT
            p.name          AS project_number,
            pod.po_serial_no,
            ad.drawing_number,
            dp.position_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad  ON ad.name  = dp.drawing_number
        LEFT JOIN `tabFT Project`     p   ON p.name   = ad.project_number
        LEFT JOIN `tabFT Po Drawing`  pod
               ON pod.project_number = p.name
              AND pod.drawing_number  = ad.name
        WHERE dp.item_id        = %(item)s
          AND ad.project_number = %(project)s
          AND ad.drawing_number = %(drawing_number)s
          AND dp.position_no    = %(position_no)s
        ORDER BY CAST(pod.po_serial_no AS UNSIGNED) ASC
    """, {
        "item": item,
        "project": project,
        "drawing_number": drawing_number,
        "position_no": position_no
    }, as_dict=True)

    # ── Workbook setup ──
    wb  = openpyxl.Workbook()
    ws  = wb.active
    ws.title = "Row Export"

    thin         = Side(style="thin")
    border       = Border(left=thin, right=thin, top=thin, bottom=thin)
    center       = Alignment(horizontal="center", vertical="center")
    header_font  = Font(bold=True, size=12, color="FFFFFF")
    header_fill  = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    total_font   = Font(bold=True, size=12, color="FFFFFF")
    total_fill   = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    # ── Title row ──
    headers = ["Sr No", "Project No", "Po Serial No", "Drawing",
               "Position No", "Qty", "Length", "Width", "Single Weight", "Total Weight"]

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell            = ws.cell(row=1, column=1, value=f"Row Export — {item_name}")
    title_cell.font       = Font(bold=True, size=14)
    title_cell.alignment  = center
    ws.row_dimensions[1].height = 22

    # ── Header row ──
    for col, h in enumerate(headers, 1):
        cell           = ws.cell(row=2, column=col, value=h)
        cell.font      = header_font
        cell.fill      = header_fill
        cell.border    = border
        cell.alignment = center

    # ── Data rows ──
    t_qty = t_len = t_wid = t_weight = 0
    for sr, d in enumerate(data, 1):
        qty    = d.get("quantity")      or 0
        length = d.get("lenght")        or 0
        width  = d.get("width")         or 0
        sw     = d.get("single_weight") or 0
        weight = d.get("total_weight")  or 0

        vals = [sr,
                d.get("project_number"), d.get("po_serial_no"),
                d.get("drawing_number"), d.get("position_no"),
                qty, length, width, sw, weight]

        for col, val in enumerate(vals, 1):
            cell               = ws.cell(row=sr + 2, column=col, value=val)
            cell.border        = border
            cell.alignment     = center
            cell.font          = Font(size=11)
            if col in [9, 10]:
                cell.number_format = '#,##0.000'

        t_qty    += qty
        t_len    += length
        t_wid    += width
        t_weight += weight

    # ── Total row ──
    total_row = len(data) + 3
    total_vals = ["Total", "", "", "", "", t_qty, t_len, t_wid, "", t_weight]
    for col, val in enumerate(total_vals, 1):
        cell               = ws.cell(row=total_row, column=col, value=val)
        cell.font          = total_font
        cell.fill          = total_fill
        cell.border        = border
        cell.alignment     = center
        if col in [9, 10]:
            cell.number_format = '#,##0.000'

    # ── Column widths ──
    for col, w in zip(range(1, 11), [8, 18, 15, 30, 15, 10, 12, 12, 16, 16]):
        ws.column_dimensions[get_column_letter(col)].width = w

    # ── Stream response ──
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response["filename"]    = f"Row_Export_{drawing_number}_{position_no}.xlsx"
    frappe.response["filecontent"] = file_stream.getvalue()
    frappe.response["type"]        = "binary"
    
    
