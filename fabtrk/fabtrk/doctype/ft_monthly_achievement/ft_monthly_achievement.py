# -*- coding: utf-8 -*-
# Copyright (c) 2026, UpGo Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from decimal import Decimal, InvalidOperation


class FTMonthlyAchievement(Document):

    def validate(self):
        if not self.total_weight_for_project_achieved or self.total_weight_for_project_achieved <= 0:
            frappe.throw("Total weight for Project Achieved must be greater than 0")

        self.calculate_and_validate_balance()

    def calculate_and_validate_balance(self):
        if not self.project_number or not self.select_month:
            return

        if not self.target_set_for_the_month:
            frappe.throw("Target set for the Month is required")

        try:
            target = Decimal(self.target_set_for_the_month)
            current = Decimal(self.total_weight_for_project_achieved)
        except InvalidOperation:
            frappe.throw("Invalid number format")

        achieved = frappe.db.sql("""
            SELECT COALESCE(SUM(total_weight_for_project_achieved), 0)
            FROM `tabFT Monthly Achievement`
            WHERE project_number = %s
              AND select_month = %s
              AND name != %s
        """, (
            self.project_number,
            self.select_month,
            self.name or ""
        ))[0][0]

        achieved = Decimal(achieved)
        remaining = target - achieved

        if current > remaining:
            frappe.throw(f"""
                <table class="table table-bordered" style="margin-top: 10px; width: 100%;">
                    <tbody>
                        <tr>
                            <td><strong>Target set for the Month</strong></td>
                            <td class="text-right">{target} Kg</td>
                        </tr>
                        <tr>
                            <td><strong>Already Achieved</strong></td>
                            <td class="text-right">{achieved} Kg</td>
                        </tr>
                        <tr class="text-success">
                            <td><strong>Remaining Balance</strong></td>
                            <td class="text-right"><strong>{remaining} Kg</strong></td>
                        </tr>
                        <tr class="text-danger">
                            <td><strong>You Entered</strong></td>
                            <td class="text-right"><strong>{current} Kg</strong></td>
                        </tr>
                    </tbody>
                </table>
            """, title="Invalid Entry")

        self.project_balance = remaining - current


@frappe.whitelist()
def get_already_achieved(select_month, project_number, docname=None):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(total_weight_for_project_achieved), 0)
        FROM `tabFT Monthly Achievement`
        WHERE project_number = %s
          AND select_month = %s
          AND name != %s
    """, (project_number, select_month, docname or ""))
    
    return result[0][0] if result else 0


@frappe.whitelist()
def get_monthly_total_weight(month_target, project_number):
    result = frappe.db.sql("""
        SELECT ct.total_weight_of_project
        FROM `tabFT Month Target Childtable` ct
        WHERE ct.parent = %s
          AND ct.project_number = %s
    """, (month_target, project_number))

    return result[0][0] if result else 0


@frappe.whitelist()
def check_project_weight(year, select_month, project_number, current_value, docname=None, actual_weight=None):
    from decimal import Decimal

    if actual_weight is None:
        actual_weight = frappe.db.get_value(
            "FT Monthly Achievement",
            {"project_number": project_number, "select_month": select_month, "year": year},
            "target_set_for_the_month"
        )
        if not actual_weight:
            return {"status": "error", "message": "Target set for the Month not found"}

    target = Decimal(actual_weight)
    current = Decimal(current_value or 0)

    achieved = frappe.db.sql("""
        SELECT SUM(total_weight_for_project_achieved)
        FROM `tabFT Monthly Achievement`
        WHERE project_number = %(project)s
          AND select_month = %(month)s
          AND year = %(year)s
          AND name != %(name)s
    """, {
        "project": project_number,
        "month": select_month,
        "year": year,
        "name": docname or ""
    })[0][0] or 0

    achieved = Decimal(achieved)
    remaining = target - achieved

    if remaining <= 0:
        return {
            "status": "full",
            "actual": str(target),
            "achieved": str(achieved),
            "balance": 0
        }

    if current > remaining:
        return {
            "status": "exceed",
            "actual": str(target),
            "achieved": str(achieved),
            "balance": str(remaining)
        }

    return {
        "status": "ok",
        "actual": str(target),
        "achieved": str(achieved),
        "balance": str(remaining - current)
    }


@frappe.whitelist()
def get_months_by_year(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name
        FROM `tabFT Monthly Target`
        WHERE name LIKE %(txt)s
        ORDER BY 
            year DESC,
            FIELD(select_month,
                'December', 'November', 'October', 'September',
                'August', 'July', 'June', 'May',
                'April', 'March', 'February', 'January'
            )
    """, {"txt": f"%{txt}%"})


@frappe.whitelist()
def get_projects_by_year_month(doctype, txt, searchfield, start, page_len, filters):
    year = filters.get("year")
    month_docname = filters.get("month")
    
    if not year or not month_docname:
        return []

    return frappe.db.sql("""
        SELECT DISTINCT ct.project_number
        FROM `tabFT Month Target Childtable` ct
        WHERE ct.parent = %s
          AND ct.project_number LIKE %s
        ORDER BY ct.project_number
    """, (month_docname, f"%{txt}%"))