import frappe

def get_context(context):
    pass


@frappe.whitelist()
def create_event(subject, starts_on, ends_on=None, description=None):
    if not subject or not starts_on:
        return {"success": False}

    event = frappe.new_doc("Event")
    event.subject = subject
    event.starts_on = starts_on
    event.ends_on = ends_on
    event.description = description
    event.insert(ignore_permissions=True)

    return {"success": True, "name": event.name}


@frappe.whitelist()
def add_participant(event, name, email=None, phone=None):
    p = frappe.new_doc("Event Participant")
    p.event = event
    p.participant_name = name
    p.participant_email = email
    p.participant_phone = phone
    p.insert(ignore_permissions=True)
