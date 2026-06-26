# Deploy IARS v4.2.0

1. Extract the ZIP locally.
2. Upload all files and folders to the GitHub repository used by Streamlit.
3. Confirm these paths exist exactly:
   - `app.py`
   - `iars_theme.py`
   - `iars_auth.py`
   - `assets/edl_logo.png`
   - `assets/internal_audit_visual.png`
   - `.streamlit/config.toml`
4. Commit the changes to the Streamlit deployment branch.
5. Reboot the Streamlit app.
6. Open the app and press `Ctrl + F5` once.

No new Supabase migration is required when upgrading from v4.0.0 or v4.1.0.
