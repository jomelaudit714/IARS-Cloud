# Deployment

1. Open Supabase → SQL Editor.
2. Run `SUPABASE_POLICY_SUBJECT_CATEGORY_FIX.sql` once.
3. Confirm the final verification query returns `subject_category`.
4. Replace these GitHub files:
   - `app.py`
   - `iars_document_library.py`
5. Commit and reboot Streamlit.
6. Wait a few seconds, press `Ctrl + F5`, then upload the policy again.

No requirements update is needed.
