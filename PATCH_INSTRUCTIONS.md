# Deployment Instructions — IARS V4.5.00

Replace these files in the current IARS GitHub repository:

1. `app.py`
2. `iars_auth.py`

Then commit the changes, reboot the Streamlit app, and perform a hard refresh (`Ctrl + F5`).

No Supabase SQL, requirements, database, or asset update is required. The transition continues to use the existing `assets/edl_logo.png`; when that file is unavailable, the built-in EDL text emblem is used safely.
