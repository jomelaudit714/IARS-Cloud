# Deploy IARS v4.1.0

1. Extract `IARS_v4_1_0_EDL_ENTERPRISE_UI_TESTED.zip`.
2. Replace the repository files with the extracted contents.
3. Confirm these paths exist:
   - `app.py`
   - `iars_theme.py`
   - `iars_auth.py`
   - `assets/edl_logo.png`
   - `assets/internal_audit_visual.png`
   - `.streamlit/config.toml`
4. Commit all changes to the branch used by Streamlit.
5. Reboot the app.
6. Press `Ctrl + F5` in the browser.

No new SQL migration is required when the v4.0.0 document library and existing user-authentication tables are already installed.
