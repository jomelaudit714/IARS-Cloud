# Installation — IARS V4.5.21

1. Extract `IARS_V4_5_21_ONE_PAGE_GANTT_MONTH_FILTER.zip`.
2. Upload the extracted contents directly to the root of the IARS GitHub repository.
3. Replace the existing root files, especially `app.py` and `iars_gantt.py`.
4. Do not place the extracted package inside a new nested folder.
5. Reboot the Streamlit application.
6. Confirm that the system header displays `v4.5.21`.
7. Open Yearly Audit Gantt and confirm:
   - there are no Rows per page or Page selectors;
   - all matching custodian rows appear on one page;
   - selecting a month changes rows only;
   - all January–December columns remain available;
   - month boxes remain clickable.

No new Supabase SQL migration is required for this release.
