# IARS v4.4.16

Complete Internal Audit Report System deployment package containing the approved login, dashboard, sidebar, Generate Extraction, PDF Tagging, header cleanup, and profile-menu updates.

## v4.4.16 Profile Menu and Picture Upload

- The top-right user card itself is the only visible profile-menu trigger.
- No separate “Open profile menu” box or label is displayed.
- JPG, JPEG, and PNG uploads are automatically EXIF-corrected, center-cropped to a square, resized to 320 × 320 pixels, and displayed with circular cover fitting.
- Profile pictures are saved to Supabase Storage when available.
- If Storage is unavailable, the optimized image is automatically saved through the secure database fallback.
- The updated `SUPABASE_PROFILE_SETUP.sql` includes explicit `service_role` grants for the profile table and Storage tables.
- Change Username, Change Password, Change Profile Picture, Remove Picture, and Sign Out remain inside the profile menu.

## Retained approved updates

- 1.8-second true inactivity autosave for PDF Tagging.
- Exact caret placement at the clicked character.
- Single-click textbox editing, long-press dragging, border dragging, and blue-handle resizing.
- Per-textbox font size control from 6–48 pt.
- Removed duplicate secondary titles from Generate Extraction, PDF Tagging, and Shared PDF Archive.
- Generate Extraction duplicate-report warning listing repeated IAD reference numbers.
- Compact, light color-coded extraction choices.
- Professional dashboard colors and readable status pills.
- Expandable Audit Report sidebar category and Audit Workpapers naming.
- Corrected Sign Up, Forgot Password, login, and sidebar alignment.

## Security

The preview-only authentication bypass and private `.streamlit/secrets.toml` are not included. Keep real credentials only in Streamlit Secrets.

## Deployment

1. Run the included latest `SUPABASE_PROFILE_SETUP.sql` in Supabase SQL Editor. It is safe to run over the earlier setup.
2. Extract the ZIP.
3. Upload the extracted contents directly to the GitHub repository root connected to Streamlit.
4. Replace the existing files.
5. Commit the changes to the deployed branch.
6. Select **Manage app → Reboot app**.
7. Refresh the browser with **Ctrl + F5**.
