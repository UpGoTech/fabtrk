 
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
# The above function is the initial version for exporting details, but we will enhance it to create a well-formatted Excel file with separate sheets for summary and details, including styling and better organization of data.
# @frappe.whitelist()
# def get_all_details_for_export(filters):
#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
#     from openpyxl.utils import get_column_letter
#     from io import BytesIO
#     from frappe.utils.file_manager import save_file

#     filters = frappe.parse_json(filters)
#     conditions = ""
#     values = {}

#     if filters.get("project_number"):
#         conditions += " AND p.name IN %(project_number)s"
#         values["project_number"] = tuple(filters.get("project_number"))

#     if filters.get("drawing_number"):
#         conditions += " AND ad.drawing_number IN %(drawing_number)s"
#         values["drawing_number"] = tuple(filters.get("drawing_number"))

#     if filters.get("item"):
#         conditions += " AND dp.item_id IN %(item)s"
#         values["item"] = tuple(filters.get("item"))

#     # ---------------- DETAIL DATA ----------------
#     detail_data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item_name,
#             ad.drawing_number,
#             dp.position_no,
#             dp.quantity,
#             dp.lenght,
#             dp.width,
#             dp.single_weight,
#             dp.total_weight
#         FROM `tabFT Drawing Parts` dp        
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
#         WHERE 1=1 {conditions}
#         ORDER BY p.name, ad.drawing_number
#     """, values, as_dict=True)

#     # ---------------- SUMMARY DATA ----------------
#     summary_data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item_name,
#             COUNT(dp.name) as total_entries,
#             SUM(dp.total_weight) as total_weight
#         FROM `tabFT Drawing Parts` dp
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
#         WHERE 1=1 {conditions}
#         GROUP BY p.name, rm.computed_name
#         ORDER BY p.name
#     """, values, as_dict=True)
    
#     wb = openpyxl.Workbook()

#     header_font = Font(bold=True, color="FFFFFF")
#     total_font = Font(bold=True, size=12)

#     header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
#     total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     # ================= SUMMARY SHEET =================
#     ws1 = wb.active
#     ws1.title = "Summary"

#     summary_headers = ["Project", "Item", "Total Entries", "Total Weight"]

#     for col, header in enumerate(summary_headers, 1):
#         cell = ws1.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border

#     row_no = 2
#     grand_total_summary = 0

#     for d in summary_data:
#         values_row = [
#             d.get("project"),
#             d.get("item_name"),
#             d.get("total_entries"),
#             d.get("total_weight"),
#         ]

#         grand_total_summary += d.get("total_weight") or 0

#         for col, value in enumerate(values_row, 1):
#             cell = ws1.cell(row=row_no, column=col, value=value)
#             cell.border = thin_border
#         row_no += 1

#     # ADD GRAND TOTAL ROW (Summary)
#     total_row = row_no

#     ws1.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=3)
#     total_label = ws1.cell(row=total_row, column=1, value="Total")
#     total_label.font = total_font
#     total_label.fill = total_fill
#     total_label.border = thin_border

#     total_value = ws1.cell(row=total_row, column=4, value=grand_total_summary)
#     total_value.font = total_font
#     total_value.fill = total_fill
#     total_value.border = thin_border

#     # Apply border to merged area
#     for col in range(1, 5):
#         ws1.cell(row=total_row, column=col).border = thin_border

#     ws1.column_dimensions["A"].width = 20
#     ws1.column_dimensions["B"].width = 40
#     ws1.column_dimensions["C"].width = 18
#     ws1.column_dimensions["D"].width = 18


#     # ================= DETAIL SHEET =================
#     ws2 = wb.create_sheet("Details")

#     detail_headers = [
#         "Project",
#         "Item",
#         "Drawing",
#         "Position No",
#         "Qty",
#         "Length",
#         "Width",
#         "Single Weight",
#         "Total Weight"
#     ]

#     for col, header in enumerate(detail_headers, 1):
#         cell = ws2.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border

#     row_no = 2
#     grand_total_detail = 0

#     for d in detail_data:
#         values_row = [
#             d.get("project"),
#             d.get("item_name"),
#             d.get("drawing_number"),
#             d.get("position_no"),
#             d.get("quantity"),
#             d.get("lenght"),
#             d.get("width"),
#             d.get("single_weight"),
#             d.get("total_weight"),
#         ]

#         grand_total_detail += d.get("total_weight") or 0

#         for col, value in enumerate(values_row, 1):
#             cell = ws2.cell(row=row_no, column=col, value=value)
#             cell.border = thin_border
#         row_no += 1

#     # ADD GRAND TOTAL ROW (Details)
#     total_row = row_no

#     ws2.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=8)
#     total_label = ws2.cell(row=total_row, column=1, value="Total")
#     total_label.font = total_font
#     total_label.fill = total_fill
#     total_label.border = thin_border

#     total_value = ws2.cell(row=total_row, column=9, value=grand_total_detail)
#     total_value.font = total_font
#     total_value.fill = total_fill
#     total_value.border = thin_border

#     for col in range(1, 10):
#         ws2.cell(row=total_row, column=col).border = thin_border

#     ws2.column_dimensions["A"].width = 20
#     ws2.column_dimensions["B"].width = 40
#     ws2.column_dimensions["C"].width = 18
#     ws2.column_dimensions["D"].width = 18
#     ws2.column_dimensions["E"].width = 10
#     ws2.column_dimensions["F"].width = 10
#     ws2.column_dimensions["G"].width = 10
#     ws2.column_dimensions["H"].width = 15
#     ws2.column_dimensions["I"].width = 15

#     # ---------------- SAVE FILE ----------------
#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     file_doc = save_file(
#         "FT_Drawing_Part.xlsx",
#         file_stream.getvalue(),
#         None,
#         None,
#         is_private=0
#     )

#     return file_doc.file_url


