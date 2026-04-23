# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class FTDrawingParts(Document):
# 	pass

import frappe
import openpyxl
import csv
import os
import json
from frappe.model.document import Document


class FTDrawingParts(Document):
    # pass
    def before_save(self):
        self.calculate_total_weight()
        self.calculate_surface_areas()

    def calculate_total_weight(self):
        quantity = float(self.quantity or 0)
        single_weight = float(self.single_weight or 0)
        self.total_weight = quantity * single_weight

    def calculate_surface_areas(self):
        if not self.item:
            self.single_unit_surface_area = "0"
            self.total_surface_area = "0"
            return

        pct = float(self.painted_surface_percentage or 0)
        if not pct:
            self.single_unit_surface_area = "0"
            self.total_surface_area = "0"
            return

        # FT Stock RM List se section_type aur surface_area fetch karo
        item_data = frappe.db.get_value(
            "FT Stock RM List",
            self.item,
            ["section_type", "surface_area_sqm__mtr"],
            as_dict=True
        )

        if not item_data:
            self.single_unit_surface_area = "0"
            self.total_surface_area = "0"
            return

        section_type = item_data.get("section_type") or ""
        surface_area_sqm_mtr = float(item_data.get("surface_area_sqm__mtr") or 0)

        lenght = float(self.lenght or 0)
        width = float(self.width or 0)
        quantity = float(self.quantity or 0)

        length_m = lenght / 1000  # mm → meters
        area_sqm = 0.0

        if section_type == "Plate":
            width_m = width / 1000  # mm → meters
            area_sqm = length_m * width_m * 2  # both sides
        else:
            area_sqm = length_m * surface_area_sqm_mtr

        single_result = area_sqm * (pct / 100)

        self.single_unit_surface_area = "{:.4f}".format(single_result)
        self.total_surface_area = "{:.4f}".format(single_result * quantity)
        
  
# ------------- EXPORT -----------------
# @frappe.whitelist()
# def export_with_value():
#     import io
#     from openpyxl import Workbook
#     from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
#     from openpyxl.utils import get_column_letter

#     # ✅ cached=False — naya field automatically export mein aayega
#     meta       = frappe.get_meta("FT Drawing Parts", cached=False)
#     fieldnames = [f.fieldname for f in meta.fields]
#     records    = frappe.get_all("FT Drawing Parts", fields=fieldnames)

#     headers = [(f.label or f.fieldname).upper() for f in meta.fields]

#     data = []
#     for d in records:
#         row = []
#         for field in fieldnames:
#             value = d.get(field)
#             if field == "item" and value:
#                 value = frappe.db.get_value("FT Stock RM List", value, "computed_name") or value
#             if field == "drawing_number" and value:
#                 value = frappe.db.get_value("FT Add Drawing", value, "name") or value
#             if field == "project_number" and value:
#                 value = frappe.db.get_value("FT Project", value, "name") or value
#             row.append(value if value is not None else "")
#         data.append(row)

#     wb = Workbook()
#     ws = wb.active
#     ws.title = "FT Drawing Parts"

#     header_fill  = PatternFill("solid", fgColor="BDD7EE")
#     header_font  = Font(bold=True, size=10, color="000000")
#     data_font    = Font(size=10)
#     center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
#     left_align   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
#     thin         = Side(style="thin", color="000000")
#     border       = Border(left=thin, right=thin, top=thin, bottom=thin)

#     ws.append(headers)
#     for cell in ws[1]:
#         cell.fill      = header_fill
#         cell.font      = header_font
#         cell.alignment = center_align
#         cell.border    = border

#     ws.row_dimensions[1].height = 30
#     ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"
#     ws.freeze_panes   = "A2"

#     for row_idx, row in enumerate(data, start=2):
#         ws.append(row)
#         fill_color = (
#             PatternFill("solid", fgColor="FFFFFF")
#             if row_idx % 2 == 0
#             else PatternFill("solid", fgColor="F2F2F2")
#         )
#         for cell in ws[row_idx]:
#             cell.fill      = fill_color
#             cell.font      = data_font
#             cell.border    = border
#             cell.alignment = (
#                 center_align if isinstance(cell.value, (int, float)) else left_align
#             )

