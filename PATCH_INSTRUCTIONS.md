# Patch Instructions — IARS V4.5.02

1. Back up the current repository files.
2. Copy `app.py` and `iars_auth.py` from this patch into the repository root.
3. Replace the existing files when prompted.
4. Commit and push the changes to the deployed Streamlit repository.
5. Allow Streamlit Community Cloud to rebuild the app.
6. Hard-refresh the browser after deployment using `Ctrl + F5` to clear previously cached CSS.

No database migration or Supabase SQL change is required for this patch.