@frappe.whitelist()
def get_all_details_for_export(filters):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from frappe.utils.file_manager import save_file
    from collections import defaultdict

    filters = frappe.parse_json(filters)
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

    # ---------------- SUMMARY DATA ----------------
    summary_data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item_name,
            COUNT(dp.name) as total_entries,
            IFNULL(SUM(dp.quantity), 0) as total_qty,
            IFNULL(SUM(dp.lenght), 0) as total_length,
            IFNULL(SUM(dp.width), 0) as total_width,
            IFNULL(SUM(dp.total_weight), 0) as total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
        WHERE 1=1 {conditions}
        GROUP BY p.name, rm.computed_name
        ORDER BY p.name
    """, values, as_dict=True)

    # ---------------- DETAIL DATA ----------------
    detail_data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item_name,
            pod.po_serial_no,
            ad.drawing_number,
            dp.position_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
        LEFT JOIN `tabFT Po Drawing` pod
            ON pod.project_number = p.name
            AND pod.drawing_number = ad.name
        WHERE 1=1 {conditions}
        ORDER BY p.name, rm.computed_name,
            CAST(pod.po_serial_no AS UNSIGNED) ASC,
            ad.drawing_number ASC
    """, values, as_dict=True)

    # ---------------- GROUP DETAIL ROWS ----------------
    grouped_detail = defaultdict(lambda: {
        "project": "", "item_name": "", "po_serial_no": "",
        "drawing_number": "", "position_no": "", "quantity": 0,
        "lenght": 0, "width": 0, "single_weight": 0,
        "total_weight": 0, "entry_count": 0
    })

    for d in detail_data:
        key = (
            d.get("project"), d.get("item_name"),
            d.get("po_serial_no"), d.get("drawing_number"),
            d.get("position_no"), d.get("quantity"),
            d.get("lenght"), d.get("width"),
            d.get("single_weight"), d.get("total_weight"),
        )
        grouped_detail[key]["project"]        = d.get("project")
        grouped_detail[key]["item_name"]      = d.get("item_name")
        grouped_detail[key]["po_serial_no"]   = d.get("po_serial_no")
        grouped_detail[key]["drawing_number"] = d.get("drawing_number")
        grouped_detail[key]["position_no"]    = d.get("position_no")
        grouped_detail[key]["quantity"]       = d.get("quantity")
        grouped_detail[key]["lenght"]         = d.get("lenght")
        grouped_detail[key]["width"]          = d.get("width")
        grouped_detail[key]["single_weight"]  = d.get("single_weight")
        grouped_detail[key]["total_weight"]   = d.get("total_weight")
        grouped_detail[key]["entry_count"]    += 1

    detail_rows = list(grouped_detail.values())

    # ============================================================
    # WORKBOOK & STYLES
    # ============================================================
    wb = openpyxl.Workbook()

    header_font     = Font(bold=True, size=12, color="FFFFFF")
    header_fill     = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    proj_total_font = Font(bold=True, size=11, color="FFFFFF")
    proj_total_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    data_font       = Font(size=11)
    total_font      = Font(bold=True, size=12)
    total_fill      = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

    thin        = Side(style="thin")
    thin_border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align   = Alignment(horizontal="left",   vertical="center")

    # ============================================================
    # SHEET 1 — Summary
    # ============================================================
    ws1 = wb.active
    ws1.title = "Summary"

    s1_headers    = ["Sr No", "Project", "Item", "Total Entries", "Total Qty", "Total Length", "Total Width", "Total Weight"]
    TOTAL_COLS_S1 = len(s1_headers)

    project_groups = defaultdict(list)
    for d in summary_data:
        project_groups[d.get("project") or "Unknown"].append(d)

    row_no = 1

    for project_name, rows in project_groups.items():

        # Project heading — no background, bold blue font
        ws1.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=TOTAL_COLS_S1)
        hc              = ws1.cell(row=row_no, column=1, value=f"{project_name}  —  All Items Data")
        hc.font         = Font(bold=True, size=15, color="1F4E79")
        hc.alignment    = left_align
        ws1.row_dimensions[row_no].height = 24
        row_no += 1

        # Blank gap row
        row_no += 1

        # Column headers
        for col, header in enumerate(s1_headers, 1):
            cell           = ws1.cell(row=row_no, column=col, value=header)
            cell.font      = header_font
            cell.fill      = header_fill
            cell.border    = thin_border
            cell.alignment = center_align
        ws1.row_dimensions[row_no].height = 18
        row_no += 1

        # Data rows
        proj_entries = proj_qty = proj_length = proj_width = proj_weight = 0
        sr = 1

        for d in rows:
            entries = d.get("total_entries") or 0
            qty     = d.get("total_qty")     or 0
            length  = d.get("total_length")  or 0
            width   = d.get("total_width")   or 0
            weight  = d.get("total_weight")  or 0

            for col, val in enumerate([sr, d.get("project") or "-", d.get("item_name") or "-",
                                        entries, qty, length, width, weight], 1):
                cell           = ws1.cell(row=row_no, column=col, value=val)
                cell.border    = thin_border
                cell.alignment = left_align if col in [2, 3] else center_align
                cell.font      = data_font

            proj_entries += entries; proj_qty    += qty
            proj_length  += length;  proj_width  += width; proj_weight += weight
            row_no += 1; sr += 1

        # Project total row
        ws1.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=3)
        pt           = ws1.cell(row=row_no, column=1, value="Total")
        pt.font      = proj_total_font
        pt.fill      = proj_total_fill
        pt.alignment = left_align
        pt.border    = thin_border

        for col, val in zip(range(4, 9), [proj_entries, proj_qty, proj_length, proj_width, proj_weight]):
            cell           = ws1.cell(row=row_no, column=col, value=val)
            cell.font      = proj_total_font
            cell.fill      = proj_total_fill
            cell.alignment = center_align
            cell.border    = thin_border

        ws1.row_dimensions[row_no].height = 18
        row_no += 2  # blank row between projects

    for col, w in zip("ABCDEFGH", [8, 18, 45, 15, 12, 15, 15, 18]):
        ws1.column_dimensions[col].width = w

    # ============================================================
    # SHEET 2 — Details
    # ============================================================
    ws2 = wb.create_sheet("Details")

    s2_headers    = [
        "Sr No", "Project", "Item", "Po Serial No", "Drawing",
        "Position No", "Entry Count", "Qty", "Length", "Width",
        "Single Weight", "Total Weight"
    ]
    TOTAL_COLS_S2 = len(s2_headers)  # 12

    detail_groups = defaultdict(list)
    for d in detail_rows:
        key = (d.get("project"), d.get("item_name"))
        detail_groups[key].append(d)

    row_no = 1

    for (proj, item_nm), rows in detail_groups.items():

        # Project + Item heading
        ws2.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=TOTAL_COLS_S2)
        h2           = ws2.cell(row=row_no, column=1, value=f"{proj}  —  {item_nm}")
        h2.font      = Font(bold=True, size=14, color="1F4E79")
        h2.alignment = left_align
        ws2.row_dimensions[row_no].height = 22
        row_no += 1

        # Blank gap
        row_no += 1

        # Column headers
        for col, header in enumerate(s2_headers, 1):
            cell           = ws2.cell(row=row_no, column=col, value=header)
            cell.font      = header_font
            cell.fill      = header_fill
            cell.border    = thin_border
            cell.alignment = center_align
        ws2.row_dimensions[row_no].height = 18
        row_no += 1

        # Data rows
        t_qty = t_length = t_width = t_weight = 0
        sr = 1

        for d in rows:
            qty    = d.get("quantity")      or 0
            length = d.get("lenght")        or 0
            width  = d.get("width")         or 0
            sw     = d.get("single_weight") or 0
            weight = d.get("total_weight")  or 0

            row_vals = [
                sr,
                d.get("project"),
                d.get("item_name"),
                d.get("po_serial_no"),
                d.get("drawing_number"),
                d.get("position_no"),
                d.get("entry_count"),
                qty, length, width, sw, weight,
            ]

            for col, val in enumerate(row_vals, 1):
                cell           = ws2.cell(row=row_no, column=col, value=val)
                cell.font      = data_font
                cell.border    = thin_border
                cell.alignment = left_align if col in [2, 3, 5] else center_align
                if col in [11, 12]:
                    cell.number_format = '#,##0.000'

            t_qty += qty; t_length += length
            t_width += width; t_weight += weight
            row_no += 1; sr += 1

        # Detail total row
        for col in range(1, TOTAL_COLS_S2 + 1):
            cell           = ws2.cell(row=row_no, column=col)
            cell.fill      = total_fill
            cell.alignment = center_align
            cell.border    = thin_border

        ws2.merge_cells(start_row=row_no, start_column=1, end_row=row_no, end_column=3)
        tl           = ws2.cell(row=row_no, column=1, value="Total")
        tl.font      = total_font
        tl.fill      = total_fill
        tl.alignment = left_align
        tl.border    = thin_border

        for col, val in zip([8, 9, 10, 12], [t_qty, t_length, t_width, t_weight]):
            cell           = ws2.cell(row=row_no, column=col, value=val)
            cell.font      = total_font
            cell.fill      = total_fill
            cell.alignment = center_align
            cell.border    = thin_border
            if col == 12:
                cell.number_format = '#,##0.000'

        ws2.row_dimensions[row_no].height = 18
        row_no += 2  # blank row between groups

    for col, w in zip(range(1, 13), [8, 18, 40, 15, 30, 15, 12, 10, 12, 12, 16, 16]):
        ws2.column_dimensions[get_column_letter(col)].width = w

    # ---------------- SAVE FILE ----------------
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    file_doc = save_file(
        "FT_Drawing_Part.xlsx",
        file_stream.getvalue(),
        None,
        None,
        is_private=0
    )

    return file_doc.file_url


