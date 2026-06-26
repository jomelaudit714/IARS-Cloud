# IARS v4.1.0 — EDL Enterprise Internal Audit Interface

This package applies the approved EDL GROUP OF COMPANIES Internal Audit interface to the working IARS application while retaining the existing authentication, extraction, PDF tagging, shared archive, document library, Master Data, and export logic.

## Visual implementation

- Exact original `assets/edl_logo.png` supplied by the user
- Navy enterprise sidebar with gold active navigation
- Compact page-specific top bar with user, role, date, and version
- Professional login split layout with Internal Audit image and white account card
- Dashboard KPI cards, recent archive activity, quick actions, and system overview
- Workflow steppers for Generate Extraction and PDF Tagging
- Summary cards for Shared PDF Archive, Report Templates, Policies & Memoranda, Master Data, User Management, and Settings
- Responsive layout for smaller screens
- Direct HTML rendering through `st.html()` when supported to prevent raw tags from appearing

## Existing functions retained

- Admin-approved username/nickname login
- Sign Up, Verify, and Reset Password
- Shared PDF archive visible to all signed-in auditors
- Direct archive upload and automatic PDF compression
- Report extraction and exact external-system export headers
- PDF tagging editor
- Report Templates library for Excel, Word, and PDF
- Policies & Memoranda archive for Excel, Word, and PDF
- Administrator-only deletion, account administration, and Master Data updates

## Deployment

1. Extract the ZIP.
2. Upload all files and folders to the GitHub repository used by Streamlit.
3. Commit them together on the deployed branch.
4. Keep the existing Streamlit Secrets.
5. Run the SQL setup files only if the corresponding Supabase tables were not created previously.
6. Reboot the Streamlit app and hard-refresh the browser with `Ctrl + F5`.

The Streamlit implementation follows the approved mockup closely, but native Streamlit controls may not be pixel-identical to a custom React or HTML application.