#     for col_idx, col_cells in enumerate(ws.columns, start=1):
#         max_len = 0
#         for cell in col_cells:
#             try:
#                 if cell.value:
#                     max_len = max(max_len, len(str(cell.value)))
#             except:
#                 pass
#         ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 35)

#     output = io.BytesIO()
#     wb.save(output)
#     output.seek(0)

#     frappe.local.response.filename    = "FT_Drawing_Parts.xlsx"
#     frappe.local.response.filecontent = output.getvalue()
#     frappe.local.response.type        = "binary"


# # ye all working code hai bas iss mai filtered mai jab item select karne ke bad uski value nahi id aa rahi hai..
# @frappe.whitelist()
# def export_with_value(file_type="xlsx", export_type="all", filters=None, selected_fields=None):
#     import io
#     import csv as csv_module
#     from openpyxl import Workbook
#     from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
#     from openpyxl.utils import get_column_letter

#     meta = frappe.get_meta("FT Drawing Parts", cached=False)

#     if selected_fields:
#         sf_list = json.loads(selected_fields) if isinstance(selected_fields, str) else selected_fields
#     else:
#         sf_list = [f.fieldname for f in meta.fields]

#     field_label_map = {}
#     for f in meta.fields:
#         field_label_map[f.fieldname] = (f.label or f.fieldname)
#     field_label_map["name"] = "ID"

#     valid_fieldnames = ["name"] + [f.fieldname for f in meta.fields]
#     fieldnames = [fn for fn in sf_list if fn in valid_fieldnames]

#     if not fieldnames:
#         frappe.throw("No fields selected for export.")

#     headers_original = [field_label_map.get(fn, fn) for fn in fieldnames]
#     headers_upper    = [h.upper() for h in headers_original]

#     # ── Records fetch ──
#     if export_type == "blank":
#         records = []
#     else:
#         query_kwargs = {"fields": fieldnames}

#         if export_type == "filtered" and filters:
#             if isinstance(filters, str):
#                 parsed = json.loads(filters)
#             else:
#                 parsed = filters

#             from collections import defaultdict
#             equals_groups = defaultdict(list)
#             other_filters = []

#             for f in parsed:
#                 if not isinstance(f, list):
#                     continue
#                 if len(f) == 4:
#                     _, field, op, value = f
#                 elif len(f) == 3:
#                     field, op, value = f
#                 else:
#                     continue

#                 if op in ('=', 'Equals', 'equals'):
#                     equals_groups[field].append(value)
#                 else:
#                     other_filters.append([field, op, value])

#             clean_filters = []
#             for field, values in equals_groups.items():
#                 if len(values) == 1:
#                     clean_filters.append([field, '=', values[0]])
#                 else:
#                     clean_filters.append([field, 'in', values])
#             for f in other_filters:
#                 clean_filters.append(f)

#             query_kwargs["filters"] = clean_filters if clean_filters else []

#         elif export_type == "5":
#             query_kwargs["limit"] = 5

#         records = frappe.get_all("FT Drawing Parts", **query_kwargs)

#     # ── Build rows ──
#     data = []
#     for d in records:
#         row = []
#         for field in fieldnames:
#             value = d.get(field)
#             if field == "item" and value:
#                 value = frappe.db.get_value("FT Stock RM List", value, "computed_name") or value
#             if field == "drawing_number" and value:
#                 value = frappe.db.get_value("FT Add Drawing", value, "name") or value
#             if field == "project_number" and value:
#                 value = frappe.db.get_value("FT Project", value, "name") or value
#             row.append(value if value is not None else "")
#         data.append(row)

#     # ── CSV — original case headers sab ke liye ──
#     if file_type == "csv":
#         output = io.StringIO()
#         writer = csv_module.writer(output)
#         writer.writerow(headers_original)
#         writer.writerows(data)
#         frappe.local.response.filename    = "FT_Drawing_Parts.csv"
#         frappe.local.response.filecontent = output.getvalue().encode("utf-8-sig")
#         frappe.local.response.type        = "binary"
#         return

#     wb = Workbook()
#     ws = wb.active
#     ws.title = "FT Drawing Parts"

