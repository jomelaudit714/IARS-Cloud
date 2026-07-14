# Deploy IARS V4.4.62

1. Extract the ZIP.
2. Upload the contents of the extracted folder to the existing IARS GitHub repository.
3. Include the hidden `.streamlit` folder.
4. Keep the existing Streamlit Cloud Secrets unchanged.
5. Wait for Streamlit Cloud to reinstall the pinned dependencies and restart the app.
6. Perform one browser hard refresh: `Ctrl + F5`.

## Post-deployment checks

- Sign out, sign in again, and confirm the sidebar is visible by default.
- Open the Dashboard.
- Confirm there are five summary cards.
- Confirm Archive Status, Quick Actions, and System Overview are absent.
- Collapse the sidebar.
- Confirm the navy-and-gold restore button appears.
- Confirm the main interface expands.
- Restore the sidebar.
- Confirm the EDL logo remains centered and the sidebar items are positioned slightly higher.

The PDF Tagging implementation remains unchanged from the approved V4.4.57 build.


## Important upload instruction

Delete or overwrite the existing repository files using the complete contents of this extracted folder. Do not upload only `app.py`; upload all files together so GitHub does not retain mixed versions.


## Generate Extraction check

After deployment, upload one searchable PDF and click Generate Extraction. The app must remain online and show either generated records or a PDF-specific processing message.
