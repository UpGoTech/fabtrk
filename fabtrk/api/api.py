# Only shown on plate 03.15 
import frappe
import ezdxf
from io import StringIO

@frappe.whitelist()
def export_dxf(project, drawing, position, length, width):

    length = float(length)
    width = float(width)

    # Create DXF
    doc = ezdxf.new()
    msp = doc.modelspace()

    doc = ezdxf.new()
    msp = doc.modelspace()

    points = [
        (0,0),
        (length,0),
        (length,width),
        (0,width),
    ]

    msp.add_lwpolyline(points, close=True)

    # Write DXF to text buffer
    buffer = StringIO()
    doc.write(buffer)

    dxf_content = buffer.getvalue().encode("utf-8")

    # Save file in Frappe
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": f"{drawing}_{position}.dxf",
        "content": dxf_content,
        "is_private": 0
    })

    file_doc.save()

    return file_doc.file_url




# import frappe
# import ezdxf
# from io import StringIO


# def draw_plate(msp, length, width):
#     msp.add_line((0,0), (length,0))
#     msp.add_line((length,0), (length,width))
#     msp.add_line((length,width), (0,width))
#     msp.add_line((0,width), (0,0))


# def draw_angle(msp, leg1, leg2, thickness=6):
#     pts = [
#         (0,0),
#         (leg1,0),
#         (leg1,thickness),
#         (thickness,thickness),
#         (thickness,leg2),
#         (0,leg2)
#     ]
#     msp.add_lwpolyline(pts, close=True)


# def draw_channel(msp, width, height, thickness=6):
#     pts = [
#         (0,0),
#         (width,0),
#         (width,thickness),
#         (thickness,thickness),
#         (thickness,height-thickness),
#         (width,height-thickness),
#         (width,height),
#         (0,height)
#     ]
#     msp.add_lwpolyline(pts, close=True)


# def draw_pipe(msp, diameter):
#     radius = diameter / 2
#     msp.add_circle((0,0), radius)


# def draw_flat(msp, length, width):
#     draw_plate(msp, length, width)


# @frappe.whitelist()
# def export_dxf(project, drawing, position, length, width, item):

#     length = float(length)
#     width = float(width)

#     section_type = frappe.db.get_value(
#         "FT Stock RM List",
#         item,
#         "stock_rm_type"
#     )

#     doc = ezdxf.new()
#     doc.units = ezdxf.units.MM
#     msp = doc.modelspace()

#     if section_type == "Plate":
#         draw_plate(msp, length, width)

#     elif section_type == "Angle":
#         draw_angle(msp, length, width)

#     elif section_type == "Channel":
#         draw_channel(msp, length, width)

#     elif section_type == "Pipe":
#         draw_pipe(msp, width)

#     elif section_type == "Flat":
#         draw_flat(msp, length, width)

#     else:
#         frappe.throw(f"Unsupported section type: {section_type}")

#     buffer = StringIO()
#     doc.write(buffer)

#     dxf_content = buffer.getvalue().encode("utf-8")

#     file_doc = frappe.get_doc({
#         "doctype": "File",
#         "file_name": f"{drawing}_{position}.dxf",
#         "content": dxf_content,
#         "is_private": 0
#     })

#     file_doc.save()

#     return file_doc.file_url



# import frappe
# import ezdxf
# from io import StringIO


# def draw_1d_part(msp, length):
#     msp.add_line((0, 0), (length, 0))


# @frappe.whitelist()
# def export_dxf(project, drawing, position, length, width, item):

#     length = float(length)

#     if length <= 0:
#         frappe.throw("Length must be greater than zero")

#     doc = ezdxf.new("R12")
#     doc.units = ezdxf.units.MM
#     msp = doc.modelspace()

#     draw_1d_part(msp, length)

#     buffer = StringIO()
#     doc.write(buffer)

#     dxf_content = buffer.getvalue().encode("utf-8")

#     file_doc = frappe.get_doc({
#         "doctype": "File",
#         "file_name": f"{drawing}_{position}.dxf",
#         "content": dxf_content,
#         "is_private": 0
#     })

#     file_doc.save()

#     return file_doc.file_url