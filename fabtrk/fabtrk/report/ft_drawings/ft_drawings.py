# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Project",        "fieldname": "project_name",  "fieldtype": "Link",  "options": "FT Project", "width": 190},
        {"label": "Drawing Number", "fieldname": "drawing_number", "fieldtype": "Data",  "width": 200, "align": "center"},
        {"label": "PO Serial No",   "fieldname": "po_serial_no",  "fieldtype": "Data",  "width": 190, "align": "center"},
        {"label": "Unit Weight",    "fieldname": "unit_weight",   "fieldtype": "Float", "width": 200, "align": "center"},
        {"label": "Required Qty",   "fieldname": "quantity",      "fieldtype": "Int",   "width": 190, "align": "center"},
        {"label": "Total Weight",   "fieldname": "total_weight",  "fieldtype": "Float", "width": 200, "align": "center"},
    ]

    conditions = ""
    values = {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND ad.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    if filters.get("po_serial_no"):
        conditions += " AND pod.po_serial_no IN %(po_serial_no)s"
        values["po_serial_no"] = tuple(str(x) for x in filters.get("po_serial_no"))

    if filters.get("is_active"):
        conditions += " AND p.is_active = 1"

    query = f"""
        SELECT
            p.name AS project_name,
            ad.name AS drawing_id,
            ad.drawing_number AS drawing_number,
            pod.po_serial_no AS po_serial_no,
            IFNULL(ad.unit_weight, 0) AS unit_weight,
            IFNULL(pod.required_qty, 0) AS quantity,
            (IFNULL(pod.unit_weight, 0) * IFNULL(pod.required_qty, 0)) AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad ON ad.project_number = p.name
        LEFT JOIN `tabFT Po Drawing`  pod ON pod.drawing_number = ad.name
        WHERE 1=1 {conditions}
        ORDER BY CAST(pod.po_serial_no AS UNSIGNED) ASC
    """

    # ✅ Sirf pure data rows — koi TOTAL row nahi
    raw_data = frappe.db.sql(query, values, as_dict=1) or []

    return columns, raw_data, None, None, None


# ------------------ Cards — Directly Doctype se (table se bilkul alag)
@frappe.whitelist()
def get_summary_cards(filters=None):
    import json

    if filters:
        filters = json.loads(filters) if isinstance(filters, str) else filters
    else:
        filters = {}

    # ---------- FT Project doctype se ----------
    proj_cond = "WHERE 1=1"
    proj_vals = {}

    if filters.get("project_number"):
        proj_cond += " AND name IN %(project_number)s"
        proj_vals["project_number"] = tuple(filters["project_number"])

    if filters.get("is_active"):
        proj_cond += " AND is_active = 1"

    total_projects = frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabFT Project` {proj_cond}", proj_vals
    )[0][0] or 0

    project_total_weight = frappe.db.sql(
        f"SELECT IFNULL(SUM(total_weight), 0) FROM `tabFT Project` {proj_cond}", proj_vals
    )[0][0] or 0

    # ---------- FT Add Drawing + FT Po Drawing se ----------
    join_cond = "WHERE 1=1"
    join_vals = {}

    if filters.get("project_number"):
        join_cond += " AND p.name IN %(project_number)s"
        join_vals["project_number"] = tuple(filters["project_number"])

    if filters.get("drawing_number"):
        join_cond += " AND ad.drawing_number IN %(drawing_number)s"
        join_vals["drawing_number"] = tuple(filters["drawing_number"])

    if filters.get("po_serial_no"):
        join_cond += " AND pod.po_serial_no IN %(po_serial_no)s"
        join_vals["po_serial_no"] = tuple(str(x) for x in filters["po_serial_no"])

    if filters.get("is_active"):
        join_cond += " AND p.is_active = 1"

    po_result = frappe.db.sql(f"""
        SELECT
            COUNT(DISTINCT ad.name)                             AS total_drawings,
            COUNT(pod.name)                                     AS total_line_items,
            IFNULL(SUM(pod.unit_weight * pod.required_qty), 0) AS total_weight_line_items
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Add Drawing` ad  ON ad.project_number  = p.name
        LEFT JOIN `tabFT Po Drawing`  pod ON pod.drawing_number = ad.name
        {join_cond}
    """, join_vals, as_dict=1)

    po_data           = po_result[0] if po_result else {}
    total_drawings    = po_data.get("total_drawings",        0) or 0
    total_line_items  = po_data.get("total_line_items",      0) or 0
    total_weight_line = po_data.get("total_weight_line_items", 0) or 0
    drawing_balance   = float(project_total_weight) - float(total_weight_line)

    return {
        "total_projects":          int(total_projects),
        "project_total_weight":    float(project_total_weight),
        "total_line_items":        int(total_line_items),
        "total_weight_line_items": float(total_weight_line),
        "total_drawings":          int(total_drawings),
        "drawing_balance":         float(drawing_balance),
    }


# ------------------ Drawing Number filter
@frappe.whitelist()
def get_drawing_numbers(project_number=None, txt=None):
    import json

    filters = {}
    if project_number:
        projects = json.loads(project_number) if isinstance(project_number, str) else project_number
        if projects:
            filters["project_number"] = ["in", projects]

    results = frappe.db.get_all("FT Add Drawing", filters=filters, fields=["drawing_number"], limit=0)

    seen, unique = set(), []
    for r in results:
        val = r.get("drawing_number")
        if val and val not in seen:
            seen.add(val)
            unique.append({"value": val, "label": val, "description": ""})

    if txt:
        tl = txt.lower()
        unique = [u for u in unique if tl in u["label"].lower()]

    return unique


# ------------------------- PO Serial No filter
@frappe.whitelist()
def get_po_serial_numbers(project_number=None, drawing_number=None, txt=None):
    import json

    project_list = json.loads(project_number) if isinstance(project_number, str) else (project_number or [])
    drawing_list = json.loads(drawing_number) if isinstance(drawing_number, str) else (drawing_number or [])

    cond, vals = "WHERE 1=1", {}

    if project_list:
        cond += " AND pod.project_number IN %(project_list)s"
        vals["project_list"] = tuple(project_list)

    if drawing_list:
        cond += " AND pod.drawing_number IN (SELECT name FROM `tabFT Add Drawing` WHERE drawing_number IN %(drawing_list)s)"
        vals["drawing_list"] = tuple(drawing_list)

    rows = frappe.db.sql(
        f"SELECT DISTINCT pod.po_serial_no FROM `tabFT Po Drawing` pod {cond} "
        f"ORDER BY CAST(pod.po_serial_no AS UNSIGNED) ASC",
        vals, as_dict=True
    )

    unique = []
    for r in rows:
        val = r.get("po_serial_no")
        if val is not None:
            s = str(val)
            unique.append({"value": s, "label": s, "description": ""})

    if txt:
        tl = txt.lower()
        unique = [u for u in unique if tl in u["label"].lower()]

    return unique


# ------------------------- Excel Export
@frappe.whitelist()
def download_drawing_excel(filters):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from io import BytesIO

    filters = frappe.parse_json(filters)

    conditions, values = "", {}

    if filters.get("project_number"):
        conditions += " AND p.name IN %(project_number)s"
        values["project_number"] = tuple(filters.get("project_number"))

    if filters.get("drawing_number"):
        conditions += " AND pod.drawing_number IN %(drawing_number)s"
        values["drawing_number"] = tuple(filters.get("drawing_number"))

    data = frappe.db.sql(f"""
        SELECT p.name AS project,
               IFNULL(pod.drawing_number, '') AS drawing_number,
               IFNULL(pod.po_serial_no, '')   AS po_serial_no,
               IFNULL(pod.unit_weight, 0)     AS unit_weight,
               IFNULL(pod.required_qty, 0)    AS required_qty,
               IFNULL(pod.total_weight, 0)    AS total_weight
        FROM `tabFT Project` p
        LEFT JOIN `tabFT Po Drawing` pod ON p.name = pod.project_number
        WHERE 1=1 {conditions}
        ORDER BY p.name
    """, values, as_dict=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PO Drawing Data"

    ws.merge_cells('A1:F1')
    c = ws['A1']
    c.value = "PO Drawing"
    c.font  = Font(size=16, bold=True)
    c.alignment = Alignment(horizontal="center", vertical="center")

    hdrs  = ["Project", "Drawing Number", "PO Serial No", "Unit Weight", "Required Qty", "Total Weight"]
    hfont = Font(bold=True, size=13, color="FFFFFF")
    hfill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    dfont = Font(size=12)
    tfont = Font(bold=True, size=13, color="FFFFFF")
    tfill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
    bdr   = Border(left=Side(style="thin"), right=Side(style="thin"),
                   top=Side(style="thin"),  bottom=Side(style="thin"))
    ctr   = Alignment(horizontal="center", vertical="center")

    for col, h in enumerate(hdrs, 1):
        cell = ws.cell(row=2, column=col, value=h)
        cell.font = hfont; cell.fill = hfill; cell.border = bdr; cell.alignment = ctr

    rn = 3; uwt = rqt = gt = 0

    for d in data:
        uw = d.get("unit_weight") or 0
        rq = d.get("required_qty") or 0
        tw = d.get("total_weight") or 0
        uwt += uw; rqt += rq; gt += tw

        for col, val in enumerate([d.get("project"), d.get("drawing_number"),
                                    d.get("po_serial_no"), uw, rq, tw], 1):
            cell = ws.cell(row=rn, column=col, value=val)
            cell.font = dfont; cell.border = bdr; cell.alignment = ctr
            if col in [4, 6]: cell.number_format = '0.000'
        rn += 1

    # Total row Excel mein rakhni hai (export ke liye zaroori)
    for col in range(1, 7):
        ws.cell(row=rn, column=col).fill   = tfill
        ws.cell(row=rn, column=col).border = bdr

    tl = ws.cell(row=rn, column=1, value="Total")
    tl.font = tfont
    tl.alignment = Alignment(horizontal="left", vertical="center")

    for col, val, fmt in [(4, uwt, '0.000'), (5, rqt, None), (6, gt, '0.000')]:
        c = ws.cell(row=rn, column=col, value=val)
        c.font = tfont; c.fill = tfill; c.alignment = ctr
        if fmt: c.number_format = fmt

    ws.column_dimensions["A"].width = 20; ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 18; ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 15; ws.column_dimensions["F"].width = 18

    fs = BytesIO()
    wb.save(fs); fs.seek(0)

    frappe.response['filename']    = "Drawing_Report.xlsx"
    frappe.response['filecontent'] = fs.getvalue()
    frappe.response['type']        = 'binary'



