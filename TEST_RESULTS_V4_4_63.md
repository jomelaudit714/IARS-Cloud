# Test Results — V4.4.63

## Dependency compatibility

- Streamlit 1.47.1 Pillow constraint checked: `>=7.1.0,<12`.
- pdfplumber 0.11.9 Pillow constraint checked: `>=9.1`.
- Pillow 11.3.0 satisfies both constraints.
- The conflicting pdfplumber 0.11.10 / Pillow 12.2.0 combination was removed.

## Repeated tests

- Python compilation passed three consecutive runs.
- Isolated extraction worker processed a generated searchable audit PDF into one finding row in three consecutive runs.
- Actual application AppTest passed three consecutive runs.
- Local Streamlit startup returned HTTP 200 in three consecutive runs.
- Clean ZIP extraction, compilation, import, static validation, worker extraction, and AppTest passed three consecutive runs.

## Integrity

- Original IARS parser logic retained.
- Original PDF Tagging import and Components v2 implementation retained.
- Dashboard, sidebar, avatar, login, archive, document-library, and Master Data behavior retained.
- No old changelogs, old test reports, `__pycache__`, or `.pyc` files included.
