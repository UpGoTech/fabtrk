# #### Copyright (c) 2026, UpGo Technologies and contributors
# #### For license information, please see license.txt

# ## import frappe
# ## from frappe.model.document import Document


# ## class FTDrawingParts(Document):
# ## 	pass


# import frappe
# import openpyxl
# import csv
# import os
# import json
# from frappe.model.document import Document

# class FTDrawingParts(Document):
#     pass

# # EXPORT
# @frappe.whitelist()
# def export_with_value():
#     import io
#     from openpyxl import Workbook
#     from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
#     from openpyxl.utils import get_column_letter

#     meta       = frappe.get_meta("FT Drawing Parts")
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

# # GET FILE HEADERS — for mapping dialog
# # @frappe.whitelist()
# # def get_file_headers(file_url):

# #     try:
# #         file_doc  = frappe.get_doc("File", {"file_url": file_url})
# #         file_path = file_doc.get_full_path()
# #     except Exception as e:
# #         frappe.throw(f"File nahi mili: {str(e)}")

# #     file_ext = os.path.splitext(file_url)[1].lower()
# #     headers  = []

# #     if file_ext == ".xlsx":
# #         wb      = openpyxl.load_workbook(file_path)
# #         ws      = wb.active
# #         headers = [str(c).strip() if c is not None else "" for c in next(ws.iter_rows(values_only=True))]
# #     elif file_ext == ".csv":
# #         with open(file_path, "r", encoding="utf-8-sig") as f:
# #             headers = [h.strip() for h in next(csv.reader(f))]
# #     else:
# #         frappe.throw("Sirf .xlsx ya .csv file allowed hai.")

# #     # Build label→fieldname map
# #     meta           = frappe.get_meta("FT Drawing Parts")
# #     label_to_field = {}
# #     for f in meta.fields:
# #         if f.label:
# #             label_to_field[f.label.strip()] = f.fieldname
# #         label_to_field[f.fieldname.strip()]  = f.fieldname

# #     # All available fields for dropdown
# #     all_fields = [
# #         {"label": f.label or f.fieldname, "fieldname": f.fieldname}
# #         for f in meta.fields
# #         if f.fieldtype not in ["Section Break", "Column Break", "HTML", "Heading"]
# #     ]

# #     matched   = {}
# #     unmatched = []

# #     for h in headers:
# #         if not h:
# #             continue
# #         if h in label_to_field:
# #             matched[h] = label_to_field[h]
# #         else:
# #             unmatched.append(h)

# #     return {
# #         "headers"   : headers,
# #         "matched"   : matched,
# #         "unmatched" : unmatched,
# #         "all_fields": all_fields
# #     }

# # @frappe.whitelist()
# # def get_file_headers(file_url):

# #     try:
# #         file_doc  = frappe.get_doc("File", {"file_url": file_url})
# #         file_path = file_doc.get_full_path()
# #     except Exception as e:
# #         frappe.throw(f"File not found: {str(e)}")

# #     file_ext = os.path.splitext(file_url)[1].lower()
# #     headers  = []

# #     if file_ext == ".xlsx":
# #         wb      = openpyxl.load_workbook(file_path)
# #         ws      = wb.active
# #         headers = [str(c).strip() if c is not None else "" for c in next(ws.iter_rows(values_only=True))]
# #     elif file_ext == ".csv":
# #         with open(file_path, "r", encoding="utf-8-sig") as f:
# #             headers = [h.strip() for h in next(csv.reader(f))]
# #     else:
# #         frappe.throw("Only .xlsx or .csv files are allowed.")

# #     # ✅ cached=False — new fields turant aayenge
# #     meta = frappe.get_meta("FT Drawing Parts", cached=False)

# #     label_to_field = {}
# #     for f in meta.fields:
# #         if f.label:
# #             label_to_field[f.label.strip()] = f.fieldname
# #         label_to_field[f.fieldname.strip()]  = f.fieldname

# #     # ✅ Raw label bhejo — None bhi theek hai, JS handle karega
# #     all_fields = [
# #         {"label": f.label, "fieldname": f.fieldname}
# #         for f in meta.fields
# #         if f.fieldtype not in ("Section Break", "Column Break", "HTML", "Heading")
# #     ]

# #     matched   = {}
# #     unmatched = []

# #     for h in headers:
# #         if not h:
# #             continue
# #         if h in label_to_field:
# #             matched[h] = label_to_field[h]
# #         else:
# #             unmatched.append(h)

# #     return {
# #         "headers"   : headers,
# #         "matched"   : matched,
# #         "unmatched" : unmatched,
# #         "all_fields": all_fields
# #     }
 
# # IMPORT
# @frappe.whitelist()
# def import_with_value(file_url, custom_mapping=None):

#     try:
#         file_doc  = frappe.get_doc("File", {"file_url": file_url})
#         file_path = file_doc.get_full_path()
#     except Exception as e:
#         frappe.throw(f"File nahi mili: {str(e)}")

#     rows     = []
#     file_ext = os.path.splitext(file_url)[1].lower()

