# IARS v4.2.1 Flat Deployment

This ZIP is intentionally flat. After extraction, `app.py` must be at the GitHub repository root.

Required root structure:

```text
app.py
iars_auth.py
iars_theme.py
assets/edl_logo.png
assets/internal_audit_visual.png
.streamlit/config.toml
```

Do not upload the extracted folder as a subfolder. Overwrite the existing root-level files, commit, reboot Streamlit, and hard refresh. The app header/settings should show version 4.2.1.
