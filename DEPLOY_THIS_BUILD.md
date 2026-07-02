# Deploy IARS v4.4.13

1. Run `SUPABASE_PROFILE_SETUP.sql` once in the Supabase SQL Editor.
2. Extract the ZIP locally.
3. Upload the extracted contents directly to the GitHub repository root, replacing the previous files.
4. Do not upload the ZIP as an unextracted file or place the project in an extra nested folder.
5. Commit to the branch used by Streamlit.
6. Open Streamlit **Manage app → Reboot app**.
7. Refresh the browser with **Ctrl + F5**.

The top-right profile card now contains username, password, profile-picture, and sign-out controls. Existing Streamlit Secrets remain the administrator fallback credentials if no editable override has been saved yet.
