# Deploy IARS v4.4.0

1. Extract the ZIP.
2. Upload the contents directly to the GitHub repository root.
3. Keep these exact paths:
   - `app.py`
   - `iars_theme.py`
   - `iars_auth.py`
   - `assets/edl_logo.png`
   - `assets/login_panel.jpg`
   - `assets/internal_audit_visual.png`
   - `data/Master_Data.xlsx`
   - `.streamlit/config.toml`
4. Commit all files together.
5. Reboot the Streamlit app.
6. Refresh the browser with Ctrl+F5.

No new Supabase migration is required when upgrading from v4.2.1.
