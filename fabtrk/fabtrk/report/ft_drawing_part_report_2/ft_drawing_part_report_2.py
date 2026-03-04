import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project", "fieldname": "project_name", "fieldtype": "Link", "options": "FT Project", "width": 190},
        {"label": "Item", "fieldname": "item_name", "width": 400},
        {"label": "Total Entries", "fieldname": "item_count", "fieldtype": "Int", "width": 200, "align": "center"},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 200, "align": "center"},
        {"label": "Details", "fieldname": "view", "fieldtype": "HTML", "width": 200, "align": "center"},
    ]

    # ---------------- CONDITIONS ----------------
    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
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
        dp.item AS item_id,
        rm.computed_name AS item_name,
        COALESCE(CAST(st.sort_key AS UNSIGNED), 9999) AS sort_key,
        COUNT(dp.name) AS item_count,
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
    ORDER BY p.name, sort_key ASC
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
            WHERE ad.drawing_number IN %(drawing_number)s
        """, {
            "drawing_number": tuple(filters.get("drawing_number"))
        }, as_dict=True)

        for proj in blank_projects:
            data.append({
                "project_name": proj.name,
                "item": "-",
                "total_entries": 0,
                "total_weight": 0.000,
            })

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
        project_count_query += " AND ad.drawing_number IN %(drawing_number)s"
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
        {" AND ad.drawing_number IN %(drawing_number)s" if filters.get("drawing_number") else ""}
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
            AND pod.drawing_number IN (
                SELECT name FROM `tabFT Add Drawing`
                WHERE drawing_number IN %(drawing_number)s
            )
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
        grand_total_weight = sum(d["total_weight"] for d in data)
        # grand_total_weight = sum(float(d.get("total_weight") or 0) for d in data)

# ---------------- GET ITEM DETAILS FOR MODAL ----------------
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

    item_name = frappe.db.get_value("FT Stock RM List", item, "computed_name") or item

    return {"item_name": item_name, "data": rows}


# # ---------------- EXCEL EXPORT ----------------
# @frappe.whitelist()
# def get_all_details_for_export(filters):
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

#     data = frappe.db.sql(f"""
#         SELECT
#             p.name as project,
#             rm.computed_name as item_name,
#             ad.drawing_number,
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