#     # ── Blank Template ──
#     if export_type == "blank":
#         ws.append(headers_original)
#         for col_idx in range(1, len(headers_original) + 1):
#             ws.column_dimensions[get_column_letter(col_idx)].width = 20
#         output = io.BytesIO()
#         wb.save(output)
#         output.seek(0)
#         frappe.local.response.filename    = "FT_Drawing_Parts_Template.xlsx"
#         frappe.local.response.filecontent = output.getvalue()
#         frappe.local.response.type        = "binary"
#         return

#     # ── Styled Excel ──
#     header_fill  = PatternFill("solid", fgColor="BDD7EE")
#     header_font  = Font(bold=True, size=10, color="000000")
#     data_font    = Font(size=10)
#     center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
#     left_align   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
#     thin         = Side(style="thin", color="000000")
#     border       = Border(left=thin, right=thin, top=thin, bottom=thin)

#     ws.append(headers_upper)
#     for cell in ws[1]:
#         cell.fill      = header_fill
#         cell.font      = header_font
#         cell.alignment = center_align
#         cell.border    = border

#     ws.row_dimensions[1].height = 30

#     # ── Auto-filter ONLY for "all" ──
#     if export_type == "all":
#         ws.auto_filter.ref = f"A1:{get_column_letter(len(headers_upper))}1"

#     ws.freeze_panes = "A2"

#     for row_idx, row in enumerate(data, start=2):
#         ws.append(row)
#         fill_color = (
#             PatternFill("solid", fgColor="FFFFFF")
#             if row_idx % 2 == 0
#             else PatternFill("solid", fgColor="F2F2F2")
#         )
#         for cell in ws[row_idx]:
#             cell.fill      = fill_color
#             cell.font      = data_font
#             cell.border    = border
#             cell.alignment = (
#                 center_align if isinstance(cell.value, (int, float)) else left_align
#             )

#     for col_idx, col_cells in enumerate(ws.columns, start=1):
#         max_len = 0
#         for cell in col_cells:
#             try:
#                 if cell.value:
#                     max_len = max(max_len, len(str(cell.value)))
#             except:
#                 pass
#         ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 35)

#     output = io.BytesIO()
#     wb.save(output)
#     output.seek(0)
#     frappe.local.response.filename    = "FT_Drawing_Parts.xlsx"
#     frappe.local.response.filecontent = output.getvalue()
#     frappe.local.response.type        = "binary"


