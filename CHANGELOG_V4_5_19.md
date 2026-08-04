# IARS V4.5.19 — Root-Level Gantt Duplicate Fix

- Keeps duplicate custodian names when Audit Task or Accountability differs.
- Blocks only exact duplicates across Company / Department, Custodian, Audit Task, and Accountability.
- Uses the exact four-field combination for Supabase upsert conflicts.
- Packaged with app.py and iars_gantt.py at the ZIP root to prevent deployment into a nested folder.
- Adds a V4.5.19 marker to the exact-duplicate validation message for deployment verification.
