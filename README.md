# IARS v4.4.11

Complete Internal Audit Report System deployment package containing the approved login, dashboard, sidebar, Generate Extraction, header-cleanup, and PDF Tagging updates.

## v4.4.11 PDF Tagging interaction refinements

- A single normal left click inside existing textbox text immediately selects the textbox, focuses the editor, and places the caret at the clicked position.
- No second left click is required after clicking outside the textbox.
- Long-press and drag inside textbox text repositions the whole textbox.
- Dragging the plain sides or border repositions the whole textbox.
- Dragging the small blue handles resizes the textbox only.
- Click-versus-long-press detection prevents editing, moving, and resizing actions from conflicting.
- Automatic save and per-textbox font size controls remain enabled.

## Retained approved updates

- Removed duplicate secondary titles from Generate Extraction, PDF Tagging, and Shared PDF Archive.
- Per-textbox font size control from 6–48 pt, with the selected size retained.
- Automatic saving with no manual Save Changes button.
- Generate Extraction duplicate-report warning listing all repeated IAD reference numbers.
- Compact, light color-coded extraction choices.
- Professional dashboard colors and readable status pills.
- Expandable Audit Report sidebar category and Audit Workpapers naming.
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


## v4.4.12 PDF Tagging improvements

- 1.8-second true inactivity delay before Streamlit autosave synchronization.
- Returning to an existing textbox with one left click places the caret at the clicked character.
- Browser default caret-at-end behavior is suppressed.
- Long-press drag and blue-handle resizing remain supported.
## v4.4.14 Profile Menu

The top-right user card is now clickable and opens Edit Profile. Users can change their username and password, upload or remove a JPG/PNG profile picture, and sign out from the same menu. The avatar is enlarged to 46×46 px. Run the latest included `SUPABASE_PROFILE_SETUP.sql` before using these profile controls. It is idempotent and may be run over the earlier profile setup.

