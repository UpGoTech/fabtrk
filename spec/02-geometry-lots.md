# 02 — Geometry lots (metal stock)

Status: vouchers, API, and reports are on `fxl.localhost` as of 2026-09-27. Sections 1–3 were not in the brief. Q1–Q10 are still unanswered. The build assumes one plant (Butibori) and warehouses `Main - FXL`, `Offcuts - FXL`, `Scrap - FXL`. Opening stock is not loaded.

Track in [PROGRESS.md](PROGRESS.md).

Tracer so far: pure geometry math in `fabtrk/geometry.py` (no Frappe import) and `fabtrk/test_geometry_logic.py`. Verified with `python -m unittest fabtrk.test_geometry_logic` (17 tests). Not yet on a site. DocTypes, hooks, API, reports, and opening stock are not built.

## 4. Why Batch and Serial No are rejected

**Batch.** A Batch is a fungible lot: a number, an expiry, and a quantity. It has no usable length or width. Custom fields on Batch cannot answer "find a remnant at least 600 × 400" without a full scan, and Batch semantics (one batch per item, batch-wise balances, batch pickers) fight the use case.

**Serial No.** A Serial No is one unit with warranty/recall identity. It has no geometry. One serial per piece is thousands of master records a year for material that has no serial meaning, and the damage shows up in Item forms, pickers, and stock reports.

**Serial and Batch Bundle.** Plumbing for serial/batch tracking, not an alternative. The app must not touch it. Validate loudly if a metal Item has `has_batch_no` or `has_serial_no` on.

**Correct shape.** Batch/Serial answers "which unit is this?". `Fabtrk Lot` answers "what geometry is this, how many identical pieces, how much does it weigh, where did it come from, and where did it go?".

## 5. Data model

Custom fields via fixtures. No core edits. No parallel Bin, SLE, or valuation. No GL. No geometry UOM. `qty_pieces` and `weight_kg` on a lot change only from a voucher submit/cancel or a lot movement.

### 5.1 Item custom fields

| Field | Type | Purpose |
|---|---|---|
| `fabtrk_grade` | Select (`E250`, `E350`, `SAILHARD400`, `HARDOX400`, `HARDOX500`) | Grade without parsing the SKU |
| `fabtrk_shape` | Select (`Plate`, `Angle`, `Channel`, `Beam`, `NPB`, `Pipe`, `Tube`, `Round Bar`, `Coil`, `Other`) | 1D vs 2D, report grouping |
| `fabtrk_thickness_mm` | Float | Plate thickness |
| `fabtrk_kg_per_metre` | Float | Section weight per metre |
| `fabtrk_default_length_mm` | Float | Standard bought length (informational) |
| `fabtrk_is_geometry_tracked` | Check | App manages lots only for these Items |

`fabtrk_is_geometry_tracked = 1` requires `stock_uom` in `Kg` or `MT`, `has_batch_no = 0`, `has_serial_no = 0`, Plate ⇒ thickness > 0, 1D shapes ⇒ kg per metre > 0.

### 5.1 Voucher child tables

One child table each on **Stock Entry** and **Purchase Receipt**, at voucher level (a line can split across lots):

`item_code`, `warehouse`, `length_mm` (per piece), `width_mm` (0 for solids), `qty_pieces`, `weight_kg`, `weight_basis` (`Kg Per Metre` / `Density` / `Weighment`), `weight_basis_source`, `source_reference`, `lot` (read-only; set on submit for receipts), `remarks`.

`item_code` must exist on the voucher. `warehouse` must match that item line.

### 5.2 Fabtrk Lot

Autoname `FABTRK-LOT-.YYYY.-.#####`. `track_changes = 1`. One row per distinct geometry held.

`item_code` (reqd). Fetched: `item_name`, `stock_uom`, `fabtrk_grade`, `fabtrk_shape`, `fabtrk_thickness_mm`. `warehouse`. `division` (see Q1). `stock_group` (`Full Stock` / `Offcut Stock` / `Scrap`, derived from warehouse). `length_mm` (per piece, reqd). `width_mm`. `qty_pieces` and `weight_kg` (cache of the movement table). `kg_per_piece` (read-only average, labelled avg). `weight_basis`, `weight_basis_source` (required for Kg Per Metre and Density). `density_kg_m3` from settings. `lot_type` (`Parent` / `Offcut` / `Scrap`). `status` (`In Stock` / `Consumed` / `Scrapped` / `Transferred Out`). `parent_lot`. `source_doctype`, `source_document`, `source_reference`. `origin_job` (see Q8). `received_on`. `valuation_rate` at permlevel 1.

### 5.3 Fabtrk Lot Movement

Append-only. Never edited or deleted. `track_changes = 1`, `in_create = 1`. One row per lot per voucher.

