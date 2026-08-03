# Verification — IARS V4.5.13

## Actual supplied LOGP sample

Input: `LOGP 61005123 DAVIDO GOOD - 06-22-2026.xlsx`

- Captured rows: 37
- LOGP number: 61005123
- Document date: 2026-06-22
- Remarks: Good
- Employee mapping: `DAVIDO, REY VAN` → `Rey Van Laurente Davido`
- Apostrophe test: `Amtyl Max 100's` → `Amtyl Max 100s`
- Output filename: `FOR UPLOAD 61005123 GOOD.xlsx`

## Exact-reference validation

Using process date `2026-06-28` and auditor `Jed Laserna`, all 38 rows × 18 columns of the generated workbook matched the approved reference workbook exactly in values and number formats.

## Repeated tests

- 120 repeated actual-sample conversions passed.
- Half of the runs used the physical `assets/logp_conversion_template.xlsx`.
- Half used the embedded template fallback with a deliberately missing asset path.
- Existing Warehouse conversion regression passed with 119 captured rows.
- Synthetic LOGP tests passed for:
  - source beginning at `A01AMB03` instead of `A01AMB01`;
  - blank UoM;
  - apostrophe removal;
  - Master Data name resolution;
  - `Regular` → `Good`;
  - `Sotex` and `Sold Out` filename parsing;
  - required blank output fields.
- Python compilation passed for `app.py`, `iars_excel_conversion.py`, `iars_auth.py` and `iars_theme.py`.
- Formula/error scan of the generated output found zero spreadsheet errors.

## Environment limitation

The uploaded base is a patch package and does not contain the complete production repository or production Supabase secrets. Full connected Streamlit Cloud behavior must be confirmed after the files are pushed to the full repository.
