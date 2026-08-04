# Verification — IARS V4.5.15

## Passed checks
- Python compilation passed for `app.py`, `iars_auth.py`, `iars_theme.py`, and `iars_excel_conversion.py`.
- Invoice conversion tests passed.
- LOGP regression test passed.
- Warehouse regression test passed.
- Actual Invoice Davido sample retained the exact V4.5.14 values and number formats across 86 rows × 18 columns.
- Dedicated blister tests passed:
  - `-20 BLISTERS` → `-2 box`
  - `15 Blister` → `1.5 box`
- 120 repeated end-to-end conversions passed:
  - 60 using the physical Invoice template asset
  - 60 using the embedded template fallback
- Artifact inspection confirmed the generated blister output in columns L and M.
- ZIP integrity test passed.

## Deployment limitation
The package was tested locally as an integrated patch. A live Streamlit Cloud test with the production Supabase connection still requires deployment to the user's full repository and environment.
