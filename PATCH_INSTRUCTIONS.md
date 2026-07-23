# IARS V4.4.80 Deployment

Replace these files in the current GitHub repository:

1. `app.py`
2. `iars_document_library.py`
3. `assets/login_left_panel.png`

Then commit the changes, reboot the Streamlit app, and refresh the browser with Ctrl + F5.

No Supabase SQL migration and no requirements update are needed. The current document-library setup already grants update and delete privileges to the service role.
