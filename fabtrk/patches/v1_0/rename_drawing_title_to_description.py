import frappe


def execute():
	if not frappe.db.table_exists("Fabrication Drawing"):
		return
	has_title = frappe.db.has_column("Fabrication Drawing", "title")
	has_description = frappe.db.has_column("Fabrication Drawing", "description")
	if has_title and not has_description:
		frappe.db.sql_ddl(
			"ALTER TABLE `tabFabrication Drawing` CHANGE `title` `description` varchar(140)"
		)
	elif has_title and has_description:
		frappe.db.sql(
			"""
			update `tabFabrication Drawing`
			set `description` = `title`
			where ifnull(`description`, '') = '' and ifnull(`title`, '') != ''
			"""
		)
		frappe.db.sql_ddl("ALTER TABLE `tabFabrication Drawing` DROP COLUMN `title`")
