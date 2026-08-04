# Installation — IARS V4.5.18

1. Overlay all files from this package onto the complete current IARS repository.
2. In Supabase SQL Editor, run `SUPABASE_GANTT_V4_5_18_DUPLICATE_RULE_FIX.sql` once.
3. Commit and deploy the updated repository.
4. Refresh Streamlit and confirm the header shows version 4.5.18.
5. Upload the four-column `assets/gantt_master_data_template.xlsx`.

## Important database step

The migration changes the Gantt master unique key from:

`Company / Department + Custodian + Audit Task`

to:

`Company / Department + Custodian + Audit Task + Accountability`

It does not delete existing Gantt master or schedule records.
