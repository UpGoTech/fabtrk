# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.utils.xlsxutils import make_xlsx

# class FTStockRMList(Document):
# 	pass


import frappe
import openpyxl
import csv
import os
import json
from frappe.model.document import Document


class FTStockRMList(Document):
    pass


# EXPORT
@frappe.whitelist()
def export_with_value():
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    meta       = frappe.get_meta("FT Stock RM List")
    fieldnames = [f.fieldname for f in meta.fields]
    records    = frappe.get_all("FT Stock RM List", fields=fieldnames)

    headers = [(f.label or f.fieldname).upper() for f in meta.fields]

    data = []
    for d in records:
        row = []
        for field in fieldnames:
            value = d.get(field)
            if field == "grade" and value:
                value = frappe.db.get_value(
                    "FT Material Grade Catalogues", value, "grade"
                ) or value
            if field == "thk":
                value = "THK" if value in [1, True, "1"] else ""
            row.append(value if value is not None else "")
        data.append(row)

    wb = Workbook()
    ws = wb.active
    ws.title = "FT Stock RM List"

    header_fill  = PatternFill("solid", fgColor="BDD7EE")
    header_font  = Font(bold=True, size=10, color="000000")
    data_font    = Font(size=10)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
    thin         = Side(style="thin", color="000000")
    border       = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.append(headers)
    for cell in ws[1]:
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = center_align
        cell.border    = border

    ws.row_dimensions[1].height = 30
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"
    ws.freeze_panes   = "A2"

    for row_idx, row in enumerate(data, start=2):
        ws.append(row)
        fill_color = (
            PatternFill("solid", fgColor="FFFFFF")
            if row_idx % 2 == 0
            else PatternFill("solid", fgColor="F2F2F2")
        )
        for cell in ws[row_idx]:
            cell.fill      = fill_color
            cell.font      = data_font
            cell.border    = border
            cell.alignment = (
                center_align if isinstance(cell.value, (int, float)) else left_align
            )

    for col_idx, col_cells in enumerate(ws.columns, start=1):
        max_len = 0
        for cell in col_cells:
            try:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 40)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.local.response.filename    = "FT_Stock_RM_List.xlsx"
    frappe.local.response.filecontent = output.getvalue()
    frappe.local.response.type        = "binary"


# GET FILE HEADERS
@frappe.whitelist()
def get_file_headers(file_url):
    try:
        file_doc  = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
    except Exception as e:
        frappe.throw(f"File not found: {str(e)}")

    file_ext = os.path.splitext(file_url)[1].lower()
    headers  = []

    if file_ext == ".xlsx":
        wb      = openpyxl.load_workbook(file_path)
        ws      = wb.active
        headers = [str(c).strip() if c is not None else "" for c in next(ws.iter_rows(values_only=True))]
    elif file_ext == ".csv":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            headers = [h.strip() for h in next(csv.reader(f))]
    else:
        frappe.throw("Only .xlsx or .csv files are allowed.")

    meta = frappe.get_meta("FT Stock RM List", cached=False)

    label_to_field = {}
    for f in meta.fields:
        if f.label:
            label_to_field[f.label.strip()] = f.fieldname
        label_to_field[f.fieldname.strip()]  = f.fieldname

    all_fields = [
        {"label": f.label, "fieldname": f.fieldname}
        for f in meta.fields
        if f.fieldtype not in ("Section Break", "Column Break", "HTML", "Heading")
    ]

    matched   = {}
    unmatched = []

    for h in headers:
        if not h:
            continue
        if h in label_to_field:
            matched[h] = label_to_field[h]
        else:
            unmatched.append(h)

    return {
        "headers"   : headers,
        "matched"   : matched,
        "unmatched" : unmatched,
        "all_fields": all_fields
    }


# computed_name
def compute_name_python(d, grade_doc=None):
    section_type  = str(d.get("section_type") or "").strip()
    stock_rm_type = str(d.get("stock_rm_type") or "").strip()
    thk_val       = d.get("thk")
    thk_text      = "THK" if thk_val in [1, True, "1", "True"] else ""

    base_name = stock_rm_type
    size_part = ""

    if section_type == "Section":
        name1 = str(d.get("name1") or "").strip()
        if name1:
            size_part = name1 + (" " + thk_text if thk_text else "")

    elif section_type == "Plate":
        thickness = d.get("thickness_mm")
        if thickness is not None and str(thickness).strip() not in ["", "None"]:
            try:
                thickness_str = str(float(thickness))
                if thickness_str.endswith(".0"):
                    thickness_str = thickness_str[:-2]
                if "." in thickness_str:
                    parts         = thickness_str.split(".")
                    thickness_str = parts[0].zfill(2) + "." + parts[1]
                else:
                    thickness_str = thickness_str.zfill(2)
                size_part = thickness_str + (" " + thk_text if thk_text else "")
            except Exception as e:
                frappe.log_error(
                    title="compute_name thickness error",
                    message=f"thickness value: {thickness!r}, error: {e}"
                )

    if not grade_doc:
        return " ".join(filter(None, [base_name, size_part]))

    grade_display = str(grade_doc.get("grade") or "").strip()
    main_bis      = str(grade_doc.get("bis") or "").strip()
    type_bis      = str(
        (grade_doc.get("bis_section") if section_type == "Section"
         else grade_doc.get("bis_plate")) or ""
    ).strip()

    return " ".join(filter(None, [base_name, size_part, type_bis, main_bis, grade_display]))


