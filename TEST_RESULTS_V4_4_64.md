# Test Results — V4.4.64

## Dependency checks

- `pyarrow==24.0.0` is explicitly pinned.
- No requirement permits `pyarrow==25.0.0`.
- `ARROW_DEFAULT_MEMORY_POOL=system` is configured before pandas and
  application imports in `app.py`.

## Repeated tests

- Python compilation: 3 consecutive passes
- Streamlit 1.47 API compatibility scan: passed
- application AppTest: 3 consecutive passes
- local Streamlit startup: HTTP 200 in 3 consecutive runs
- Arrow threaded import/allocation safety test: 3 consecutive passes using
  the available unaffected local Arrow runtime; the release itself pins
  PyArrow 24.0.0, the unaffected version identified by Apache Arrow.
- Generate Extraction worker test: 3 consecutive passes
- clean-ZIP extract, compile, import, AppTest, and extraction tests:
  3 consecutive passes

## Integrity

- Original `iars_parser.py` retained.
- PDF Tagging retained.
- No old changelogs, old test reports, `__pycache__`, or `.pyc` files.
