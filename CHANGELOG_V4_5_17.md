# IARS V4.5.17 — Automatic Gantt Frequency

- Removed Frequency from the Gantt Master Data upload template and admin form.
- Required upload columns are now Company / Department, Custodian, Audit Task, and Accountability.
- Frequency in the yearly Gantt is read-only and calculated automatically.
- Automatic Frequency = number of audit schedules marked Done for the custodian in the selected year.
- Planned, In Progress, and Overdue schedules are not counted.
- Changing Done back to another status automatically reduces the displayed count.
- Done still requires a Date Accomplished.
- Existing V4.5.16 database frequency columns are ignored for backward compatibility.
- Updated the Supabase setup script to include service-role grants.
