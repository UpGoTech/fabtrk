# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.utils.xlsxutils import make_xlsx

# class FTStockRMList(Document):
# 	pass


import frappe
import openpyxl
from frappe.model.document import Document
from frappe.utils.xlsxutils import make_xlsx


class FTStockRMList(Document):
    pass


# ─────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────
@frappe.whitelist()
def export_with_value():

    meta       = frappe.get_meta("FT Stock RM List")
    fieldnames = [f.fieldname for f in meta.fields]
    records    = frappe.get_all("FT Stock RM List", fields=fieldnames)

    data = [fieldnames]

    for d in records:
        row = []
        for field in fieldnames:
            value = d.get(field)
            if field == "grade" and value:
                value = frappe.db.get_value(
                    "FT Material Grade Catalogues", value, "grade"
                )
            row.append(value)
        data.append(row)

    xlsx_file = make_xlsx(data, "FT Stock RM List")
    frappe.local.response.filename    = "FT_Stock_RM_List.xlsx"
    frappe.local.response.filecontent = xlsx_file.getvalue()
    frappe.local.response.type        = "binary"


# ─────────────────────────────────────────
# computed_name — FIXED (int+str error fix)
# ─────────────────────────────────────────
def compute_name_python(d, grade_doc=None):

    section_type  = str(d.get("section_type") or "").strip()
    stock_rm_type = str(d.get("stock_rm_type") or "").strip()
    thk_val       = d.get("thk")
    thk_text      = "THK" if thk_val in [1, True, "1", "True"] else ""

    base_name = stock_rm_type
    size_part = ""

    if section_type == "Section":
        # ✅ FIX — name1 ko str() mein wrap karo
        name1 = str(d.get("name1") or "").strip()
        if name1:
            size_part = name1 + (" " + thk_text if thk_text else "")

    elif section_type == "Plate":
        thickness = d.get("thickness_mm")
        if thickness is not None and str(thickness).strip() not in ["", "None"]:
            try:
                # ✅ FIX — pehle float, phir string
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


# ─────────────────────────────────────────
# IMPORT
# ─────────────────────────────────────────
@frappe.whitelist()
def import_with_value(file_url):

    try:
        file_doc  = frappe.get_doc("File", {"file_url": file_url})
        file_path = file_doc.get_full_path()
    except Exception as e:
        frappe.throw(f"File nahi mili: {str(e)}")

    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
    except Exception as e:
        frappe.throw(f"Excel open nahi hui: {str(e)}")

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        frappe.throw("File mein koi data nahi hai.")

    meta           = frappe.get_meta("FT Stock RM List")
    label_to_field = {f.label.strip(): f.fieldname for f in meta.fields}
    excel_headers  = [str(h).strip() if h is not None else "" for h in rows[0]]

    matched   = [h for h in excel_headers if h and label_to_field.get(h)]
    unmatched = [h for h in excel_headers if h and not label_to_field.get(h)]

    float_fields = [
        "thickness_mm", "kg__sqm", "kg__meter",
        "surface_area_sqm__mtr", "surface_area_sqm__ton"
    ]
    check_fields = ["thk"]

    # ✅ String fields — Excel number de toh str karo
    string_fields = ["name1", "stock_rm_type", "section_type"]

    success = 0
    errors  = []

    for i, row in enumerate(rows[1:], start=2):

        try:
            d = {}

            for idx, excel_label in enumerate(excel_headers):
                if not excel_label:
                    continue

                fieldname = label_to_field.get(excel_label.strip())
                if not fieldname:
                    continue

                val = row[idx] if idx < len(row) else None

                # Float
                if fieldname in float_fields:
                    try:
                        val = float(val) if val not in [None, ""] else None
                    except:
                        val = None

                # Check
                elif fieldname in check_fields:
                    val = 1 if val in [True, 1, "1", "True", "true"] else 0

                # ✅ String fields — int/float → str convert
                elif fieldname in string_fields:
                    val = str(val).strip() if val not in [None, ""] else None

                # Empty → None
                if val == "" or str(val) == "None":
                    val = None

                d[fieldname] = val

            # Empty row skip
            if not any(v is not None for v in d.values()):
                continue

            # Grade value → MGC ID
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
                    errors.append(f"Row {i}: Grade '{d['grade']}' nahi mila — skip")
                    continue

            # computed_name set
            d["computed_name"] = compute_name_python(d, grade_doc)

            d.pop("name", None)
            d.pop("naming_series", None)

            doc = frappe.new_doc("FT Stock RM List")
            doc.update(d)
            doc.insert(ignore_permissions=True)

            success += 1

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
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
        msg += f"\n\n❌ {len(errors)} rows mein error:\n" + "\n".join(errors)

    return msg