# Shown non fill data in excel file when value is None or 0, also added summary sheet with total projects, total weight as per project, total no of drawings, total weight as per drawing, total no of drawing parts and total weight as per drawing parts. we have also added styling to the excel file for better readability.
# @frappe.whitelist()
# def get_all_details_for_export(filters):

#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side
#     from openpyxl.utils import get_column_letter
#     from io import BytesIO
#     from frappe.utils.file_manager import save_file

#     filters = frappe.parse_json(filters)
#     conditions = ""
#     values = {}

#     if filters.get("project_number"):
#         conditions += " AND p.name IN %(project_number)s"
#         values["project_number"] = tuple(filters.get("project_number"))

#     if filters.get("drawing_number"):
#         conditions += " AND ad.name IN %(drawing_number)s"
#         values["drawing_number"] = tuple(filters.get("drawing_number"))

#     if filters.get("item"):
#         conditions += " AND dp.item IN %(item)s"
#         values["item"] = tuple(filters.get("item"))

#     # ================= DETAILS QUERY =================
#     # Base table = FT Add Drawing (important)
#     detail_data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             ad.name as drawing_number,
#             rm.computed_name as item_name,
#             dp.quantity,
#             dp.lenght,
#             dp.width,
#             dp.single_weight,
#             dp.total_weight
#         FROM `tabFT Add Drawing` ad
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
#         WHERE 1=1 {conditions}
#         ORDER BY p.name, ad.name
#     """, values, as_dict=True)

#     # ================= SUMMARY QUERY =================
#     summary_data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item_name,
#             COUNT(dp.name) as total_entries,
#             SUM(dp.total_weight) as total_weight
#         FROM `tabFT Add Drawing` ad
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
#         WHERE 1=1 {conditions}
#         GROUP BY p.name, rm.computed_name
#         ORDER BY p.name
#     """, values, as_dict=True)

#     # ================= CREATE WORKBOOK =================
#     wb = openpyxl.Workbook()

#     header_font = Font(bold=True)
#     header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     # ================= SUMMARY SHEET =================
#     ws1 = wb.active
#     ws1.title = "Summary"

#     summary_headers = ["Project", "Item", "Total Entries", "Total Weight"]

