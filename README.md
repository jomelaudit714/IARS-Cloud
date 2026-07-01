# IARS v4.4.8

Complete Internal Audit Report System deployment package containing all previously approved login, dashboard, sidebar, Generate Extraction, and Audit Report updates.

## v4.4.8 refinements

- Removed duplicate secondary titles from Generate Extraction, PDF Tagging, and Shared PDF Archive.
- Retained one primary header title with a brief page description.
- Added a per-textbox **Font size** control in PDF Tagging.
- Font-size range: **6–48 pt**.
- Each textbox can retain its own font size for tagged-PDF generation.
- Improved existing-textbox editing after adding or selecting another textbox.
- Keystrokes are saved browser-side without rebuilding the textbox layer on every character.
- Streamlit synchronization occurs after idle/blur instead of on every keystroke.
- Reduced lag while deleting and retyping inside a previously completed textbox.

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
