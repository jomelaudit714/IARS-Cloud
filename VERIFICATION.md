# Verification — IARS V4.5.11

## Code and package checks

- Python compilation passed for `app.py`, `iars_auth.py`, `iars_theme.py`, and `iars_excel_conversion.py`.
- AST parsing passed for all four Python files.
- App integration assertions passed for:
  - `Excel Conversion` sidebar group
  - active `Warehouse` page
  - disabled `LOGP` and `Invoice` placeholders under Sales Personnel
  - Warehouse page dispatch
  - visible version `4.5.11`
- V4.5.10 approved `iars_auth.py`, `iars_theme.py`, login artwork, sidebar artwork, and EDL logo hashes are unchanged.

## Warehouse conversion checks

- Tested with `Cebu Good Stocks EPLSI.xlsx`.
- Tested with `Cebu Damage Warehouse EPLSI(1).xlsx`.
- Captured exactly 119 rows in each sample.
- Generated the approved 13-column `For Uploading` worksheet.
- Verified `CEB260731-EPLSI`, `EPLSI-GS`, and `EPLSI-DW` generation.
- Verified duplicate filename suffix removal such as `(1)` and `(42)`.
- Verified product capture begins at `A01AMB01` and excludes the `Whse:` row.
- Verified apostrophe removal, including straight and curly apostrophes.
- Verified blank UoM remains blank and record quantity stays aligned.
- Verified `id` and `count_qty` remain blank.
- Verified date columns use `yyyy-mm-dd`; all other output columns use `General`.
- Compared all 119 Damage rows against the approved converted reference. All mapped values matched; product apostrophes were removed according to the confirmed Rule A.
- Completed 120 repeated end-to-end conversion simulations. Every generated workbook reopened successfully and retained 120 worksheet rows including the header.

## Scope note

The uploaded V4.5.10 package is a patch package and does not include the complete repository modules, Supabase secrets, or production environment. The new conversion engine, generated workbooks, navigation source integration, and package were tested locally; final connected Streamlit Cloud behavior should be confirmed after deployment to the full repository.
