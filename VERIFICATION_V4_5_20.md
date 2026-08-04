# Verification — IARS V4.5.20

## Automated checks completed
- Python compilation: `app.py` and `iars_gantt.py`
- Full regression suite: 12 tests passed
- Warehouse, LOGP, Invoice, duplicate-rule, Gantt, holiday-template, permissions, and UI-path simulations passed
- 240 independent working-day deadline comparisons passed
- 120 complete IRS/FRS transition simulations passed
- Admin and auditor page render paths simulated repeatedly with a Streamlit-compatible test stub
- Excel assets inspected for expected headers/data and formula errors
- ZIP integrity checked after packaging

## Live checks required after deployment
- Confirm month popovers open correctly in the deployed Streamlit version.
- Confirm the migration completed and the PostgREST schema cache reloaded.
- Import the holiday asset and verify the 5-working-day deadline shown in a month box.
- Confirm auditor receives IRS notifications and Admin/Supervisor receives FRS notifications.
