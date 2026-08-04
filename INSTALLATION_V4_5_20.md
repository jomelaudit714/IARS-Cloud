# Installation — IARS V4.5.20

1. Back up the current GitHub repository and Supabase project.
2. Run `SUPABASE_GANTT_V4_5_20_WORKFLOW_MIGRATION.sql` in the Supabase SQL Editor.
3. Upload the contents of this ZIP to the **root** of the IARS GitHub repository and replace existing files.
4. Confirm that `app.py`, `iars_gantt.py`, and `assets/` are at repository root level, not inside a nested folder.
5. Reboot the Streamlit app.
6. Confirm the top header shows **v4.5.20**.
7. Open **Gantt Master Data > Holiday Calendar** and import `assets/gantt_holiday_calendar_template.xlsx`.
8. Open **Yearly Audit Gantt** and click a month box to test Planned → Done → IRS → FRS.

For a fresh database only, run `SUPABASE_GANTT_SETUP.sql` instead of the migration file.