#     for col, header in enumerate(summary_headers, 1):
#         cell = ws1.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border

#     row_no = 2
#     for d in summary_data:
#         row_values = [
#             d.get("project") or "",
#             d.get("item_name") or "",
#             d.get("total_entries") or 0,
#             d.get("total_weight") or 0,
#         ]
#         for col, value in enumerate(row_values, 1):
#             cell = ws1.cell(row=row_no, column=col, value=value)
#             cell.border = thin_border
#         row_no += 1

#     for col in range(1, len(summary_headers) + 1):
#         ws1.column_dimensions[get_column_letter(col)].width = 20


#     # ================= DETAIL SHEET =================
#     ws2 = wb.create_sheet("Details")

#     detail_headers = [
#         "Project",
#         "Drawing",
#         "Item",
#         "Qty",
#         "Length",
#         "Width",
#         "Single Weight",
#         "Total Weight"
#     ]

#     for col, header in enumerate(detail_headers, 1):
#         cell = ws2.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border

#     row_no = 2
#     for d in detail_data:
#         row_values = [
#             d.get("project") or "",
#             d.get("drawing_number") or "",
#             d.get("item_name") or "",
#             d.get("quantity") or 0,
#             d.get("lenght") or 0,
#             d.get("width") or 0,
#             d.get("single_weight") or 0,
#             d.get("total_weight") or 0,
#         ]
#         for col, value in enumerate(row_values, 1):
#             cell = ws2.cell(row=row_no, column=col, value=value)
#             cell.border = thin_border
#         row_no += 1

#     for col in range(1, len(detail_headers) + 1):
#         ws2.column_dimensions[get_column_letter(col)].width = 20

#     # ================= SAVE FILE =================
#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     file_doc = save_file(
#         "FT_Drawing_Part_Report.xlsx",
#         file_stream.getvalue(),
#         None,
#         None,
#         is_private=0
#     )

#     return file_doc.file_url


# The above function is the initial version for exporting details, but we will enhance it to create a well-formatted Excel file, including styling and better organization of data.
# @frappe.whitelist()
# def download_item_excel(filters):
#     import frappe
#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
#     from io import BytesIO

#     filters = frappe.parse_json(filters)

#     conditions = ""
#     values = {}

#     if filters.get("project_number"):
#         conditions += " AND p.name IN %(project_number)s"
#         values["project_number"] = tuple(filters.get("project_number"))

#     if filters.get("item"):
#         conditions += " AND dp.item_id IN %(item)s"
#         values["item"] = tuple(filters.get("item"))

#     data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item,
#             COUNT(dp.name) as total_entries,
#             IFNULL(SUM(dp.total_weight),0) as total_weight
#         FROM `tabFT Drawing Parts` dp
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
#         WHERE 1=1 {conditions}
#         GROUP BY p.name, rm.computed_name
#         ORDER BY p.name
#     """, values, as_dict=True)

#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Item Report"

#     headers = ["Project", "Item", "Total Entries", "Total Weight"]

#     header_font = Font(bold=True, size=12, color="FFFFFF")
#     header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

#     total_font = Font(bold=True, size=12)
#     total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     center_align = Alignment(horizontal="center", vertical="center")

#     # Header Row
#     for col, header in enumerate(headers, 1):
#         cell = ws.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border
#         cell.alignment = center_align

#     # Data Rows
#     row_no = 2
#     grand_total_entries = 0
#     grand_total_weight = 0

#     for d in data:
#         entries = d.get("total_entries") or 0
#         weight = d.get("total_weight") or 0

#         values_row = [
#             d.get("project"),
#             d.get("item") or "-",
#             entries,
#             weight,
#         ]

#         grand_total_entries += entries
#         grand_total_weight += weight

#         for col, val in enumerate(values_row, 1):
#             cell = ws.cell(row=row_no, column=col, value=val)
#             cell.border = thin_border
#             cell.alignment = start_align = Alignment(horizontal="left", vertical="center") if col in [1, 2] else center_align
#             cell.font = Font(size=11)

#         row_no += 1

#     # GRAND TOTAL ROW ADD
#     total_row = row_no

#     ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)

#     total_label = ws.cell(row=total_row, column=1, value="Total")
#     total_label.font = total_font
#     total_label.fill = total_fill
#     total_label.alignment = start_align = Alignment(horizontal="left", vertical="center")

#     total_entries_cell = ws.cell(row=total_row, column=3, value=grand_total_entries)
#     total_entries_cell.font = total_font
#     total_entries_cell.fill = total_fill
#     total_entries_cell.alignment = center_align

#     total_weight_cell = ws.cell(row=total_row, column=4, value=grand_total_weight)
#     total_weight_cell.font = total_font
#     total_weight_cell.fill = total_fill
#     total_weight_cell.alignment = center_align

#     # Apply border to full total row
#     for col in range(1, 5):
#         ws.cell(row=total_row, column=col).border = thin_border

#     # Column Width Adjust
#     ws.column_dimensions["A"].width = 20
#     ws.column_dimensions["B"].width = 45
#     ws.column_dimensions["C"].width = 18
#     ws.column_dimensions["D"].width = 18

#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     frappe.response['filename'] = "Item_Report.xlsx"
#     frappe.response['filecontent'] = file_stream.getvalue()
#     frappe.response['type'] = 'binary'
    
# @frappe.whitelist()
# def download_item_excel(filters):
#     import frappe
#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
#     from io import BytesIO

#     filters = frappe.parse_json(filters)

#     conditions = ""
#     values = {}

#     if filters.get("project_number"):
#         conditions += " AND p.name IN %(project_number)s"
#         values["project_number"] = tuple(filters.get("project_number"))

#     if filters.get("item"):
#         conditions += " AND dp.item_id IN %(item)s"
#         values["item"] = tuple(filters.get("item"))