`lot`, `posting_date`, `voucher_type`, `voucher_no`, `item_code`, `warehouse`, signed `qty_pieces`, `length_mm`, `width_mm`, signed `weight_kg`, `resulting_qty_pieces`, `resulting_weight_kg`, mandatory `reference`, `reason` (mandatory for adjustments), `actor`, `remarks`.

### 5.4 Fabtrk Settings

`default_density_kg_m3` (7850). `weight_deviation_warn_pct` (5). `weight_deviation_block_pct` (10). `allow_negative_stock` (0; only Fabtrk Stock Owner may change it). `consume_policy` (`Offcut First then FIFO` default, `FIFO`, `Explicit Only`). `scrap_min_length_mm`, `scrap_min_width_mm`. `enforce_offcut_creation` (1).

### 5.5 Do not build

No custom Bin, SLE, valuation, or quantity-on-hand table. No reimplementation of Item, UOM, Warehouse, or valuation. No Serial No, Batch, or Serial and Batch Bundle on metal items. No hand-edits of lot qty/weight. No GL. No geometry UOM.

## 6. Units and weight

Stock UOM is `Kg`. `MT` is `kg / 1000` for reporting only.

1. `Kg Per Metre`: `length_mm / 1000 × fabtrk_kg_per_metre × qty_pieces`
2. `Density`: `(length_mm / 1000) × (width_mm / 1000) × (thickness_mm / 1000) × density × qty_pieces`. Density comes from settings, never a code constant.
3. `Weighment`: scale figure, overrides calculation, stored as such.

Warn above 5%, block above 10%. Do not silently correct. Round for display only.

`total_length_mm = SUM(length_mm * qty_pieces)`. Never `SUM(length_mm)`. `kg_per_piece` on a multi-piece lot is an average and must be labelled avg.

Checked figures (density 7850, 10 mm plate, unrounded): 5800×1500 = 682.95 kg (display 683.0) vs invoiced 686.7; 8000×1500 = 942 vs 940; 6300×1500 = 741.825; 4000×1500 = 471; 2300×1500 = 270.825.

## 7. Transactions

Hooks `on_submit` and `on_cancel` in the same DB transaction. Geometry is entered on Purchase Receipt or Stock Entry.

- **Receipt** (Purchase Receipt, or Stock Entry Material Receipt): at least one lot row per tracked item line. Sum of lot weights matches the line qty within tolerance. Warehouses match. Group lots by item, warehouse, length, width, weight basis, and origin. Positive movements. Mandatory reference. Reject duplicate `(voucher_type, reference, item, geometry)` and name the existing document.
- **Issue** (Material Issue, or Material Transfer to WIP): operator selects lots. Default follows `consume_policy`. Refuse the whole voucher if pieces exceed the lot or weight exceeds Bin. Status `Consumed` at zero; never delete. Negative movements. Capture `origin_job` when known.
- **Return:** receipt against a prior issue, linked by reference.
- **Offcut:** consumed geometry and remainder on the same voucher. New lot `lot_type = Offcut`, warehouse `Offcuts - FXL`, `parent_lot` set, weight basis inherited. Below scrap minima, suggest Scrap (overridable with a reason). Same voucher moves weight on the native side: consumed Main → WIP, reusable remainder Main → Offcuts, unusable remainder Main → Scrap. Use Repack only if the remainder gets its own item code (Q2). Conservation warns, does not block: `issued ≈ offcut + scrap + consumed`. A remnant is never both inside an unconsumed parent and a separate offcut lot.
- **Transfer:** move warehouse, write a movement.
- **Adjustment:** dated movement, mandatory reason, matched by an equal native weight adjustment. Removal is an Issue. Corrections are a compensating pair.
- **Cancel:** reverse movements. Do not delete lots.

## 8. Roles

| Role | Rights |
|---|---|
| Fabtrk Stock Owner | Everything, including cancel, adjustments, masters, settings, cost |
| Fabtrk Stock Storekeeper | Submit receipts, issues, transfers, offcuts, scrap, returns. No cancel, no master edits, no adjustments, no cost |
| Fabtrk Stock Viewer | Read lots, movements, reports |

`valuation_rate` at permlevel 1. `track_changes = 1` on every app doctype. `reference` mandatory; `reason` mandatory on adjustments. No System Manager for day-to-day work.

## 9. API

Token auth. Whitelist in `fabtrk/api.py`: `post_receipt`, `post_issue`, `post_transfer`, `post_adjustment`, `stock_by_geometry`, `lot_search`, `lot_trace`, `reconcile`, `import_opening_lots`.