@frappe.whitelist()
def export_with_value(file_type="xlsx", export_type="all", filters=None, selected_fields=None):
    import io
    import csv as csv_module
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    meta = frappe.get_meta("FT Drawing Parts", cached=False)

    if selected_fields:
        sf_list = json.loads(selected_fields) if isinstance(selected_fields, str) else selected_fields
    else:
        sf_list = [f.fieldname for f in meta.fields]

    field_label_map = {}
    for f in meta.fields:
        field_label_map[f.fieldname] = (f.label or f.fieldname)
    field_label_map["name"] = "ID"

    valid_fieldnames = ["name"] + [f.fieldname for f in meta.fields]
    fieldnames = [fn for fn in sf_list if fn in valid_fieldnames]

    if not fieldnames:
        frappe.throw("No fields selected for export.")

    headers_original = [field_label_map.get(fn, fn) for fn in fieldnames]
    headers_upper    = [h.upper() for h in headers_original]

    # ── Records fetch ──
    if export_type == "blank":
        records = []
    else:
        query_kwargs = {"fields": fieldnames}

        if export_type == "filtered" and filters:
            if isinstance(filters, str):
                parsed = json.loads(filters)
            else:
                parsed = filters

            from collections import defaultdict
            equals_groups = defaultdict(list)
            other_filters = []

            for f in parsed:
                if not isinstance(f, list):
                    continue
                if len(f) == 4:
                    _, field, op, value = f
                elif len(f) == 3:
                    field, op, value = f
                else:
                    continue

                if op in ('=', 'Equals', 'equals'):
                    equals_groups[field].append(value)
                else:
                    other_filters.append([field, op, value])

            clean_filters = []
            for field, values in equals_groups.items():
                if len(values) == 1:
                    clean_filters.append([field, '=', values[0]])
                else:
                    clean_filters.append([field, 'in', values])
            for f in other_filters:
                clean_filters.append(f)

            # ── Item field: computed_name → actual name convert ──
            final_filters = []
            for f in clean_filters:
                if isinstance(f, list) and len(f) == 3 and f[0] == 'item':
                    field, op, value = f
                    if op == '=':
                        item_name = frappe.db.get_value(
                            'FT Stock RM List', {'computed_name': value}, 'name'
                        )
                        final_filters.append([field, op, item_name or value])
                    elif op == 'in':
                        item_names = []
                        for v in value:
                            item_name = frappe.db.get_value(
                                'FT Stock RM List', {'computed_name': v}, 'name'
                            )
                            item_names.append(item_name or v)
                        final_filters.append([field, op, item_names])
                    else:
                        final_filters.append(f)
                else:
                    final_filters.append(f)

            query_kwargs["filters"] = final_filters if final_filters else []

        elif export_type == "5":
            query_kwargs["limit"] = 5

        records = frappe.get_all("FT Drawing Parts", **query_kwargs)

    # ── Build rows ──
    data = []
    for d in records:
        row = []
        for field in fieldnames:
            value = d.get(field)
            if field == "item" and value:
                value = frappe.db.get_value("FT Stock RM List", value, "computed_name") or value
            if field == "drawing_number" and value:
                value = frappe.db.get_value("FT Add Drawing", value, "name") or value
            if field == "project_number" and value:
                value = frappe.db.get_value("FT Project", value, "name") or value
            row.append(value if value is not None else "")
        data.append(row)

    # ── CSV — original case headers sab ke liye ──
    if file_type == "csv":
        output = io.StringIO()
        writer = csv_module.writer(output)
        writer.writerow(headers_original)
        writer.writerows(data)
        frappe.local.response.filename    = "FT_Drawing_Parts.csv"
        frappe.local.response.filecontent = output.getvalue().encode("utf-8-sig")
        frappe.local.response.type        = "binary"
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "FT Drawing Parts"

    # ── Blank Template ──
    if export_type == "blank":
        ws.append(headers_original)
        for col_idx in range(1, len(headers_original) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 20
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        frappe.local.response.filename    = "FT_Drawing_Parts_Template.xlsx"
        frappe.local.response.filecontent = output.getvalue()
        frappe.local.response.type        = "binary"
        return

    # ── Styled Excel ──
    header_fill  = PatternFill("solid", fgColor="BDD7EE")
    header_font  = Font(bold=True, size=10, color="000000")
    data_font    = Font(size=10)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
    thin         = Side(style="thin", color="000000")
    border       = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.append(headers_upper)
    for cell in ws[1]:
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = center_align
        cell.border    = border

    ws.row_dimensions[1].height = 30

    # ── Auto-filter sirf "all" pe ──
    if export_type == "all":
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers_upper))}1"

    ws.freeze_panes = "A2"

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
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 35)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    frappe.local.response.filename    = "FT_Drawing_Parts.xlsx"
    frappe.local.response.filecontent = output.getvalue()
    frappe.local.response.type        = "binary"


# DISTINCT VALUES — filter autocomplete ke liye
@frappe.whitelist()
def get_field_distinct_values(fieldname, search_text=None):
    meta = frappe.get_meta("FT Drawing Parts", cached=False)
    valid_fields = [f.fieldname for f in meta.fields] + ["name"]

    if fieldname not in valid_fields:
        frappe.throw("Invalid fieldname")

    where_clauses = [f"`{fieldname}` IS NOT NULL", f"`{fieldname}` != ''"]
    params = {}

    if search_text:
        where_clauses.append(f"`{fieldname}` LIKE %(s)s")
        params["s"] = f"%{search_text}%"

    sql = f"""
        SELECT DISTINCT `{fieldname}`
        FROM `tabFT Drawing Parts`
        WHERE {' AND '.join(where_clauses)}
        ORDER BY `{fieldname}` ASC
    """

    rows = frappe.db.sql(sql, params)
    return [str(r[0]) for r in rows if r[0] is not None]


#------------- GET FILE HEADERS ---------------- 
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

    # ✅ cached=False
    meta = frappe.get_meta("FT Drawing Parts", cached=False)

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


