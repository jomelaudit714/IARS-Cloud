# Yearly Audit Gantt Module

## Master Data upload
Use the Excel template in `assets/gantt_master_data_template.xlsx` and retain these exact headers:

1. Company / Department
2. Custodian
3. Audit Task
4. Accountability

Do not add Frequency to the upload. Frequency is calculated automatically from Done schedules for the custodian in the selected schedule year.

## Frequency rule
- Done with Date Accomplished: counted
- Planned: not counted
- In Progress: not counted
- Overdue: not counted
- Reverting Done to another status reduces the count

## Access
- Admin sees and edits the complete annual schedule and Gantt Master Data.
- Auditors see only schedules assigned to their account.
- Auditor dashboards show overdue notifications.


## Duplicate-rule behavior (V4.5.18)

- The same custodian may appear more than once.
- Rows are separate when Audit Task or Accountability differs.
- Only an exact match of Company / Department, Custodian, Audit Task, and Accountability is treated as a duplicate.
- Automatic Frequency is counted separately for each exact master-data record.
