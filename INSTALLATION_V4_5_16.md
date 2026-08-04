# Installation — IARS V4.5.16

1. Copy the contents of this package over the current IARS repository.
2. Keep the existing repository files that are not included in this patch package.
3. In Supabase SQL Editor, run `SUPABASE_GANTT_SETUP.sql` once.
4. Confirm these files are deployed:
   - `iars_gantt.py`
   - `assets/gantt_master_data_template.xlsx`
5. Restart or redeploy Streamlit.
6. Sign in as Admin and open **Audit Planning → Gantt Master Data**.
7. Download the Excel template, upload the yearly master records, then open **Yearly Audit Gantt** to assign monthly schedules.

The module uses the same Supabase service-role connection already configured for IARS. No additional Streamlit Secret is required.