# IMPORT — Dynamic with mapping support
@frappe.whitelist()
def import_with_value(file_url, custom_mapping=None):

    try:
        file_doc  = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
    except Exception as e:
        frappe.throw(f"File nahi mili: {str(e)}")

    rows     = []
    file_ext = os.path.splitext(file_url)[1].lower()

    if file_ext == ".xlsx":
        try:
            wb   = openpyxl.load_workbook(file_path)
            ws   = wb.active
            rows = list(ws.iter_rows(values_only=True))
        except Exception as e:
            frappe.throw(f"Excel open nahi hui: {str(e)}")
    elif file_ext == ".csv":
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                rows = list(csv.reader(f))
        except Exception as e:
            frappe.throw(f"CSV open nahi hui: {str(e)}")
    else:
        frappe.throw("Only .xlsx or .csv format ki file upload karo.")

    if not rows:
        frappe.throw("File mein koi data nahi hai.")

    meta = frappe.get_meta("FT Stock RM List", cached=False)

    label_to_field = {}
    for f in meta.fields:
        if f.label:
            label_to_field[f.label.strip()] = f.fieldname
        label_to_field[f.fieldname.strip()]  = f.fieldname

    if custom_mapping:
        extra = json.loads(custom_mapping) if isinstance(custom_mapping, str) else custom_mapping
        label_to_field.update(extra)

    float_fields  = ["thickness_mm", "kg__sqm", "kg__meter",
                     "surface_area_sqm__mtr", "surface_area_sqm__ton"]
    check_fields  = ["thk"]
    string_fields = ["name1", "stock_rm_type", "section_type"]

    excel_headers = [str(h).strip() if h is not None else "" for h in rows[0]]

    matched   = [h for h in excel_headers if h and label_to_field.get(h)]
    unmatched = [h for h in excel_headers if h and not label_to_field.get(h)]

    success = 0
    errors  = []

    for i, row in enumerate(rows[1:], start=2):
        try:
            d = {}

            if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                continue

            for idx, excel_label in enumerate(excel_headers):
                if not excel_label:
                    continue
                fieldname = label_to_field.get(excel_label.strip())
                if not fieldname:
                    continue

                val = row[idx] if idx < len(row) else None

                if fieldname in float_fields:
                    try:
                        val = float(val) if val not in [None, ""] else None
                    except:
                        val = None
                elif fieldname in check_fields:
                    val = 1 if val in [True, 1, "1", "True", "true"] else 0
                elif fieldname in string_fields:
                    val = str(val).strip() if val not in [None, ""] else None

                if val == "" or str(val) == "None":
                    val = None

                d[fieldname] = val

            if not any(v is not None for v in d.values()):
                continue

            # Grade lookup
            grade_doc = None
            if d.get("grade"):
                grade_id = frappe.db.get_value(
                    "FT Material Grade Catalogues",
                    {"grade": str(d["grade"]).strip()},
                    "name"
                )
                if grade_id:
                    grade_doc = frappe.db.get_value(
                        "FT Material Grade Catalogues",
                        grade_id,
                        ["grade", "bis", "bis_section", "bis_plate"],
                        as_dict=True
                    )
                    d["grade"] = grade_id
                else:
                    errors.append(f"⚠️ Row {i}: Grade '{d['grade']}' nahi mila — skipped")
                    continue

            # Computed name
            d["computed_name"] = compute_name_python(d, grade_doc)

            # Duplicate check
            existing = frappe.db.get_value(
                "FT Stock RM List",
                {"computed_name": d["computed_name"]},
                "name"
            )
            if existing:
                errors.append(f"⚠️ Row {i}: '{d['computed_name']}' already exists — skipped")
                continue

            d.pop("name", None)
            d.pop("naming_series", None)

            doc = frappe.new_doc("FT Stock RM List")
            doc.update(d)
            doc.insert(ignore_permissions=True)
            success += 1

        except Exception as e:
            errors.append(f"❌ Row {i}: {str(e)}")
            frappe.log_error(
                title=f"Import Error Row {i}",
                message=f"Row: {row}\nError: {str(e)}"
            )

    frappe.db.commit()

    msg = f"✅ {success} records import ho gaye."
    msg += f"\n\n📋 Matched fields ({len(matched)}): {', '.join(matched)}"
    if unmatched:
        msg += f"\n⚠️ Skip hue fields ({len(unmatched)}): {', '.join(unmatched)}"
    if errors:
        msg += f"\n\n❌/⚠️ {len(errors)} rows mein issue:\n" + "\n".join(errors)

    return msg