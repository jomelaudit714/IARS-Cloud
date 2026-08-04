# IARS V4.5.14 — Sales Personnel Invoice Conversion

## Added
- Enabled **Excel Conversion → Sales Personnel → Invoice** in the sidebar.
- Added SAP Invoice upload, validation, preview, and compatible Excel download.
- Added `assets/invoice_conversion_template.xlsx` based on the approved output file.
- Added an embedded copy of the Invoice template as a deployment fallback.

## Confirmed Invoice rules
- Convert only source rows with `INV` in column A.
- `docu_date`: each INV row's own date from source column C.
- `prod_name`: source column E, with straight and curly apostrophes removed.
- `inv_qty`: source column F; negative quantities are retained.
- `prod_uom`: source column G.
- `inv_no`: source column J.
- `logp_no`: number from column B beside a `LOGP` marker in column A, repeated across output rows.
- `employee_name`: resolved from the uploaded filename through Employees Master Data.
- `remarks`: read from filename (`Good`, `Regular` → `Good`, `Sotex`, or `Sold Out`).
- `auditor_name`: signed-in IARS user's full name in column R.
- Source INV row order is preserved.
- `trans_id`, `sold_no`, `pd_no`, `prod_code`, `disc_qty`, `record_qty`, and `count_qty` remain blank.

## Retained
- Warehouse conversion module.
- Sales Personnel LOGP conversion module.
- Existing authentication, branding, navigation, and other IARS modules from V4.5.13.
