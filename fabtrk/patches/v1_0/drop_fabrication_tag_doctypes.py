import frappe


def execute():
	for dt in ("Fabrication Drawing Tag", "Fabrication Tag"):
		if not frappe.db.exists("DocType", dt):
			continue
		if frappe.db.table_exists(dt):
			frappe.db.delete(dt)
		frappe.delete_doc("DocType", dt, force=1, ignore_permissions=True)
