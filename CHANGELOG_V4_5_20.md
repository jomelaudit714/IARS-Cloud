# IARS V4.5.20 — Clickable Gantt + IRS/FRS Workflow

## Yearly Audit Gantt
- Each January–December month box is now a native Streamlit popover that can be clicked directly.
- Admin/Supervisor plans an audit by selecting only the auditor. Status is saved as **Planned** and Due Date is automatically the last day of the selected month.
- The assigned auditor clicks the same month box to mark the audit **Done** and enters the **Date of Audit**.
- Frequency remains automatic and counts Done audits per exact Company / Department + Custodian + Audit Task + Accountability record.

## Report submission workflow
- **IRS** = Initial Report Submitted, updated by the assigned auditor.
- **FRS** = Final Report Submitted, updated by the Admin/Supervisor.
- IRS due date is 5 working days after Date of Audit.
- FRS due date is 5 working days after IRS submission date.
- Submission dates are captured automatically using the current Philippine date.
- Red month boxes and dashboard notifications are shown for IRS Overdue and FRS Overdue.
- Yellow notifications are shown while For IRS or For FRS is pending.

## Working-day exclusions
- Saturdays and Sundays are excluded.
- Active Regular, Special Non-Working, and Local Special Non-Working holiday records are excluded.
- National, Province of Rizal, and San Mateo, Rizal coverage is supported.
- Special Working holidays remain working days.

## Admin Holiday Calendar
- Added Excel upload, manual add/edit, active/inactive control, source reference, and annual holiday display.
- Added a prefilled 2026 holiday template based on official proclamations available as of 4 August 2026.