#     return data

    
    
    
# The above function is the initial version for exporting details, but we will enhance it to create a well-formatted Excel file with separate sheets for summary and details, including styling and better organization of data.
@frappe.whitelist()
def get_all_details_for_export(filters):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from frappe.utils.file_manager import save_file

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
        conditions += " AND dp.item_id IN %(item)s"
        values["item"] = tuple(filters.get("item"))

    # ---------------- DETAIL DATA ----------------
    detail_data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item_name,
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
        WHERE 1=1 {conditions}
        ORDER BY p.name, ad.drawing_number
    """, values, as_dict=True)

    # ---------------- SUMMARY DATA ----------------
    summary_data = frappe.db.sql(f"""
        SELECT
            p.name as project,
            rm.computed_name as item_name,
            COUNT(dp.name) as total_entries,
            SUM(dp.total_weight) as total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad ON ad.name = dp.drawing_number
        LEFT JOIN `tabFT Project` p ON p.name = ad.project_number
        LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item_id
        WHERE 1=1 {conditions}
        GROUP BY p.name, rm.computed_name
        ORDER BY p.name
    """, values, as_dict=True)
    # summary_data = frappe.db.sql(f"""
    #     SELECT
    #         p.name as project,
    #         rm.computed_name as item_name,
    #         COUNT(dp.name) as total_entries,
    #         COALESCE(SUM(dp.total_weight), 0) as total_weight
    #     FROM `tabFT Project` p
    #     LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
    #     LEFT JOIN `tabFT Drawing Parts` dp ON dp.drawing_number = ad.name
    #     LEFT JOIN `tabFT Stock RM List` rm ON rm.name = dp.item
    #     WHERE 1=1 {conditions}
    #     GROUP BY p.name, rm.computed_name
    #     ORDER BY p.name
    # """, values, as_dict=True)

    wb = openpyxl.Workbook()

    header_font = Font(bold=True, color="FFFFFF")
    total_font = Font(bold=True, size=12)

    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # ================= SUMMARY SHEET =================
    ws1 = wb.active
    ws1.title = "Summary"

    summary_headers = ["Project", "Item", "Total Entries", "Total Weight"]

    for col, header in enumerate(summary_headers, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border

    row_no = 2
    grand_total_summary = 0

    for d in summary_data:
        values_row = [
            d.get("project"),
            d.get("item_name"),
            d.get("total_entries"),
            d.get("total_weight"),
        ]

        grand_total_summary += d.get("total_weight") or 0

        for col, value in enumerate(values_row, 1):
            cell = ws1.cell(row=row_no, column=col, value=value)
            cell.border = thin_border
        row_no += 1

    # ADD GRAND TOTAL ROW (Summary)
    total_row = row_no

    ws1.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=3)
    total_label = ws1.cell(row=total_row, column=1, value="Total")
    total_label.font = total_font
    total_label.fill = total_fill
    total_label.border = thin_border

    total_value = ws1.cell(row=total_row, column=4, value=grand_total_summary)
    total_value.font = total_font
    total_value.fill = total_fill
    total_value.border = thin_border

    # Apply border to merged area
    for col in range(1, 5):
        ws1.cell(row=total_row, column=col).border = thin_border

    ws1.column_dimensions["A"].width = 20
    ws1.column_dimensions["B"].width = 40
    ws1.column_dimensions["C"].width = 18
    ws1.column_dimensions["D"].width = 18


    # ================= DETAIL SHEET =================
    ws2 = wb.create_sheet("Details")

    detail_headers = [
        "Project",
        "Item",
        "Drawing",
        "Position No",
        "Qty",
        "Length",
        "Width",
        "Single Weight",
        "Total Weight"
    ]

    for col, header in enumerate(detail_headers, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border

    row_no = 2
    grand_total_detail = 0

    for d in detail_data:
        values_row = [
            d.get("project"),
            d.get("item_name"),
            d.get("drawing_number"),
            d.get("position_no"),
            d.get("quantity"),
            d.get("lenght"),
            d.get("width"),
            d.get("single_weight"),
            d.get("total_weight"),
        ]

        grand_total_detail += d.get("total_weight") or 0

        for col, value in enumerate(values_row, 1):
            cell = ws2.cell(row=row_no, column=col, value=value)
            cell.border = thin_border
        row_no += 1

    # ADD GRAND TOTAL ROW (Details)
    total_row = row_no

    ws2.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=8)
    total_label = ws2.cell(row=total_row, column=1, value="Total")
    total_label.font = total_font
    total_label.fill = total_fill
    total_label.border = thin_border

    total_value = ws2.cell(row=total_row, column=9, value=grand_total_detail)
    total_value.font = total_font
    total_value.fill = total_fill
    total_value.border = thin_border

    for col in range(1, 10):
        ws2.cell(row=total_row, column=col).border = thin_border

    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 40
    ws2.column_dimensions["C"].width = 18
    ws2.column_dimensions["D"].width = 18
    ws2.column_dimensions["E"].width = 10
    ws2.column_dimensions["F"].width = 10
    ws2.column_dimensions["G"].width = 10
    ws2.column_dimensions["H"].width = 15
    ws2.column_dimensions["I"].width = 15

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

    headers = ["Project", "Item", "Total Entries", "Total Weight"]

    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

    total_font = Font(bold=True, size=12)
    total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    center_align = Alignment(horizontal="center", vertical="center")

    # Header Row
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = center_align

    # Data Rows
    row_no = 2
    grand_total_entries = 0
    grand_total_weight = 0

    for d in data:
        entries = d.get("total_entries") or 0
        weight = d.get("total_weight") or 0

        values_row = [
            d.get("project"),
            d.get("item") or "-",
            entries,
            weight,
        ]

        grand_total_entries += entries
        grand_total_weight += weight

        for col, val in enumerate(values_row, 1):
            cell = ws.cell(row=row_no, column=col, value=val)
            cell.border = thin_border
            cell.alignment = start_align = Alignment(horizontal="left", vertical="center") if col in [1, 2] else center_align
            cell.font = Font(size=11)

        row_no += 1

    # GRAND TOTAL ROW ADD
    total_row = row_no

    ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)

    total_label = ws.cell(row=total_row, column=1, value="Total")
    total_label.font = total_font
    total_label.fill = total_fill
    total_label.alignment = start_align = Alignment(horizontal="left", vertical="center")

    total_entries_cell = ws.cell(row=total_row, column=3, value=grand_total_entries)
    total_entries_cell.font = total_font
    total_entries_cell.fill = total_fill
    total_entries_cell.alignment = center_align

    total_weight_cell = ws.cell(row=total_row, column=4, value=grand_total_weight)
    total_weight_cell.font = total_font
    total_weight_cell.fill = total_fill
    total_weight_cell.alignment = center_align

    # Apply border to full total row
    for col in range(1, 5):
        ws.cell(row=total_row, column=col).border = thin_border

    # Column Width Adjust
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 18

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response['filename'] = "Item_Report.xlsx"
    frappe.response['filecontent'] = file_stream.getvalue()
    frappe.response['type'] = 'binary'
    