Every write carries `reference`. Re-posting the same `(voucher_type, reference)` returns the existing name and writes nothing. Enforce in the database. Every write returns document name, item, geometry, pieces, kg/MT change, resulting lot balance, Bin balance, and validation flags. `dry_run: 1` runs validation and returns that receipt without writing.

## 10. Migration

Source `/opt/data/fxlstock/fxlstock.db`, table `transactions`: 22 rows, 15 SKUs, 78 pieces, 77,866.6 kg, 21 receipts + 1 issue, location Butibori. Do not load until Q1 and Q5 are answered. Do not recreate `PL-SAILHARD400-10MM` or `PL-E350-12MM`; validate them. Do not create pipe/tube/round-bar items until Q4. HSN is a GST-consultant decision. After migration the prototype is read-only.

## 11. Reports

R1 Stock by Geometry, R2 Availability, R3 Offcut Search, R4 Lot Traceability, R5 Per-SKU ledger, R6 Job-wise issues, R7 Reconciliation (daily, alert on drift), R8 Offcut ageing, R9 native negative/reorder filtered to tracked items. Build R1, R2, R3, R5, R7 before dashboard polish. Script reports, not Query Reports, where geometry joins are needed.

## 12. Acceptance criteria

- **AC-1.** `PL-E350-10MM`, 6 × 5800×1500 = 4,120 kg and 1 × 8000×1500 = 940 kg, reference `INV AS/077/26-27`. Exactly 2 lots. Bin 5,060 kg. Two movements.
- **AC-2.** R1 shows those two size rows. Totals 7 pcs, 5,060 kg, 5.060 MT.
- **AC-3.** After AC-1, total length 42,800 mm. Issue 3 × 5800×1500 (2,060 kg) → 25,400 mm, weight 3,000 kg, Bin 3,000 kg. Bare `SUM(length_mm)` fails the test.
- **AC-4.** 6300×1500 (741.8 kg) cut to 4000×1500 leaves Offcut 2300×1500 in Offcuts, parent decremented. 471.0 + 270.8 ≈ 741.8.
- **AC-5.** Issue 8 from a 6-piece lot: voucher rejected, available quantity named, no Stock Entry, no lot change.
- **AC-6.** Same reference twice creates nothing the second time.
- **AC-7.** 12% off calculated weight blocks with both figures and the basis. 6% saves with a warning.
- **AC-8.** Viewer can open R1/R3/R5 and cannot post or edit a lot. Storekeeper can submit receipt and issue, cannot cancel, cannot edit Item, cannot see `valuation_rate`.
- **AC-9.** After opening stock, R7 is 0.00 kg drift and total is 77,866.6 kg / 78 pieces.
- **AC-10.** Every movement has voucher, reference, actor, timestamp. Version trail on every app doctype.
- **AC-11.** No Serial No, Batch, or Serial and Batch Bundle for tracked items. Turning on `has_batch_no` warns.
- **AC-12.** Write methods return the update receipt. `dry_run = 1` does not write.

Pure rules stay in a module with no Frappe import. DocType wiring is tested with `bench --site fxl.localhost run-tests --app fabtrk`.

## 13. Deployment

Staging first. Fixtures: Custom Fields, Property Setters, Roles, Fabtrk Settings, Reports, charts, Workspace. Backup before opening stock. No ERPNext core patches, no monkey patches.

## 14. Open questions

- **Q1 (blocking).** Is Butibori the only plant, or are there two divisions? Warehouses `Main` / `Offcuts` / `Scrap` do not exist. Migration waits on this.
- **Q2.** Offcut keeps the same `item_code` (recommended) rather than a `-OFFCUT` item.
- **Q3.** Offcut valued at a proportional parent rate (recommended) or at zero.
- **Q4.** Do not create unconfirmed round-bar, pipe, or tube SKUs.
- **Q5.** Opening-stock as-of date. The 22 rows may be live stock or an old ledger.
- **Q6.** API first, voucher child-table UI second (recommended).
- **Q7.** Plain Lot doctype plus append-only movements (recommended), not a submittable Lot.
- **Q8.** `origin_job` as Project link or free text. Project is not readable by the API user.
- **Q9.** Invoiced steel arrives as Purchase Receipt (recommended), not Purchase Invoice with update stock.
- **Q10.** Prototype stays read-only or is retired. Not a second write path.

## Assumptions in the math module

These are local readings, not answers to Q1–Q10:

- Scrap is suggested when length is under `scrap_min_length_mm`, or when width is non-zero and under `scrap_min_width_mm`. A section (`width_mm = 0`) is judged on length only.
- `Coil` and `Other` do not require kg per metre. Angle, Channel, Beam, NPB, Pipe, Tube, and Round Bar do.
- Warn and block fire when the deviation is **greater than** the configured percent.