#     data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item,
#             COUNT(dp.name) as total_entries,
#             IFNULL(SUM(dp.quantity), 0) as total_qty,
#             IFNULL(SUM(dp.lenght), 0) as total_length,
#             IFNULL(SUM(dp.width), 0) as total_width,
#             IFNULL(SUM(dp.total_weight),0) as total_weight
#         FROM `tabFT Drawing Parts` dp
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
#         WHERE 1=1 {conditions}
#         GROUP BY p.name, rm.computed_name
#         ORDER BY p.name
#     """, values, as_dict=True)

#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Item Report"

#     headers = ["Project", "Item", "Total Entries", "Total Qty", "Total Length", "Total Width", "Total Weight"]

#     header_font = Font(bold=True, size=12, color="FFFFFF")
#     header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

#     total_font = Font(bold=True, size=12)
#     total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )

#     center_align = Alignment(horizontal="center", vertical="center")
#     left_align = Alignment(horizontal="left", vertical="center")

#     # -------- HEADER ROW --------
#     for col, header in enumerate(headers, 1):
#         cell = ws.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = thin_border
#         cell.alignment = center_align

#     # -------- DATA ROWS --------
#     row_no = 2
#     grand_total_entries = 0
#     grand_total_qty = 0
#     grand_total_length = 0
#     grand_total_width = 0
#     grand_total_weight = 0

#     for d in data:
#         entries = d.get("total_entries") or 0
#         qty     = d.get("total_qty") or 0
#         length  = d.get("total_length") or 0
#         width   = d.get("total_width") or 0
#         weight  = d.get("total_weight") or 0

#         values_row = [
#             d.get("project"),
#             d.get("item") or "-",
#             entries,
#             qty,
#             length,
#             width,
#             weight,
#         ]

#         grand_total_entries += entries
#         grand_total_qty     += qty
#         grand_total_length  += length
#         grand_total_width   += width
#         grand_total_weight  += weight

#         for col, val in enumerate(values_row, 1):
#             cell = ws.cell(row=row_no, column=col, value=val)
#             cell.border = thin_border
#             cell.alignment = left_align if col in [1, 2] else center_align
#             cell.font = Font(size=11)

#         row_no += 1

#     # -------- GRAND TOTAL ROW --------
#     total_row = row_no

#     ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)

#     total_label = ws.cell(row=total_row, column=1, value="Total")
#     total_label.font = total_font
#     total_label.fill = total_fill
#     total_label.alignment = left_align

#     # Col 3 → Total Entries
#     c3 = ws.cell(row=total_row, column=3, value=grand_total_entries)
#     c3.font = total_font
#     c3.fill = total_fill
#     c3.alignment = center_align

#     # Col 4 → Total Qty
#     c4 = ws.cell(row=total_row, column=4, value=grand_total_qty)
#     c4.font = total_font
#     c4.fill = total_fill
#     c4.alignment = center_align

#     # Col 5 → Total Length
#     c5 = ws.cell(row=total_row, column=5, value=grand_total_length)
#     c5.font = total_font
#     c5.fill = total_fill
#     c5.alignment = center_align

#     # Col 6 → Total Width
#     c6 = ws.cell(row=total_row, column=6, value=grand_total_width)
#     c6.font = total_font
#     c6.fill = total_fill
#     c6.alignment = center_align

#     # Col 7 → Total Weight
#     c7 = ws.cell(row=total_row, column=7, value=grand_total_weight)
#     c7.font = total_font
#     c7.fill = total_fill
#     c7.alignment = center_align

#     # Border apply on total row
#     for col in range(1, 8):
#         ws.cell(row=total_row, column=col).border = thin_border

#     # -------- COLUMN WIDTH --------
#     ws.column_dimensions["A"].width = 20   # Project
#     ws.column_dimensions["B"].width = 45   # Item
#     ws.column_dimensions["C"].width = 15   # Total Entries
#     ws.column_dimensions["D"].width = 12   # Total Qty
#     ws.column_dimensions["E"].width = 15   # Total Length
#     ws.column_dimensions["F"].width = 15   # Total Width
#     ws.column_dimensions["G"].width = 18   # Total Weight

#     # -------- SAVE & RETURN --------
#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     frappe.response['filename'] = "Item_Report.xlsx"
#     frappe.response['filecontent'] = file_stream.getvalue()
#     frappe.response['type'] = 'binary'

# @frappe.whitelist()
# def download_item_excel(filters):
#     import frappe
#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
#     from io import BytesIO

#     filters = frappe.parse_json(filters)

#     conditions = ""
#     values = {}

#     if filters.get("project_number"):
#         conditions += " AND p.name IN %(project_number)s"
#         values["project_number"] = tuple(filters.get("project_number"))

#     if filters.get("item"):
#         conditions += " AND dp.item_id IN %(item)s"
#         values["item"] = tuple(filters.get("item"))

#     data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item,
#             COUNT(dp.name) as total_entries,
#             IFNULL(SUM(dp.quantity), 0) as total_qty,
#             IFNULL(SUM(dp.lenght), 0) as total_length,
#             IFNULL(SUM(dp.width), 0) as total_width,
#             IFNULL(SUM(dp.total_weight),0) as total_weight
#         FROM `tabFT Drawing Parts` dp
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
#         WHERE 1=1 {conditions}
#         GROUP BY p.name, rm.computed_name
#         ORDER BY p.name
#     """, values, as_dict=True)

#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Item Report"

#     # -------- STYLES --------
#     header_font       = Font(bold=True, size=12, color="FFFFFF")
#     header_fill       = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
#     total_font        = Font(bold=True, size=12)
#     total_fill        = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")
#     project_font      = Font(bold=True, size=13, color="FFFFFF")
#     project_fill      = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
#     proj_total_font   = Font(bold=True, size=11, color="FFFFFF")
#     proj_total_fill   = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

#     thin_border = Border(
#         left=Side(style="thin"),
#         right=Side(style="thin"),
#         top=Side(style="thin"),
#         bottom=Side(style="thin")
#     )
#     center_align = Alignment(horizontal="center", vertical="center")
#     left_align   = Alignment(horizontal="left",   vertical="center")

