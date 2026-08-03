# IARS V4.5.12 — Self-Contained Warehouse Template Fix

## Root cause fixed
The deployed app could load the Warehouse module but could not find `assets/warehouse_conversion_template.xlsx`.

## Changes
- Embedded the approved Warehouse conversion template directly inside `iars_excel_conversion.py` as a fallback.
- The module still uses `assets/warehouse_conversion_template.xlsx` when present.
- If the asset is omitted during deployment, conversion continues using the embedded approved template.
- Updated visible application version to `4.5.12`.
- Retained the original template file in `assets/warehouse_conversion_template.xlsx`.
