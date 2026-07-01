# IARS v4.4.10

Complete Internal Audit Report System deployment package containing the approved login, dashboard, sidebar, Generate Extraction, header-cleanup, and PDF Tagging updates.

## v4.4.10 refinements

- Removed duplicate secondary titles from Generate Extraction, PDF Tagging, and Shared PDF Archive.
- Retained one primary header title with a brief page description.
- Added a per-textbox **Font size** control in PDF Tagging, from **6–48 pt**.
- The selected font size remains after deselecting or reselecting a textbox.
- New textboxes inherit the latest selected font size.
- Removed the manual Save Changes button.
- Textbox edits are saved automatically after a short pause or control change.
- Editing remains browser-local while typing, deleting, resizing, or moving to reduce reruns and lag.
- Added automatic-save status feedback: Editing, Saving, and All changes saved automatically.
- Tagged-PDF generation uses the saved textbox font size.

## Retained approved updates

- Generate Extraction duplicate-report warning listing all repeated IAD reference numbers.
- Compact, light color-coded extraction choices.
- Professional dashboard colors and readable status pills.
- Expandable Audit Report sidebar category.
- Audit Workpapers naming.
- Corrected Sign Up, Forgot Password, login, and sidebar alignment.

## Security

The preview-only authentication bypass and private `.streamlit/secrets.toml` are not included. Keep real credentials only in Streamlit Secrets.

## Deployment

1. Extract the ZIP.
2. Upload the extracted contents directly to the GitHub repository root connected to Streamlit.
3. Replace the existing files, especially `app.py`, `iars_pdf_editor.py`, `iars_theme.py`, and `iars_auth.py`.
4. Commit the changes to the deployed branch.
5. Select **Manage app → Reboot app**.
6. Refresh the browser with **Ctrl + F5**.
