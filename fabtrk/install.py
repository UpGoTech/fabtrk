"""Installation helpers for FabTrk

This module creates required Role records when the app is installed or after
database migrations. All work is contained within the `fabtrk` app.
"""


def create_roles():
    """Create required roles used by FabTrk if they don't already exist.

    This function is referenced from `hooks.py` as both `after_install` and
    `after_migrate` to ensure roles are present after app install or a
    migration.
    """
    try:
        import frappe
    except Exception:
        # If frappe isn't available (static analysis/time of import), bail out.
        return

    roles = [
        "FT Planning",
        "FT Stores",
        "FT Purchase",
        "FT Production",
        "FT Contractor",
        "FT Gate",
    ]

    created = []
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            try:
                role = frappe.get_doc({"doctype": "Role", "role_name": role_name})
                role.insert(ignore_permissions=True)
                created.append(role_name)
            except Exception:
                # If insertion fails for any reason, continue with others.
                frappe.log_error(
                    f"Failed creating Role: {role_name}", "fabtrk.create_roles"
                )

    if created:
        # Persist and show a message in the UI when running via bench commands.
        frappe.db.commit()
        try:
            frappe.msgprint(f"FabTrk: Created roles: {', '.join(created)}")
        except Exception:
            # msgprint may not be available in all contexts; ignore.
            pass


def remove_roles():
    """Remove FabTrk roles when the app is uninstalled.

    This is registered as `before_uninstall` in `hooks.py`. The function
    attempts to delete each role and logs errors if deletion fails (for
    example, if the role is linked to users or permissions).
    """
    try:
        import frappe
    except Exception:
        return

    roles = [
        "FT Planning",
        "FT Stores",
        "FT Purchase",
        "FT Production",
        "FT Contractor",
        "FT Gate",
    ]

    removed = []
    for role_name in roles:
        if frappe.db.exists("Role", role_name):
            try:
                role = frappe.get_doc("Role", role_name)
                role.delete(ignore_permissions=True)
                removed.append(role_name)
            except Exception:
                # Log and continue with others
                frappe.log_error(
                    f"Failed removing Role: {role_name}", "fabtrk.remove_roles"
                )

    if removed:
        try:
            frappe.db.commit()
        except Exception:
            # If commit fails, nothing more we can do here
            pass
        try:
            frappe.msgprint(f"FabTrk: Removed roles: {', '.join(removed)}")
        except Exception:
            pass
