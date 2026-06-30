# Login input stability hotfix

- Removed `setStateValue()` calls from username, password, and remember-me input events.
- Typing now stays entirely in the browser and no longer starts a Streamlit rerun for every keystroke.
- Only Sign In, Forgot Password, Sign Up, and Verify Account send one-time trigger events to Python.
- Remembered usernames are stored locally in the browser when the checkbox is enabled.
- No authentication, database, archive, extraction, or master-data logic was changed.
