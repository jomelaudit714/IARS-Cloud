IARS V4.5.32 — COMPLETE CLEAN DEPLOYMENT

Changes:
- Gantt Master Data supports permanent single-record deletion.
- Gantt Master Data supports permanent multiple-record deletion.
- Gantt Master Data supports deletion of the whole custodian master list.
- Linked monthly Gantt schedules are deleted with their master records.
- Holiday Calendar records are not affected.
- Strong confirmation is required before deletion.
- The displayed and upload-template header is now Company.
- Legacy Excel files using Company / Department remain accepted.
- Retains the V4.5.31 Streamlit 1.58 Gantt compatibility fix.

Deployment:
1. Extract this ZIP.
2. Upload its contents directly to the GitHub repository root.
3. Replace existing files.
4. Reboot the Streamlit app.
5. Confirm v4.5.32 in the IARS header.

No new Supabase SQL migration is required.
Do not upload or commit a real secrets.toml file.
