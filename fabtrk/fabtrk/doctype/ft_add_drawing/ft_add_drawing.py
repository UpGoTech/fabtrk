# # Copyright (c) 2026, UpGo Technologies and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document


# class FTAddDrawing(Document):
# 	pass


class FTAddDrawing(Document):
    def validate(self):
        self.validate_duplicate_drawing_per_project()

    def validate_duplicate_drawing_per_project(self):
        exists = frappe.db.exists(
            "Add Drawing",
            {
                "project_number": self.project_number,
                "drawing_number": self.drawing_number,
                "name": ["!=", self.name]  # update case handle
            }
        )

        if exists:
            frappe.throw(
                f"Drawing Number <b>{self.drawing_number}</b> already exists for Project <b>{self.project_number}</b>"
            )
