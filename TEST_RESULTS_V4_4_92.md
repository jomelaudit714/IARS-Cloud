# Test Results — IARS V4.4.92

- Python syntax compilation for `app.py` and `iars_pdf_editor.py`: passed 3 consecutive runs.
- Embedded PDF editor JavaScript syntax (`node --check`): passed.
- Outside-click/box-switch commit delay constant: verified at 1000 ms.
- Continuous typing path: verified to update browser-local backup without scheduling Streamlit idle synchronization.
- Leave/close paths: verified to call immediate flush logic.
- Context-menu-specific save path: removed.
- Components v2 key normalization: tested with spaces, parentheses, repeated underscores, hyphens, and periods; no generated key contained `__`.
- Version labels: verified as 4.4.92.
