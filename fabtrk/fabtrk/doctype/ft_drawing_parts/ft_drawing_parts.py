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
from frappe.model.document import Document
from frappe.utils.xlsxutils import make_xlsx


class FTDrawingParts(Document):
    pass


# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
@frappe.whitelist()
def export_with_value():
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    meta       = frappe.get_meta("FT Drawing Parts")
    fieldnames = [f.fieldname for f in meta.fields]
    records    = frappe.get_all("FT Drawing Parts", fields=fieldnames)

    # ── Build data rows ──────────────────────────────
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

    # ── Create Workbook ──────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = "FT Drawing Parts"

    # ── Styles ──────────────────────────────────────
    header_fill   = PatternFill("solid", fgColor="BDD7EE")   # Light blue like image
    filter_fill   = PatternFill("solid", fgColor="D9E1F2")   
    header_font   = Font(bold=True, size=10, color="000000")
    data_font     = Font(size=10)
    center_align  = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align    = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ── Row 1: Header (fieldnames as labels) ────────
    headers = []
    for f in meta.fields:
        headers.append((f.label or f.fieldname).upper())

    ws.append(headers)
    header_row = ws[1]
    for cell in header_row:
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = center_align
        cell.border    = border

    # ── Row 2: Filter indicator row (▼ dropdown look) ──
    filter_row_data = ["▼"] * len(headers)
    ws.append(filter_row_data)
    for cell in ws[2]:
        cell.fill      = filter_fill
        cell.font      = Font(bold=True, size=9, color="595959")
        cell.alignment = center_align
        cell.border    = border

    # Enable AutoFilter on header row
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    # ── Data rows ───────────────────────────────────
    for row_idx, row in enumerate(data, start=3):
        ws.append(row)
        # Alternate row color
        fill_color = PatternFill("solid", fgColor="FFFFFF") if row_idx % 2 == 1 else PatternFill("solid", fgColor="F2F2F2")
        for col_idx, cell in enumerate(ws[row_idx], start=1):
            cell.fill   = fill_color
            cell.font   = data_font
            cell.border = border
            # Numbers center, text left
            if isinstance(cell.value, (int, float)):
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    # ── Column widths (auto-fit) ─────────────────────
    for col_idx, col_cells in enumerate(ws.columns, start=1):
        max_len = 0
        for cell in col_cells:
            try:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            except:
                pass
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 35)

    # ── Row heights ──────────────────────────────────
    ws.row_dimensions[1].height = 30  
    ws.row_dimensions[2].height = 18   

    # ── Freeze top 2 rows ───────────────────────────
    ws.freeze_panes = "A3"

    # ── Save & Return ────────────────────────────────
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    frappe.local.response.filename    = "FT_Drawing_Parts.xlsx"
    frappe.local.response.filecontent = output.getvalue()
    frappe.local.response.type        = "binary"


# ─────────────────────────────────────────
# IMPORT
# ─────────────────────────────────────────
@frappe.whitelist()
def import_with_value(file_url):

    try:
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
    except Exception as e:
        frappe.throw(f"File nahi mili: {str(e)}")

    rows = []
    file_ext = os.path.splitext(file_url)[1].lower()

    # XLSX Handling
    if file_ext == ".xlsx":
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
        except Exception as e:
            frappe.throw(f"Excel open nahi hui: {str(e)}")
    
    # CSV Handling
    elif file_ext == ".csv":
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            frappe.throw(f"CSV open nahi hui: {str(e)}")
    
    else:
        frappe.throw("Sirf .xlsx ya .csv format ki file upload karo.")

    if not rows:
        frappe.throw("File mein koi data nahi hai.")

    # Get meta and field mapping
    meta = frappe.get_meta("FT Drawing Parts")
    
    # Create mapping: Label -> Fieldname
    label_to_field = {}
    for f in meta.fields:
        if f.label:
            label_to_field[f.label.strip()] = f.fieldname
        # Also add fieldname itself
        if f.fieldname:
            label_to_field[f.fieldname.strip()] = f.fieldname
    
    excel_headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    
    # Debug: Log headers
    frappe.log_error(
        title="Import Debug - Headers",
        message=f"Excel Headers: {excel_headers}\nAvailable Labels: {list(label_to_field.keys())}"
    )
    
    matched = []
    unmatched = []
    
    for h in excel_headers:
        if h and h in label_to_field:
            matched.append(h)
        elif h:
            unmatched.append(h)

    float_fields = ["lenght", "width", "quantity", "single_weight", "total_weight", "painted_surface_percentage"]
    string_fields = ["position_no", "part_no", "po_no"]

    success = 0
    errors = []

    for i, row in enumerate(rows[1:], start=2):
        try:
            d = {}
            
            # Skip empty rows
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

                # Handle float fields
                if fieldname in float_fields:
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        errors.append(f"⚠️ Row {i}: {excel_label} '{val}' number nahi hai, skip kiya")
                        continue
                
                # Handle string fields
                elif fieldname in string_fields:
                    val = str(val).strip()
                
                # Handle item field (Link to FT Stock RM List)
                elif fieldname == "item":
                    if val:
                        item_text = str(val).strip()
                        # First try to find by computed_name
                        item_id = frappe.db.get_value(
                            "FT Stock RM List",
                            {"computed_name": item_text},
                            "name"
                        )
                        # If not found, try by name directly
                        if not item_id:
                            item_id = frappe.db.get_value(
                                "FT Stock RM List",
                                {"name": item_text},
                                "name"
                            )
                        
                        if item_id:
                            val = item_id
                        else:
                            errors.append(f"❌ Row {i}: Items '{item_text}' FT Stock RM List mein nahi mila — row skip")
                            continue  # Skip this row
                    else:
                        continue
                
                else:
                    val = str(val).strip() if val else None

                d[fieldname] = val

            if not d:
                continue

            # Remove auto fields
            d.pop("name", None)
            
            # Debug: Log what we're importing
            frappe.log_error(
                title=f"Import Row {i} - Data",
                message=f"Row {i} Data: {d}"
            )

            # Create and insert document
            doc = frappe.new_doc("FT Drawing Parts")
            doc.update(d)
            doc.insert(ignore_permissions=True)
            
            success += 1

        except Exception as e:
            errors.append(f"❌ Row {i}: {str(e)}")
            frappe.log_error(
                title=f"FT Drawing Parts Import Error Row {i}",
                message=f"Row: {row}\nError: {str(e)}"
            )

    frappe.db.commit()

    # Prepare response message
    msg = f"✅ {success} records successfully import ho gaye.\n"
    msg += f"\n📋 Matched fields ({len(matched)}): {', '.join(matched)}\n"
    
    if unmatched:
        msg += f"\n⚠️ Skip hue fields ({len(unmatched)}): {', '.join(unmatched)}\n"
    
    if errors:
        msg += f"\n❌ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
        if len(errors) > 10:
            msg += f"\n... aur {len(errors) - 10} errors"

    return msg



