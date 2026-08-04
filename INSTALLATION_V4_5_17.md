# Installation — IARS V4.5.17

1. Overlay this package on the current complete IARS repository.
2. Keep the included `assets/gantt_master_data_template.xlsx` file.
3. Existing V4.5.16 Gantt tables do not need to be recreated.
4. If the Gantt page shows a permission error, run `SUPABASE_GANTT_PERMISSION_FIX.sql` once in Supabase.
5. Refresh or reboot the Streamlit app.

The old database `frequency` column may remain. V4.5.17 no longer reads or writes it.
