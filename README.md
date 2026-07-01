# IARS v4.4.5

Complete Internal Audit Report System deployment package with the approved login interface, compact dashboard navigation, and the refined professional dashboard theme.

## v4.4.5 refinements

- Professional color treatment applied to all Dashboard metric cards
- Distinct professional colors applied to every Dashboard Quick Action
- Colored status pills added to System Overview
- Recent Archive Activity styling improved for readability
- Archive Status value fixed so **Not configured** displays completely
- Long Dashboard values given additional clearance from icon areas
- Login **or** divider spacing fixed so the Sign Up box no longer covers it
- Sign In and Sign Up remain exactly equal in width

## Retained from v4.4.3 and v4.4.2

- EDL/IARS navy gradient top header with gold border and brand accent line
- Themed signed-in user panel for the name, initials, and role
- Reduced unused space above the dashboard
- Left-aligned and evenly oriented sidebar menu items
- Expandable **Audit Report** category containing:
  - Generate Extraction
  - PDF Tagging
  - Shared PDF Archive
- **Report Templates** renamed to **Audit Workpapers** throughout the interface

## Security

The preview-only authentication bypass used for testing is **not included** in this package. A private `.streamlit/secrets.toml` is also not included.

## Deployment

1. Extract the ZIP.
2. Upload the extracted contents directly to the GitHub repository root connected to Streamlit.
3. Replace the existing files, especially `app.py`, `iars_theme.py`, and `iars_auth.py`.
4. Keep real credentials only in Streamlit Secrets.
5. Commit the changes to the deployed branch.
6. Select **Manage app → Reboot app** in Streamlit.
7. Use **Ctrl + F5** after the reboot.

See `TEST_RESULTS_V4_4_4.md` and the v4.4.5 preview files in `docs/`.
