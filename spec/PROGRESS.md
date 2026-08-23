# Spec progress

Numbered specs live in this folder. First spec is `00`. Next new spec is `01`, then `02`, and so on.

After each implementation phase, tick the matching items here and note the date. Do not mark a spec complete until its tracer path works on `fxl.localhost`.

## Spec index

| No | File | Title | Status |
| --- | --- | --- | --- |
| 00 | [00-fabrication-drawings.md](00-fabrication-drawings.md) | Fabrication drawings on ERPNext Project | Not started |

## 00 — Fabrication drawings

### Branch and hooks

- [ ] Branch `feat/fabrication-drawings` (created)
- [ ] `required_apps = ["erpnext"]` in `fabtrk/hooks.py`
- [ ] Project dashboard override: Connections show Fabrication Drawing and Fabrication Part

### DocTypes

- [ ] Fabrication Tag
- [ ] Fabrication Drawing Tag (Table MultiSelect child)
- [ ] Drawing Revision (child: file, letter, `is_current`)
- [ ] Fabrication Drawing (project, drawing_no, qty, dates, customer PO line, tags, priority, UDF 1–5)
- [ ] Fabrication Part History (child snapshot)
- [ ] Fabrication Part (1:N Link to drawing, `set_only_once`; line_no; source; dimension_type 1D/2D/Disc)
- [ ] Unique piece_mark per drawing; unique line_no per drawing
- [ ] Exactly one current drawing revision
- [ ] Cannot delete a drawing that has parts
- [ ] Workspace links: Drawing, Part, Takeoff

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

- [ ] Uniqueness (piece_mark, line_no)
- [ ] Current drawing revision
- [ ] Takeoff math (`drawing.qty × part.qty`)
- [ ] MR lines skip Client Supplied
- [ ] Revise Part history freeze + double-revise blocked

### Tracer (`fxl.localhost`)

- [ ] Drawing 101, R0, PO fields, Phase 1 tag, qty 10
- [ ] Parts: 1D rod, Bought Out, 2D plate, Disc
- [ ] R1 on drawing; Revise Part on B1 only
- [ ] Takeoff + Create Material Request

### Out of 00 (do not tick as done in this spec)

Listed in the spec under **Explicitly out of v1** (shop floor, CSV/Tekla, packing list, conversion report, part status, Item variants, etc.).
