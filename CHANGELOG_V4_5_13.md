# IARS V4.5.13 — Sales Personnel LOGP Conversion

## Added
- Enabled `Excel Conversion > Sales Personnel > LOGP` in the sidebar.
- Added SAP LOGP `.xlsx` upload, validation, preview and download.
- Added approved template asset: `assets/logp_conversion_template.xlsx`.
- Added an embedded template fallback in `iars_excel_conversion.py` so conversion still works if the asset is omitted during deployment.
- Kept `Sales Personnel > Invoice` as a disabled next-project placeholder.

## Confirmed conversion rules
- `Item Description` → `prod_name`, with apostrophes removed.
- `UoM Name` → `prod_uom`; blank remains blank.
- First `Quantity` column → `record_qty`.
- `Warehouse/ASR` → official `employee_name` from Master Data Employees.
- The converter prioritizes `A01AMB01`; when the source legitimately starts with another item, it starts at the first valid product row below the headers.
- `login_date` uses the Philippine conversion date.
- `docu_date`, `logp_no`, `docu_name` and `remarks` are parsed from the filename.
- `Regular` maps to `Good`; `Good`, `Sotex` and `Sold Out` are supported.
- Blank output fields remain blank as required.
- The signed-in user's full name becomes `auditor_name`.

## Version
- Header and System Settings version updated to `4.5.13`.
