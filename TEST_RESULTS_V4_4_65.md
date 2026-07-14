# Test Results — V4.4.65

## Duplicate detection tests

- exact PDF SHA256 match: passed
- normalized IAD-reference match: passed
- exact-filename fallback: passed
- per-file metadata-error isolation: passed
- red `st.error` duplicate notification rendering: passed
- visible duplicate-check failure warning rendering: passed

## Regression tests

- Python compilation: passed 3 consecutive runs
- actual application AppTest: passed 3 consecutive runs
- local Streamlit startup: HTTP 200 in 3 consecutive runs
- Generate Extraction worker: passed 3 consecutive runs and produced one finding row
- clean-ZIP extract, compilation, AppTest, and static validation: passed 3 consecutive runs

## Integrity

The following operational modules are byte-for-byte unchanged from V4.4.64:

- `iars_parser.py`
- `iars_extract_worker.py`
- `iars_auth.py`
- `iars_archive.py`
- `iars_document_library.py`
- `iars_pdf_editor.py`
- `iars_theme.py`

No `__pycache__`, `.pyc`, old changelogs, or old test reports are included.