#     headers = ["Sr No", "Project", "Item", "Total Entries", "Total Qty", "Total Length", "Total Width", "Total Weight"]
#     TOTAL_COLS = len(headers)  # 8

#     # -------- GROUP DATA BY PROJECT --------
#     from collections import defaultdict
#     project_groups = defaultdict(list)
#     for d in data:
#         project_groups[d.get("project") or "Unknown"].append(d)

#     row_no = 1

#     grand_total_entries = 0
#     grand_total_qty     = 0
#     grand_total_length  = 0
#     grand_total_width   = 0
#     grand_total_weight  = 0

#     for project_name, rows in project_groups.items():

#         # ======== PROJECT HEADING ROW ========
#         ws.merge_cells(
#             start_row=row_no, start_column=1,
#             end_row=row_no,   end_column=TOTAL_COLS
#         )
#         heading_cell = ws.cell(
#             row=row_no, column=1,
#             value=f"  {project_name}  —  All Items Data"
#         )
#         heading_cell.font      = project_font
#         heading_cell.fill      = project_fill
#         heading_cell.alignment = left_align
#         heading_cell.border    = thin_border
#         ws.row_dimensions[row_no].height = 22
#         row_no += 1

#         # ======== COLUMN HEADER ROW ========
#         for col, header in enumerate(headers, 1):
#             cell = ws.cell(row=row_no, column=col, value=header)
#             cell.font      = header_font
#             cell.fill      = header_fill
#             cell.border    = thin_border
#             cell.alignment = center_align
#         ws.row_dimensions[row_no].height = 18
#         row_no += 1

#         # ======== DATA ROWS ========
#         proj_entries = proj_qty = proj_length = proj_width = proj_weight = 0
#         sr = 1

#         for d in rows:
#             entries = d.get("total_entries") or 0
#             qty     = d.get("total_qty")     or 0
#             length  = d.get("total_length")  or 0
#             width   = d.get("total_width")   or 0
#             weight  = d.get("total_weight")  or 0

#             values_row = [
#                 sr,
#                 d.get("project") or "-",
#                 d.get("item")    or "-",
#                 entries,
#                 qty,
#                 length,
#                 width,
#                 weight,
#             ]

#             proj_entries += entries
#             proj_qty     += qty
#             proj_length  += length
#             proj_width   += width
#             proj_weight  += weight

#             for col, val in enumerate(values_row, 1):
#                 cell = ws.cell(row=row_no, column=col, value=val)
#                 cell.border    = thin_border
#                 cell.alignment = left_align if col in [2, 3] else center_align
#                 cell.font      = Font(size=11)
#             row_no += 1
#             sr += 1

#         # ======== PROJECT TOTAL ROW ========
#         ws.merge_cells(
#             start_row=row_no, start_column=1,
#             end_row=row_no,   end_column=3
#         )
#         pt_label = ws.cell(row=row_no, column=1, value=f"Total — {project_name}")
#         pt_label.font      = proj_total_font
#         pt_label.fill      = proj_total_fill
#         pt_label.alignment = left_align
#         pt_label.border    = thin_border

#         for col, val in zip(range(4, 9), [proj_entries, proj_qty, proj_length, proj_width, proj_weight]):
#             cell = ws.cell(row=row_no, column=col, value=val)
#             cell.font      = proj_total_font
#             cell.fill      = proj_total_fill
#             cell.alignment = center_align
#             cell.border    = thin_border

#         ws.row_dimensions[row_no].height = 18
#         row_no += 1

#         # Blank row between projects
#         row_no += 1

#         grand_total_entries += proj_entries
#         grand_total_qty     += proj_qty
#         grand_total_length  += proj_length
#         grand_total_width   += proj_width
#         grand_total_weight  += proj_weight

#     # ======== GRAND TOTAL ROW ========
#     ws.merge_cells(
#         start_row=row_no, start_column=1,
#         end_row=row_no,   end_column=3
#     )
#     gt_label = ws.cell(row=row_no, column=1, value="Grand Total — All Projects")
#     gt_label.font      = Font(bold=True, size=13, color="FFFFFF")
#     gt_label.fill      = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
#     gt_label.alignment = left_align
#     gt_label.border    = thin_border

#     for col, val in zip(
#         range(4, 9),
#         [grand_total_entries, grand_total_qty, grand_total_length, grand_total_width, grand_total_weight]
#     ):
#         cell = ws.cell(row=row_no, column=col, value=val)
#         cell.font      = Font(bold=True, size=12, color="FFFFFF")
#         cell.fill      = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
#         cell.alignment = center_align
#         cell.border    = thin_border

#     ws.row_dimensions[row_no].height = 20

#     # -------- COLUMN WIDTH --------
#     ws.column_dimensions["A"].width = 8    # Sr No
#     ws.column_dimensions["B"].width = 18   # Project
#     ws.column_dimensions["C"].width = 45   # Item
#     ws.column_dimensions["D"].width = 15   # Total Entries
#     ws.column_dimensions["E"].width = 12   # Total Qty
#     ws.column_dimensions["F"].width = 15   # Total Length
#     ws.column_dimensions["G"].width = 15   # Total Width
#     ws.column_dimensions["H"].width = 18   # Total Weight

#     # -------- SAVE & RETURN --------
#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     frappe.response['filename'] = "Item_Report.xlsx"
#     frappe.response['filecontent'] = file_stream.getvalue()
#     frappe.response['type'] = 'binary'



