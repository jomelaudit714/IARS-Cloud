# Deploy IARS v4.4.4

1. Extract the ZIP locally.
2. Upload the extracted contents directly to the GitHub repository root.
3. Replace the existing files, especially `app.py`, `iars_theme.py`, and `iars_auth.py`.
4. Do not upload `.streamlit/secrets.toml`; keep real credentials only in Streamlit Secrets.
5. Commit to the branch connected to Streamlit.
6. Open Streamlit **Manage app → Reboot app**.
7. Press **Ctrl + F5** after the reboot.
