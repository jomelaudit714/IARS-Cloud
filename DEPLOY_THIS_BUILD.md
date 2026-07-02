# Deploy IARS v4.4.14

1. Run the included latest `SUPABASE_PROFILE_SETUP.sql` in the Supabase SQL Editor. It is safe to run over the earlier profile setup; do not drop the existing profile table or bucket.
2. Extract the ZIP locally.
3. Upload the extracted contents directly to the GitHub repository root, replacing the previous files.
4. Do not upload the ZIP as an unextracted file or place the project in an extra nested folder.
5. Commit to the branch used by Streamlit.
6. Open Streamlit **Manage app → Reboot app**.
7. Refresh the browser with **Ctrl + F5**.

The top-right profile card now contains username, password, profile-picture, and sign-out controls. Existing Streamlit Secrets remain the administrator fallback credentials if no editable override has been saved yet.
