# Test Results — V4.4.61

## Import-mismatch test

The exact Cloud failure was reproduced as a deployment mismatch scenario:
current `app.py` was tested with the older V4.4.59 `iars_theme.py`, which does
not define `force_sidebar_expanded_once`.

Result: the application passed three consecutive AppTest runs without the
ImportError.

## Repeated tests

- Python compilation: passed 3 consecutive runs
- Streamlit 1.47 API compatibility scan: passed
- Actual application AppTest: passed 3 consecutive runs
- Old-theme mismatch AppTest: passed 3 consecutive runs
- Local Streamlit startup: HTTP 200 in 3 consecutive runs
- Local sidebar-helper generation: passed 3 consecutive runs
- Browser sidebar-expansion simulation: passed 3 consecutive runs
- Final clean-ZIP extraction, compilation, import, static checks, and AppTest:
  passed 3 consecutive runs

## Integrity

- Streamlit remains pinned to 1.47.1
- Supabase remains pinned to 2.31.0
- PDF Tagging import and Components v2 implementation remain intact
- Dashboard removals remain
- no `__pycache__`, `.pyc`, old changelogs, or old test reports are included
