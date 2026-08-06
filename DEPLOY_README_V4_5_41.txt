IARS V4.5.41 — Gantt Non-Null Reference Fix

BASELINE
- IARS V4.5.40 complete deployment.

FIX
- Corrects monthly Gantt creation failure caused by explicit NULL values being sent to the NOT NULL columns initial_report_reference and final_report_reference.
- Scheduled, In Progress, Done, and report-stage records now always send valid text values.
- Existing report references are retained when the corresponding IRS/FRS stage remains active.

DEPLOYMENT
1. Extract this ZIP.
2. Upload all contents directly to the GitHub repository root.
3. Replace the existing files.
4. Reboot the Streamlit application and perform a hard refresh.
5. Confirm that the header displays v4.5.41.

DATABASE
- No Supabase SQL migration is required.
- The database schema is already correct: both reference columns are NOT NULL with empty-string defaults.
