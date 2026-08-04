# IARS V4.5.18 — Exact Gantt Duplicate Rule

- Allowed the same custodian to appear in multiple master-data rows when Audit Task or Accountability differs.
- Duplicate validation now checks all four fields: Company / Department, Custodian, Audit Task, and Accountability.
- Updated Supabase upsert conflict columns to the same four-field key.
- Added a safe Supabase migration that replaces the old three-field unique constraint.
- Automatic Frequency is now counted separately per exact master-data record, not combined by custodian name.
- Added Accountability to schedule and edit selectors so records with the same custodian/task remain distinguishable.
- Updated the Gantt Excel template instructions to explain the new duplicate and frequency rules.
- Updated IARS version to 4.5.18.
