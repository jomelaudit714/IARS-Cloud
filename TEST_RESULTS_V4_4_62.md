# Test Results — V4.4.62

## Diagnosis

- `iars_parser.py` MD5 matches the user-approved V4.4.51 parser exactly: `ac63127939ab36b356a1e6eea1bd3d8f`.
- Generate Extraction processing logic differs from V4.4.51 only in Streamlit 1.47 display keywords (`use_container_width=True`).
- The regression coincided with PDF-stack downgrades introduced after V4.4.51.

## Restored PDF stack

- pdfplumber 0.11.10
- PyMuPDF 1.27.2.3
- Pillow 12.2.0

## Extraction tests

- Searchable table PDF parsed into 1 finding row: passed 5 consecutive worker runs.
- Actual isolated helper returned 1 finding row: passed 3 consecutive runs.
- Simulated native worker SIGSEGV (signal 11): contained 3 consecutive runs; parent process remained alive.

## Application tests

- Python compile: passed 3 consecutive runs.
- Imports with restored PDF stack: passed 3 consecutive runs.
- Actual Streamlit AppTest: passed 3 consecutive runs.
- Local Streamlit startup: HTTP 200 in 3 consecutive runs.
- Final clean ZIP validation: repeated before release.

## Integrity

- Original PDF Tagging import and Components v2 implementation retained.
- Sidebar, Dashboard, avatar, login, archive, document-library, and Master Data behavior retained.
- No old changelogs, old test reports, `__pycache__`, or `.pyc` files included.
