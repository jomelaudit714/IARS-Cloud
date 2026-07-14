# Internal Audit Report System — V4.4.65

EDL Group of Companies Internal Audit Report System built with Streamlit.

## Current approved changes

- The sidebar is expanded after every successful manual sign-in, regardless of an older remembered collapsed browser state.

- The original V4.4.65 theme, logo treatment, colors, fonts, cards, borders, shadows, and module appearance are retained.
- The sidebar content is positioned slightly higher.
- The EDL logo is horizontally centered in the sidebar.
- A visible navy-and-gold restore button appears when the sidebar is collapsed, using Streamlit 1.47's exact `stExpandSidebarButton` control.
- The main interface expands into the available width while the sidebar is hidden.
- The Dashboard no longer displays:
  - Archive Status
  - Quick Actions
  - System Overview
- The five remaining Dashboard cards retain their original design and become only moderately wider because one card was removed.
- Recent Archive Activity retains its original design and left-column proportion.

## Main application files

- `app.py`
- `iars_auth.py`
- `iars_theme.py`
- `iars_parser.py`
- `iars_archive.py`
- `iars_document_library.py`
- `iars_pdf_editor.py`
- `requirements.txt`
- `packages.txt`

## Required repository folders

- `.streamlit/`
- `assets/`
- `data/`

Do not upload real Supabase keys into GitHub. Store live credentials only in Streamlit Cloud Secrets.


## Generate Extraction protection

The unchanged IARS parser runs in an isolated extraction worker. Native PDF/OCR failures cannot terminate the main Streamlit service.