@frappe.whitelist()
def download_item_excel(filters):
    import frappe
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from io import BytesIO

    filters = frappe.parse_json(filters)

    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("item"):
        conditions += " AND dp.item_id IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item,
            COUNT(dp.name) as total_entries,
            IFNULL(SUM(dp.quantity), 0) as total_qty,
            IFNULL(SUM(dp.lenght), 0) as total_length,
            IFNULL(SUM(dp.width), 0) as total_width,
            IFNULL(SUM(dp.total_weight),0) as total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
        WHERE 1=1 {conditions}
        GROUP BY p.name, rm.computed_name
        ORDER BY p.name
    """, values, as_dict=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Item Report"

    # -------- STYLES --------
    header_font     = Font(bold=True, size=12, color="FFFFFF")
    header_fill     = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    proj_total_font = Font(bold=True, size=11, color="FFFFFF")
    proj_total_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    center_align = Alignment(horizontal="center", vertical="center")
    left_align   = Alignment(horizontal="left",   vertical="center")

    headers    = ["Sr No", "Project", "Item", "Total Entries", "Total Qty", "Total Length", "Total Width", "Total Weight"]
    TOTAL_COLS = len(headers)  # 8

    # -------- GROUP DATA BY PROJECT --------
    from collections import defaultdict
    project_groups = defaultdict(list)
    for d in data:
        project_groups[d.get("project") or "Unknown"].append(d)

    row_no = 1

    for project_name, rows in project_groups.items():

        # ======== PROJECT HEADING — No background, big bold font ========
        ws.merge_cells(
            start_row=row_no, start_column=1,
            end_row=row_no,   end_column=TOTAL_COLS
        )
        heading_cell = ws.cell(
            row=row_no, column=1,
            value=f"{project_name}  —  All Items Data"
        )
        # ✅ Sirf font bada, koi background nahi
        heading_cell.font      = Font(bold=True, size=15, color="1F4E79")
        heading_cell.alignment = left_align
        ws.row_dimensions[row_no].height = 24
        row_no += 1

        # ✅ Blank row — heading aur table ke beech gap
        row_no += 1

        # ======== COLUMN HEADER ROW ========
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row_no, column=col, value=header)
            cell.font      = header_font
            cell.fill      = header_fill
            cell.border    = thin_border
            cell.alignment = center_align
        ws.row_dimensions[row_no].height = 18
        row_no += 1

        # ======== DATA ROWS ========
        proj_entries = proj_qty = proj_length = proj_width = proj_weight = 0
        sr = 1

        for d in rows:
            entries = d.get("total_entries") or 0
            qty     = d.get("total_qty")     or 0
            length  = d.get("total_length")  or 0
            width   = d.get("total_width")   or 0
            weight  = d.get("total_weight")  or 0

            values_row = [
                sr,
                d.get("project") or "-",
                d.get("item")    or "-",
                entries, qty, length, width, weight,
            ]

            proj_entries += entries
            proj_qty     += qty
            proj_length  += length
            proj_width   += width
            proj_weight  += weight

            for col, val in enumerate(values_row, 1):
                cell = ws.cell(row=row_no, column=col, value=val)
                cell.border    = thin_border
                cell.alignment = left_align if col in [2, 3] else center_align
                cell.font      = Font(size=11)
            row_no += 1
            sr += 1

        # ======== PROJECT TOTAL ROW — Sirf "Total" ========
        ws.merge_cells(
            start_row=row_no, start_column=1,
            end_row=row_no,   end_column=3
        )
        pt_label = ws.cell(row=row_no, column=1, value="Total")   
        pt_label.font      = proj_total_font
        pt_label.fill      = proj_total_fill
        pt_label.alignment = left_align
        pt_label.border    = thin_border

        for col, val in zip(
            range(4, 9),
            [proj_entries, proj_qty, proj_length, proj_width, proj_weight]
        ):
            cell = ws.cell(row=row_no, column=col, value=val)
            cell.font      = proj_total_font
            cell.fill      = proj_total_fill
            cell.alignment = center_align
            cell.border    = thin_border

        ws.row_dimensions[row_no].height = 18
        row_no += 1

        # ✅ Blank row between projects
        row_no += 1

    # ======== ✅ GRAND TOTAL ROW — REMOVED ========

    # -------- COLUMN WIDTH --------
    ws.column_dimensions["A"].width = 8    # Sr No
    ws.column_dimensions["B"].width = 18   # Project
    ws.column_dimensions["C"].width = 45   # Item
    ws.column_dimensions["D"].width = 15   # Total Entries
    ws.column_dimensions["E"].width = 12   # Total Qty
    ws.column_dimensions["F"].width = 15   # Total Length
    ws.column_dimensions["G"].width = 15   # Total Width
    ws.column_dimensions["H"].width = 18   # Total Weight

    # -------- SAVE & RETURN --------
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response['filename'] = "Item_Report.xlsx"
    frappe.response['filecontent'] = file_stream.getvalue()
    frappe.response['type'] = 'binary'


# The above function generates a well-formatted Excel file for item details, including styling and better organization of data. It handles cases where values might be None or 0, ensuring the Excel file is clean and readable.
# @frappe.whitelist()
# def download_item_details_excel(filters):
#     import frappe
#     import openpyxl
#     from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
#     from openpyxl.utils import get_column_letter
#     from io import BytesIO
#     from collections import defaultdict

#     filters = frappe.parse_json(filters)

#     item = filters.get("item")
#     project = filters.get("project")

#     data = frappe.db.sql("""
#         SELECT
#             p.name as project_number,
#             pod.po_serial_no,
#             ad.drawing_number as drawing,
#             dp.position_no,
#             dp.quantity,
#             dp.lenght,
#             dp.width,
#             dp.single_weight,
#             dp.total_weight
#         FROM `tabFT Drawing Parts` dp
#         LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
#         LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
#         LEFT JOIN `tabFT Po Drawing` pod
#             ON pod.project_number = p.name
#             AND pod.drawing_number = ad.name
#         WHERE dp.item = %(item)s
#         AND ad.project_number = %(project)s
#         ORDER BY 
#             CAST(pod.po_serial_no AS UNSIGNED) ASC,
#             ad.drawing_number ASC
#     """, {"item": item, "project": project}, as_dict=True)

#     # -------- GROUP SAME ROWS --------
#     grouped = defaultdict(lambda: {
#         "project_number": "",
#         "po_serial_no": "",
#         "drawing": "",
#         "position_no": "",
#         "quantity": 0,
#         "lenght": 0,
#         "width": 0,
#         "single_weight": 0,
#         "total_weight": 0,
#         "entry_count": 0
#     })

