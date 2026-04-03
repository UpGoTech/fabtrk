# # Only shown on plate 03.15 
# import frappe
# import ezdxf
# from io import StringIO

# @frappe.whitelist()
# def export_dxf(project, drawing, position, length, width):

#     length = float(length)
#     width = float(width)

#     # Create DXF
#     doc = ezdxf.new()
#     msp = doc.modelspace()

#     doc = ezdxf.new()
#     msp = doc.modelspace()

#     points = [
#         (0,0),
#         (length,0),
#         (length,width),
#         (0,width),
#     ]

#     msp.add_lwpolyline(points, close=True)

#     # Write DXF to text buffer
#     buffer = StringIO()
#     doc.write(buffer)

#     dxf_content = buffer.getvalue().encode("utf-8")

#     # Save file in Frappe
#     file_doc = frappe.get_doc({
#         "doctype": "File",
#         "file_name": f"{drawing}_{position}.dxf",
#         "content": dxf_content,
#         "is_private": 0
#     })

#     file_doc.save()

#     return file_doc.file_url







import json

def convert_to_contours(input_json):
    contours = []

    parts = input_json["Problem"]["Parts"]

    for part in parts:
        length = float(part["RectangularShape"]["Length"])
        width = float(part["RectangularShape"]["Width"])

        contour = {
            "Type": "Curve2CompositeClosed",
            "Data": {
                "Chunks": [
                    {
                        "Type": "PolylineBulge",
                        "Data": {
                            "Vertices": [
                                {"X": 0, "Y": 0},
                                {"X": length, "Y": 0},
                                {"X": length, "Y": width},
                                {"X": 0, "Y": width}
                            ]
                        }
                    }
                ]
            }
        }

        contours.append(contour)

    return {"ContoursEx": contours}
















# import frappe
# import ezdxf
# from io import StringIO

# @frappe.whitelist()
# def export_dxf(project, drawing, position, length, width):

#     length = float(length)
#     width = float(width)

#     # Create DXF
#     doc = ezdxf.new()
#     msp = doc.modelspace()

#     doc = ezdxf.new()
#     msp = doc.modelspace()

#     points = [
#         (0,0),
#         (length,0),
#         (length,width),
#         (0,width),
#     ]

#     msp.add_lwpolyline(points, close=True)

#     # Write DXF to text buffer
#     buffer = StringIO()
#     doc.write(buffer)

#     dxf_content = buffer.getvalue().encode("utf-8")

#     # Save file in Frappe
#     file_doc = frappe.get_doc({
#         "doctype": "File",
#         "file_name": f"{drawing}_{position}.dxf",
#         "content": dxf_content,
#         "is_private": 0
#     })

#     file_doc.save()

#     return file_doc.file_url


# import json

# def convert_to_contours(input_json):
    contours = []

    parts = input_json["Problem"]["Parts"]

    for part in parts:
        length = float(part["RectangularShape"]["Length"])
        width = float(part["RectangularShape"]["Width"])

        contour = {
            "Type": "Curve2CompositeClosed",
            "Data": {
                "Chunks": [
                    {
                        "Type": "PolylineBulge",
                        "Data": {
                            "Vertices": [
                                {"X": 0, "Y": 0},
                                {"X": length, "Y": 0},
                                {"X": length, "Y": width},
                                {"X": 0, "Y": width}
                            ]
                        }
                    }
                ]
            }
        }

        contours.append(contour)

    return {"ContoursEx": contours}