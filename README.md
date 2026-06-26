# IARS v4.0.0 — EDL Professional Internal Audit Workspace

This package applies the approved EDL GROUP OF COMPANIES branding and professional Internal Audit interface to the current IARS functions.

## Main functions

- Administrator-approved multi-user login using username/nickname and password
- Dashboard with system status, archive activity and quick actions
- Generate Extraction with three choices:
  - Generate extraction only
  - Generate extraction and archive original PDFs
  - Archive original PDFs only
- PDF Tagging Editor
- Shared PDF Archive visible to all signed-in auditors
- Automatic PDF compression before archive storage
- Report Templates Library for Excel, Word and PDF files
- Policies & Memoranda Archive for Excel, Word and PDF files
- User Management for administrator approval and account control
- Master Data Management with workbook validation before activation
- Read-only System Settings and security status

## Branding and interface

- Uses the exact original `EDL GROUP OF COMPANIES` logo supplied by the user
- Professional navy, white and restrained gold palette
- Sidebar navigation instead of top-level workspace tabs
- Corporate dashboard, compact status cards and user-friendly upload screens
- Responsive layout for desktop and tablet use

## Deployment

1. Extract the ZIP.
2. Upload all files and folders to the GitHub repository used by Streamlit.
3. Commit the changes together.
4. Run the required Supabase SQL files:
   - `SUPABASE_SETUP.sql`
   - `SUPABASE_AUDITOR_MIGRATION.sql`
   - `SUPABASE_USER_AUTH_SETUP.sql`
   - `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql`
5. Add the values from `.streamlit/secrets.toml.example` to Streamlit Secrets.
6. Reboot the Streamlit app.

## Important files

- `app.py` — application pages and workflows
- `iars_theme.py` — EDL professional interface
- `iars_auth.py` — login, sign-up, approval and reset flow
- `iars_archive.py` — compressed PDF archive
- `iars_document_library.py` — templates, policies and memoranda storage
- `iars_parser.py` — audit report extraction and exact export values
- `assets/edl_logo.png` — exact original logo
- `assets/internal_audit_workspace.png` — Internal Audit visual used in the interface