#     for d in data:
#         key = (
#             d.get("project_number"),
#             d.get("po_serial_no"),
#             d.get("drawing"),
#             d.get("position_no"),
#             d.get("quantity"),
#             d.get("lenght"),
#             d.get("width"),
#             d.get("single_weight"),
#             d.get("total_weight"),
#         )

#         grouped[key]["project_number"] = d.get("project_number")
#         grouped[key]["po_serial_no"] = d.get("po_serial_no")
#         grouped[key]["drawing"] = d.get("drawing")
#         grouped[key]["position_no"] = d.get("position_no")
#         grouped[key]["quantity"] = d.get("quantity")
#         grouped[key]["lenght"] = d.get("lenght")
#         grouped[key]["width"] = d.get("width")
#         grouped[key]["single_weight"] = d.get("single_weight")
#         grouped[key]["total_weight"] = d.get("total_weight")
#         grouped[key]["entry_count"] += 1

#     data = list(grouped.values())

#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Item Details"

#     headers = [
#         "Sr No",
#         "Project No",
#         "Po Serial No",
#         "Drawing",
#         "Position No",
#         "Entry Count",
#         "Qty",
#         "Length",
#         "Width",
#         "Single Weight",
#         "Total Weight"
#     ]

#     # -------- STYLES --------
#     header_font = Font(bold=True, size=13, color="FFFFFF")
#     header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
#     data_font = Font(size=12)
#     total_font = Font(bold=True, size=14)
#     total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

#     thin = Side(style="thin")
#     center = Alignment(horizontal="center", vertical="center")
#     full_border = Border(left=thin, right=thin, top=thin, bottom=thin)

#     # -------- HEADER --------
#     for col, header in enumerate(headers, 1):
#         cell = ws.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.border = full_border
#         cell.alignment = center

#     row_no = 2
#     serial_no = 1

#     total_qty = total_length = total_width = total_weight = 0

#     # -------- DATA ROWS --------
#     for d in data:

#         row_values = [
#             serial_no,
#             d.get("project_number"),
#             d.get("po_serial_no"),
#             d.get("drawing"),
#             d.get("position_no"),
#             d.get("entry_count"),
#             d.get("quantity"),
#             d.get("lenght"),
#             d.get("width"),
#             d.get("single_weight"),
#             d.get("total_weight"),
#         ]

#         total_qty += d.get("quantity") or 0
#         total_length += d.get("lenght") or 0
#         total_width += d.get("width") or 0
#         total_weight += d.get("total_weight") or 0

#         for col, val in enumerate(row_values, 1):
#             cell = ws.cell(row=row_no, column=col, value=val)
#             cell.font = data_font
#             cell.border = full_border
#             cell.alignment = center
            
#             # Formatting for Single Weight (column 10)
#             if col == 10:
#                 cell.number_format = '#,##0.000'

#             # Formatting for Total Weight (column 11)
#             if col == 11:
#                 cell.number_format = '#,##0.000'

#         row_no += 1
#         serial_no += 1

#     # -------- TOTAL ROW --------
#     for col in range(1, 12):
#         cell = ws.cell(row=row_no, column=col)
#         cell.fill = total_fill
#         cell.alignment = center

#         if col == 1:
#             cell.value = "Total"
#             cell.font = total_font
#             cell.border = Border(left=thin, top=thin, bottom=thin)

#         elif col == 7:
#             cell.value = total_qty
#             cell.font = total_font
#             cell.border = Border(top=thin, bottom=thin)

#         elif col == 8:
#             cell.value = total_length
#             cell.font = total_font
#             cell.border = Border(top=thin, bottom=thin)

#         elif col == 9:
#             cell.value = total_width
#             cell.font = total_font
#             cell.border = Border(top=thin, bottom=thin)

#         elif col == 11:
#             cell.value = total_weight
#             cell.font = total_font
#             cell.border = Border(right=thin, left=thin, top=thin, bottom=thin)
#             cell.number_format = '#,##0.000'  # <-- yahan number format lagao

#         else:
#             cell.border = Border(top=thin, bottom=thin)

#     # -------- COLUMN WIDTH --------
#     widths = [8, 18, 15, 30, 15, 12, 10, 12, 12, 16, 16]
#     for i, w in enumerate(widths, 1):
#         ws.column_dimensions[get_column_letter(i)].width = w

#     # -------- SAVE --------
#     file_stream = BytesIO()
#     wb.save(file_stream)
#     file_stream.seek(0)

#     frappe.response['filename'] = "Item_Details.xlsx"
#     frappe.response['filecontent'] = file_stream.getvalue()
#     frappe.response['type'] = 'download'   
    
        
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
    for col in range(1, 12):
        cell = ws.cell(row=row_no, column=col)
        cell.fill = total_fill
        cell.alignment = center

        if col == 1:
            cell.value = "Total"
            cell.font = total_font
            cell.border = Border(left=thin, top=thin, bottom=thin)

        elif col == 7:
            cell.value = total_qty
            cell.font = total_font
            cell.border = Border(top=thin, bottom=thin)

        elif col == 8:
            cell.value = total_length
            cell.font = total_font
            cell.border = Border(top=thin, bottom=thin)

        elif col == 9:
            cell.value = total_width
            cell.font = total_font
            cell.border = Border(top=thin, bottom=thin)

        elif col == 11:
            cell.value = total_weight
            cell.font = total_font
            cell.border = Border(right=thin, left=thin, top=thin, bottom=thin)
            cell.number_format = '#,##0.000'  # <-- yahan number format lagao

        else:
            cell.border = Border(top=thin, bottom=thin)

    # -------- COLUMN WIDTH --------
    widths = [8, 18, 15, 30, 15, 12, 10, 12, 12, 16, 16]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # -------- SAVE --------
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response['filename'] = "Item_Details.xlsx"
    frappe.response['filecontent'] = file_stream.getvalue()
    frappe.response['type'] = 'download'
