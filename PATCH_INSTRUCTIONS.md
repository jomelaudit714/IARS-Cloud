# Patch Instructions

Replace these files in the current IARS repository:

1. `app.py`
2. `iars_document_library.py`

Commit the changes, reboot the Streamlit app, and perform a hard browser refresh (`Ctrl + F5`).

No new SQL or package installation is required for V4.4.96. If the earlier Policies upload error still appears, run the V4.4.95 `subject_category` Supabase migration once.
