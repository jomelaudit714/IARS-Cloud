# IARS Yearly Audit Gantt — V4.5.23

## Roles

### Admin/Supervisor
- Views all schedules.
- Clicks a month box to assign an auditor.
- Planned due date is automatically the last day of the month.
- Receives For FRS and FRS Overdue notifications.
- Clicks the month box to record **FRS — Final Report Submitted**.
- Maintains custodian master data and the holiday calendar.

### Auditor
- Sees only assigned schedules.
- Clicks a month box to mark the audit Done and records Date of Audit.
- Receives For IRS and IRS Overdue notifications.
- Clicks the same month box to record **IRS — Initial Report Submitted**.

## Deadline rules
- IRS: 5 working days after Date of Audit.
- FRS: 5 working days after IRS submission.
- The starting date is not counted.
- Overdue begins the day after the fifth valid working day.
- Weekends and active non-working holidays are excluded.
- Special Working holidays are not excluded.

## Required Supabase objects
- `iars_gantt_master`
- `iars_gantt_schedule`
- `iars_gantt_holiday`

## V4.5.23 display behavior
- All matching custodians remain in one scrollable Gantt viewport.
- The complete header from Company / Department through December stays visible while scrolling vertically.
- Company, Custodian, Audit Task, Accountability, and Frequency remain sticky during horizontal scrolling.
- Identifying columns are compact to provide more space for the twelve month boxes.
- Accountability is displayed as Philippine peso with two decimal places.


### V4.5.23 layout correction
- All 17 columns use an equal 104 px width.
- The header row cannot wrap, so December remains after November.
- The actual Streamlit header row is sticky inside the vertical Gantt viewport.
- Every header label is centered.
- Accountability displays two decimal places.
