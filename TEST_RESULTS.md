# Test Results — IARS v3.9.0

## Static validation

- `app.py` syntax compilation: PASSED
- `iars_auth.py` syntax compilation: PASSED
- `iars_theme.py` syntax compilation: PASSED
- `iars_archive.py` syntax compilation: PASSED
- `iars_parser.py` syntax compilation: PASSED
- `iars_pdf_editor.py` syntax compilation: PASSED

## Package validation

- EDL logo asset included: PASSED
- Streamlit theme configuration included: PASSED
- Deployment files arranged at ZIP root: PASSED
- No new Python dependency introduced: PASSED

## Regression checks

The following files are byte-for-byte unchanged from v3.8.2:

- `iars_archive.py`
- `iars_parser.py`
- `iars_pdf_editor.py`
- `data/Master_Data.xlsx`

Therefore, the following prior behaviors remain unchanged:

- Shared archive visibility for all signed-in auditors
- Direct PDF archive and extraction/archive options
- Automatic PDF compression
- Exact 27-column export headers
- Exact Master Data labels
- Blank Auditor 2 / `by02` behavior

## Environment limitation

Live login and Supabase archive actions require the user's deployed Supabase project and Streamlit Secrets. Those remote operations were not executed in the offline package test.
