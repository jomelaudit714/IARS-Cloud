# Verification — IARS V4.5.14

## Actual uploaded Invoice sample
- 85 `INV` rows captured.
- LOGP number resolved as `61005123`.
- Employee resolved as `Rey Van Laurente Davido`.
- Invoice dates ranged from 2026-06-23 through 2026-06-26.
- Every output `docu_date` matched the corresponding source INV row's column C.
- Source row order was preserved.
- Column E products mapped to `prod_name`; apostrophes were removed.
- Column F quantities mapped to `inv_qty`; negative values were retained.
- Column G mapped to `prod_uom`.
- Column J mapped to `inv_no`.
- Blank output columns remained blank.

## Repeated testing
- 120 repeated end-to-end conversions passed after the final code changes.
- 60 runs used the physical `invoice_conversion_template.xlsx` asset.
- 60 runs used the embedded template fallback with the physical template path intentionally missing.

## Regression and package checks
- Invoice synthetic tests passed.
- LOGP regression tests passed.
- Warehouse regression tests passed.
- Python compilation passed for `app.py`, `iars_auth.py`, and `iars_excel_conversion.py`.
- Output workbook inspection found no formula errors.