# The above function generates a well-formatted Excel file for item details, including styling and better organization of data. It handles cases where values might be None or 0, ensuring the Excel file is clean and readable.
@frappe.whitelist()
def download_item_details_excel(filters):
    import frappe
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    filters = frappe.parse_json(filters)

    item = filters.get("item")
    project = filters.get("project")

    data = frappe.db.sql("""
        SELECT
            dp.drawing_number as drawing,
            dp.position_no,
            dp.quantity,
            dp.lenght,
            dp.width,
            dp.single_weight,
            dp.total_weight
        FROM `tabFT Drawing Parts` dp
        LEFT JOIN `tabFT Add Drawing` ad
            ON ad.name = dp.drawing_number
        WHERE dp.item = %(item)s
        AND ad.project_number = %(project)s
    """, {"item": item, "project": project}, as_dict=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Item Details"
    # ws.row_dimensions[1].height = 28

    headers = [
        "Drawing",
        "Position",
        "Qty",
        "Length",
        "Width",
        "Single Weight",
        "Total Weight"
    ]

    # ---------- STYLES ----------
    header_font = Font(bold=True, size=13, color="FFFFFF")
    header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")

    data_font = Font(size=12)
    total_font = Font(bold=True, size=14)

    total_fill = PatternFill(start_color="F3F3F3", end_color="F3F3F3", fill_type="solid")

    thin = Side(style="thin")
    center = Alignment(horizontal="center", vertical="center")

    full_border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ---------- HEADER ----------
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = full_border
        cell.alignment = center

    row_no = 2
    total_weight_sum = 0

    # ---------- DATA ROWS ----------
    for d in data:

        row_values = [
            d.get("drawing"),
            d.get("position_no"),
            d.get("quantity"),
            d.get("lenght"),
            d.get("width"),
            d.get("single_weight"),
            d.get("total_weight"),
        ]

        total_weight_sum += d.get("total_weight") or 0

        for col, val in enumerate(row_values, 1):
            cell = ws.cell(row=row_no, column=col, value=val)
            cell.font = data_font
            cell.border = full_border
            cell.alignment = center

        row_no += 1

    # ---------- TOTAL ROW ----------
    for col in range(1, 8):

        cell = ws.cell(row=row_no, column=col)
        cell.fill = total_fill
        cell.alignment = start_align = Alignment(horizontal="left", vertical="center") if col == 1 else center

        # LEFT OUTER BORDER
        if col == 1:
            cell.border = Border(left=thin, top=thin, bottom=thin)
            cell.value = "Total"
            cell.font = total_font

        # RIGHT OUTER BORDER
        elif col == 7:
            cell.border = Border(right=thin, left=thin, top=thin, bottom=thin)
            cell.value = total_weight_sum
            cell.font = total_font

        # MIDDLE CELLS (NO VERTICAL LINE)
        else:
            cell.border = Border(top=thin, bottom=thin)

    # ---------- COLUMN WIDTH ----------
    widths = [22, 15, 10, 12, 12, 16, 16]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ---------- SAVE ----------
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    frappe.response['filename'] = "Item_Details.xlsx"
    frappe.response['filecontent'] = file_stream.getvalue()
    frappe.response['type'] = 'download'
    
    
    
