# Deployment

1. Extract this ZIP.
2. Copy the contents directly to the root of the GitHub repository.
3. Confirm that `app.py` and `iars_gantt.py` are beside each other at repository root.
4. Do not upload the extracted folder as a subfolder.
5. Run `SUPABASE_GANTT_V4_5_18_DUPLICATE_RULE_FIX.sql` once if the database still uses the old three-field unique constraint.
6. Restart or reboot the Streamlit app.
7. The header should show version 4.5.19.
