# IARS V4.5.11 — Warehouse Excel Conversion Module

This package is based directly on `IARS_V4_5_10_APPROVED_LOGIN_PANEL_FINAL` and retains its approved login/sidebar artwork and authentication/theme files.

## New sidebar structure

- Excel Conversion
  - Warehouse
  - Sales Personnel
    - LOGP — disabled placeholder for the next project
    - Invoice — disabled placeholder for the next project

## Files to apply

Replace/add these files in the current IARS repository:

- `app.py`
- `iars_excel_conversion.py`
- `assets/warehouse_conversion_template.xlsx`

The ZIP also includes the unchanged V4.5.10 approved files for safe full-package replacement.

After pushing to the deployment branch, wait for Streamlit Cloud to complete the rebuild and use `Ctrl + F5`.

Expected visible version: `4.5.11`.