#     if file_ext == ".xlsx":
#         try:
#             wb   = openpyxl.load_workbook(file_path)
#             ws   = wb.active
#             rows = list(ws.iter_rows(values_only=True))
#         except Exception as e:
#             frappe.throw(f"Excel open nahi hui: {str(e)}")
#     elif file_ext == ".csv":
#         try:
#             with open(file_path, "r", encoding="utf-8-sig") as f:
#                 rows = list(csv.reader(f))
#         except Exception as e:
#             frappe.throw(f"CSV open nahi hui: {str(e)}")
#     else:
#         frappe.throw("Sirf .xlsx ya .csv format ki file upload karo.")

#     if not rows:
#         frappe.throw("File mein koi data nahi hai.")

#     meta           = frappe.get_meta("FT Drawing Parts")
#     label_to_field = {}
#     for f in meta.fields:
#         if f.label:
#             label_to_field[f.label.strip()] = f.fieldname
#         label_to_field[f.fieldname.strip()]  = f.fieldname

#     # Merge custom mapping provided by user from mapping dialog
#     if custom_mapping:
#         extra = json.loads(custom_mapping) if isinstance(custom_mapping, str) else custom_mapping
#         label_to_field.update(extra)  # excel_label → fieldname

#     excel_headers = [str(h).strip() if h is not None else "" for h in rows[0]]

#     matched   = [h for h in excel_headers if h and label_to_field.get(h)]
#     unmatched = [h for h in excel_headers if h and not label_to_field.get(h)]

#     float_fields  = ["lenght", "width", "quantity", "single_weight", "total_weight", "painted_surface_percentage"]
#     string_fields = ["position_no", "part_no", "po_no"]

#     success = 0
#     errors  = []

#     for i, row in enumerate(rows[1:], start=2):
#         try:
#             d = {}

#             if not row or all(cell is None or str(cell).strip() == "" for cell in row):
#                 continue

#             for idx, excel_label in enumerate(excel_headers):
#                 if not excel_label:
#                     continue

#                 fieldname = label_to_field.get(excel_label.strip())
#                 if not fieldname:
#                     continue

#                 val = row[idx] if idx < len(row) else None

#                 if val is None or str(val).strip() == "":
#                     continue

#                 if fieldname in float_fields:
#                     try:
#                         val = float(val)
#                     except (ValueError, TypeError):
#                         errors.append(f"⚠️ Row {i}: {excel_label} '{val}' number nahi hai, skip kiya")
#                         continue

#                 elif fieldname in string_fields:
#                     val = str(val).strip()

#                 elif fieldname == "item":
#                     item_text = str(val).strip()
#                     item_id   = frappe.db.get_value("FT Stock RM List", {"computed_name": item_text}, "name")
#                     if not item_id:
#                         item_id = frappe.db.get_value("FT Stock RM List", {"name": item_text}, "name")
#                     if item_id:
#                         val = item_id
#                     else:
#                         errors.append(f"❌ Row {i}: Item '{item_text}' nahi mila — row skip")
#                         continue

#                 else:
#                     val = str(val).strip() if val else None

#                 d[fieldname] = val

#             if not d:
#                 continue

#             d.pop("name", None)

#             doc = frappe.new_doc("FT Drawing Parts")
#             doc.update(d)
#             doc.insert(ignore_permissions=True)
#             success += 1

#         except Exception as e:
#             errors.append(f"❌ Row {i}: {str(e)}")
#             frappe.log_error(title=f"FT Drawing Parts Import Error Row {i}", message=f"Row: {row}\nError: {str(e)}")

#     frappe.db.commit()

#     msg = f"✅ {success} records successfully import ho gaye.\n"
#     msg += f"\n📋 Matched fields ({len(matched)}): {', '.join(matched)}\n"
#     if unmatched:
#         msg += f"\n⚠️ Skip hue fields ({len(unmatched)}): {', '.join(unmatched)}\n"
#     if errors:
#         msg += f"\n❌ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
#         if len(errors) > 10:
#             msg += f"\n... aur {len(errors) - 10} errors"

#     return msg



import frappe
import openpyxl
import csv
import os
import json
from frappe.model.document import Document


class FTDrawingParts(Document):
    pass


# ------------- EXPORT -----------------
@frappe.whitelist()
def export_with_value():
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    # ✅ cached=False — naya field automatically export mein aayega
    meta       = frappe.get_meta("FT Drawing Parts", cached=False)
    fieldnames = [f.fieldname for f in meta.fields]
    records    = frappe.get_all("FT Drawing Parts", fields=fieldnames)

    headers = [(f.label or f.fieldname).upper() for f in meta.fields]

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

    wb = Workbook()
    ws = wb.active
    ws.title = "FT Drawing Parts"

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
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 35)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.local.response.filename    = "FT_Drawing_Parts.xlsx"
    frappe.local.response.filecontent = output.getvalue()
    frappe.local.response.type        = "binary"


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


# ------------- IMPORT --------------------- 
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

    msg = f"✅ {success} records successfully import ho gaye.\n"
    msg += f"\n📋 Matched fields ({len(matched)}): {', '.join(matched)}\n"
    if unmatched:
        msg += f"\n⚠️ Skip hue fields ({len(unmatched)}): {', '.join(unmatched)}\n"
    if errors:
        msg += f"\n❌ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
        if len(errors) > 10:
            msg += f"\n... aur {len(errors) - 10} errors"

    return msg

 