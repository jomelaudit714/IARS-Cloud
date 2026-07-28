# Test Results — IARS V4.5.02

## Passed

- Python bytecode compilation for `app.py` and `iars_auth.py`.
- Python AST parsing for both patch files.
- Verified matching V4.5.02 module-transition, logout-state, and Sign Out widget keys.
- Verified the non-Dashboard header recovery is exactly 29 pixels, based on the supplied video frames where Generate Extraction started 29 pixels lower than Dashboard.
- Verified the non-Dashboard recovery includes a matching negative bottom margin to avoid creating extra space below the header.
- Verified the header uses sticky positioning with a 4-pixel top threshold.
- Verified Philippine Standard Time remains configured as UTC+8 with the `PHT` label.
- Verified the hidden Enter submit control appears before `Forgot password` in the sign-in form source order.
- Verified Enter and the visible Sign In button are combined into the same `submitted` result.
- Verified the login left-panel EDL artwork horizontal adjustment was increased from 2.6% to 6.5%.
- Verified displayed version is `4.5.02`.
- ZIP archive integrity test.

## Deployment limitation

A complete Supabase-connected Streamlit Cloud test was not possible in the isolated environment because the patch package contains only the replacement source files and does not include the full repository, secrets, assets, dependencies, or connected database configuration.
