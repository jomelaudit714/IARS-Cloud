# Deploy this exact build

Upload the **contents of this folder** to the root of the GitHub branch connected to Streamlit.

The repository root must directly contain `app.py`, `iars_auth.py`, `iars_theme.py`, `requirements.txt`, `assets/`, `data/`, and `.streamlit/`. Do not upload the ZIP as a single unextracted file and do not place these files inside another folder.

After committing, open Streamlit **Manage app → Reboot app**, then perform a hard refresh (`Ctrl+F5`).

Build marker in the login HTML: `4.4.1-deployment-fixed`.
