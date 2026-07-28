# Deployment Instructions

Replace these files in the current IARS GitHub repository:

1. `app.py`
2. `iars_auth.py`

Then commit the changes, reboot the Streamlit app, and perform a hard refresh (`Ctrl + F5`).

No Supabase SQL, requirements, or asset update is required. The transition uses the existing `assets/edl_logo.png`; if that asset is unavailable, it safely displays an EDL text emblem instead.
