# IARS V4.5.21 — One-Page Gantt and Month Row Filter

## Yearly Audit Gantt

- Removed the **Rows per page** and **Page** controls.
- All custodian records matching the active filters are rendered on one page.
- Users move through the records by scrolling down instead of changing pages.
- The Month filter now explicitly filters custodian rows only.
- January through December remain visible for every matching custodian row.
- The table header remains sticky while scrolling down.
- Company / Department, Custodian, Audit Task, Accountability, and Frequency remain sticky while scrolling horizontally.
- Existing clickable month-box editing, Done, IRS, FRS, overdue, frequency, and holiday logic are retained.

## Database

No Supabase migration is required for V4.5.21. Continue using the V4.5.20 workflow tables and columns.
