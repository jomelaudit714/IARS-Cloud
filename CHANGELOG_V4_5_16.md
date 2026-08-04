# IARS V4.5.16 — Yearly Audit Gantt Module

## Added

- New **Audit Planning** sidebar group.
- **Yearly Audit Gantt** page for Admin and Auditor accounts.
- **Gantt Master Data** page restricted to Admin accounts.
- One custodian per row with January through December as separate columns.
- Wider monthly cells and larger table-header font.
- Auditor nickname display in Gantt cells:
  - Patricia Anne Del Rosario → Anne
  - Sarina Amuraw → Sab
  - Cris Canonoy → Cris
  - Additional approved auditors use their configured short/default first name.
- Monthly assignment fields: auditor, status, planned date, date accomplished and remarks.
- Status values: Planned, In Progress, Done and Overdue.
- Solid red monthly boxes for overdue audit schedules.
- Sorting/filtering by Auditor, Status, Month and Custodian.
- Role-based visibility:
  - Admin sees the complete yearly schedule and can assign/edit audits.
  - Auditors see only schedules assigned to their own full-name account.
  - Auditors can update only their status, date accomplished and accomplishment remarks.
- Dashboard overdue notification for assigned audit schedules.
- Admin Excel upload and manual maintenance for Company / Department, Custodian, Audit Task, Accountability and Frequency.
- Supabase persistence using `iars_gantt_master` and `iars_gantt_schedule`.

## Included files

- `iars_gantt.py`
- `SUPABASE_GANTT_SETUP.sql`
- `assets/gantt_master_data_template.xlsx`
- `YEARLY_GANTT_RENDER_PREVIEW.png`

## Preserved

- Warehouse conversion
- LOGP conversion
- Invoice conversion, including blister-to-box conversion
- Existing login, header, sidebar, PDF, archive, document-library and profile behavior
