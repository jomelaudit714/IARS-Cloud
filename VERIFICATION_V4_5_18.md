# Verification — IARS V4.5.18

Verified locally:

- Python compilation for all IARS modules.
- All Warehouse, LOGP, Invoice, and Gantt automated tests.
- Same company/custodian/audit task with different Accountability is accepted.
- Exact duplicates across all four fields are rejected.
- Supabase upsert conflict key uses all four fields.
- Done Frequency is counted separately per exact master-data record.
- Planned and In Progress schedules do not increase Frequency.
- Gantt template has exactly four upload columns and updated instructions.
- ZIP integrity verification.

Live Supabase execution still requires running the included migration in the user's connected project.
