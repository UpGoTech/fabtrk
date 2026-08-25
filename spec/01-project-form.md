# 01 — ERPNext Project form customization

Status: applied on `fxl.localhost` for review. Track in [PROGRESS.md](PROGRESS.md).

Keep ERPNext Project as the job container. Customize its Desk form via FabTrk Custom Fields + Property Setters + form JS — do not fork ERPNext `project.json`.

Re-apply on a site after pull: `bench --site <site> migrate` then `bench --site <site> execute fabtrk.project_form_setup.sync`.

## Form layout (locked from review)

### Details

| Field | Type | Notes |
|-------|------|--------|
| Project Name | Data | stock `project_name` |
| Customer Name | Link → Customer | stock `customer`, **required**, relabeled |
| Customer PO | Data | `custom_customer_po` |
| Customer PO Date | Date | `custom_customer_po_date` |
| **Timeline** | Section | |
| Start Date | Date | stock `expected_start_date`, relabeled |
| End Date | Date | stock `expected_end_date`, relabeled |
| **Order Details** | Section | |
| Order Qty (kg) | Float | `custom_order_qty_kg` |
| Rate Per KG | Currency | `custom_rate_per_kg` |
| Order Value | Currency, read-only | `custom_order_value` = Qty × Rate (client + validate) |
| GST Rate | Percent | `custom_gst_rate` |
| Assembly Percentage | Data | `custom_assembly_percentage` |

All other stock Details / Costing / Progress / More Info fields are **hidden**. Series is hidden. **Connections** tab kept (Fabrication Drawing / Part).

### Billing and Shipping

| Field | Type | Notes |
|-------|------|--------|
| Bill To | Link → Address | filtered to Project Customer |
| Ship To | Table **Project Ship To** | multiple Address rows; filtered to Customer |
| **Transport Scope** | Section | |
| Transport Scope | Select | Self / Customer |

Changing Customer clears Bill To and Ship To rows.

### Payment Terms

| Field | Type | Notes |
|-------|------|--------|
| Advance | Percent | |
| RM | Percent | |
| Black Inspection | Percent | |
| Final Invoice | Percent | |

No sum-to-100 validation in this slice.

## Files

| Path | Role |
|------|------|
| [`fabtrk/project_form_setup.py`](../fabtrk/project_form_setup.py) | Idempotent sync of fields / hide / field_order |
| [`fabtrk/project_events.py`](../fabtrk/project_events.py) | `validate` → Order Value |
| [`fabtrk/public/js/project.js`](../fabtrk/public/js/project.js) | Order Value live calc; Address queries |
| [`fabtrk/fabtrk/doctype/project_ship_to/`](../fabtrk/fabtrk/doctype/project_ship_to/) | Child table for multiple Ship To |
| [`fabtrk/fixtures/custom_field.json`](../fabtrk/fixtures/custom_field.json) | Fixture export |
| [`fabtrk/fixtures/property_setter.json`](../fabtrk/fixtures/property_setter.json) | Fixture export |
| [`fabtrk/hooks.py`](../fabtrk/hooks.py) | `doctype_js`, `doc_events`, `fixtures` |

## Out of this slice

- Payment % must total 100
- Default drawing `customer_po_no` from Project Customer PO
- Restoring hidden ERPNext Project fields (Costing dashboard numbers, Users, Notes, etc.)
