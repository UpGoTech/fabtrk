# Spec progress

Numbered specs live in this folder. First spec is `00`. Next new spec is `01`, then `02`, and so on.

After each implementation phase, tick the matching items here and note the date. Do not mark a spec complete until its tracer path works on `fxl.localhost`.

## Spec index

| No | File | Title | Status |
| --- | --- | --- | --- |
| 00 | [00-fabrication-drawings.md](00-fabrication-drawings.md) | Fabrication drawings on ERPNext Project | Phase 1 (register) — 2026-08-24 |
| 01 | [01-project-form.md](01-project-form.md) | ERPNext Project form customization | Full form layout on site for review — 2026-08-25 |

## 00 — Fabrication drawings

### Branch and hooks

- [x] Branch `feat/fabrication-drawings` (created)
- [x] `required_apps = ["erpnext"]` in `fabtrk/hooks.py`
- [x] Project dashboard override: Connections show Fabrication Drawing and Fabrication Part

### DocTypes

- [x] Drawing Revision (child: file, letter, `is_current`)
- [x] Fabrication Drawing (project, drawing_no, `description`, Int `qty`, dates, customer PO line, `po_weight` in kg, Frappe system tags, priority, UDF 1–5)
- [x] Fabrication Part History (child snapshot)
- [x] Fabrication Part (1:N Link to drawing, `set_only_once`; line_no; source; dimension_type 1D/2D/Disc)
- [x] Unique piece_mark per drawing; unique line_no per drawing
- [x] Exactly one current drawing revision
- [x] Cannot delete a drawing that has parts
- [x] Workspace links: Project, Drawing, Part (Takeoff deferred until the report exists)
- [x] Standard Desktop Icon + Workspace Sidebar so Fabtrk appears on Desk after install
- [x] Fabtrk sidebar includes ERPNext Project (ships with the app)
- [x] Drop Fabrication Tag / Fabrication Drawing Tag; drawings use Frappe system tags
- [x] Drawing `qty` is Int (not Float); `title` renamed to `description`; PO Weight labelled (kg)

### Revise Part

- [ ] **Revise Part** button freezes current fields into history
- [ ] Sets `revised_in` to drawing current revision
- [ ] Does not auto-hold
- [ ] Blocks a second revise on the same drawing revision
- [ ] New drawing revision does not auto-revise or auto-hold parts

### Takeoff and Material Request

- [ ] Report **Project Material Takeoff**: group by Item; include source and line_no
- [ ] Totals use `drawing.qty × part.qty` (and length/weight products)
- [ ] Create Material Request: Purchase, project set; skip Client Supplied and parts with no Item

### Tests

- [x] Uniqueness (piece_mark, line_no)
- [x] Current drawing revision
- [ ] Takeoff math (`drawing.qty × part.qty`)
- [ ] MR lines skip Client Supplied
- [ ] Revise Part history freeze + double-revise blocked

### Tracer (`fxl.localhost`)

- [ ] Drawing 101, R0, description, PO weight (kg), Phase 1 system tag, qty 10
- [ ] Parts: 1D rod, Bought Out, 2D plate, Disc
- [ ] R1 on drawing; Revise Part on B1 only
- [ ] Takeoff + Create Material Request

### Out of 00 (do not tick as done in this spec)

Listed in the spec under **Explicitly out of v1** (shop floor, CSV/Tekla, packing list, conversion report, part status, Item variants, etc.).

## 01 — Project form

### Layout

- [x] Details: Project Name, Customer Name (reqd), Customer PO, Customer PO Date
- [x] Timeline: Start Date, End Date
- [x] Order Details: Order Qty (kg), Rate Per KG, Order Value (qty×rate), GST Rate, Assembly Percentage
- [x] Hide remaining stock Details / Costing / Progress / More Info fields; keep Connections
- [x] Billing and Shipping: Bill To, Ship To (multi), Transport Scope Self/Customer
- [x] Payment Terms: Advance, RM, Black Inspection, Final Invoice (Percent)
- [x] Form JS + validate for Order Value; Address queries by Customer
- [x] Child DocType Project Ship To; fixtures + `project_form_setup.sync`
- [ ] User review on Desk
- [ ] Commit (when asked)