# IMPORT — 100% DYNAMIC — zero hardcoded lists
@frappe.whitelist()
def import_with_value(file_url, custom_mapping=None):

    try:
        file_doc  = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
    except Exception as e:
        frappe.throw(f"File not found: {str(e)}")

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

    # ✅ cached=False — fresh meta
    meta = frappe.get_meta("FT Drawing Parts", cached=False)

    # ✅ DYNAMIC: label → fieldname map
    label_to_field = {}
    for f in meta.fields:
        if f.label:
            label_to_field[f.label.strip()] = f.fieldname
        label_to_field[f.fieldname.strip()]  = f.fieldname

    # ✅ DYNAMIC: custom mapping merge
    if custom_mapping:
        extra = json.loads(custom_mapping) if isinstance(custom_mapping, str) else custom_mapping
        label_to_field.update(extra)

    # ✅ DYNAMIC: fieldname → fieldtype map (hardcoded list ki jagah)
    field_type_map = {}
    for f in meta.fields:
        field_type_map[f.fieldname] = f.fieldtype

    # ✅ DYNAMIC: fieldname → Link options map (hardcoded item/drawing/project ki jagah)
    link_options_map = {}
    for f in meta.fields:
        if f.fieldtype == "Link" and f.options:
            link_options_map[f.fieldname] = f.options.strip()

    # ✅ DYNAMIC: konse fieldtypes float accept karte hain
    numeric_types = ("Float", "Currency", "Percent", "Int")

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

                if val is None or str(val).strip() == "":
                    continue

                # ✅ DYNAMIC: numeric conversion — fieldtype se detect
                ftype = field_type_map.get(fieldname, "")
                if ftype in numeric_types:
                    try:
                        val = float(val)
                        if ftype == "Int":
                            val = int(val)
                    except (ValueError, TypeError):
                        errors.append(f"⚠️ Row {i}: {excel_label} '{val}' is not a valid number, skipped")
                        continue

                # ✅ DYNAMIC: Link field lookup — options se detect
                elif ftype == "Link":
                    link_doctype = link_options_map.get(fieldname, "")
                    text_val = str(val).strip()

                    if link_doctype == "FT Stock RM List":
                        # Try computed_name first, then name
                        item_id = frappe.db.get_value("FT Stock RM List", {"computed_name": text_val}, "name")
                        if not item_id:
                            item_id = frappe.db.get_value("FT Stock RM List", {"name": text_val}, "name")
                        if item_id:
                            val = item_id
                        else:
                            errors.append(f"❌ Row {i}: {excel_label} '{text_val}' not found in {link_doctype} — row skipped")
                            continue

                    elif link_doctype == "FT Add Drawing":
                        doc_id = frappe.db.get_value("FT Add Drawing", {"name": text_val}, "name")
                        if doc_id:
                            val = doc_id
                        else:
                            errors.append(f"❌ Row {i}: {excel_label} '{text_val}' not found in {link_doctype} — row skipped")
                            continue

                    elif link_doctype == "FT Project":
                        doc_id = frappe.db.get_value("FT Project", {"name": text_val}, "name")
                        if doc_id:
                            val = doc_id
                        else:
                            errors.append(f"❌ Row {i}: {excel_label} '{text_val}' not found in {link_doctype} — row skipped")
                            continue

                    else:
                        # ✅ DYNAMIC: koi bhi nayi Link field — generic lookup
                        doc_id = frappe.db.get_value(link_doctype, {"name": text_val}, "name")
                        if doc_id:
                            val = doc_id
                        else:
                            errors.append(f"❌ Row {i}: {excel_label} '{text_val}' not found in {link_doctype} — row skipped")
                            continue

                else:
                    # ✅ Data, Small Text, Text etc — string
                    val = str(val).strip() if val else None

                d[fieldname] = val

            if not d:
                continue

            d.pop("name", None)

            doc = frappe.new_doc("FT Drawing Parts")
            doc.update(d)
            doc.insert(ignore_permissions=True)
            success += 1

        except Exception as e:
            errors.append(f"❌ Row {i}: {str(e)}")
            frappe.log_error(title=f"FT Drawing Parts Import Error Row {i}", message=f"Row: {row}\nError: {str(e)}")

    frappe.db.commit()

    msg = f"✅ {success} records successfully import.\n"
    msg += f"\n📋 Matched fields ({len(matched)}): {', '.join(matched)}\n"
    if unmatched:
        msg += f"\n⚠️ Skip hue fields ({len(unmatched)}): {', '.join(unmatched)}\n"
    if errors:
        msg += f"\n❌ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
        if len(errors) > 10:
            msg += f"\n... aur {len(errors) - 10} errors"

    return msg

