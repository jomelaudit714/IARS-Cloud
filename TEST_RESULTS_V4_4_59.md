# Test Results — V4.4.59

## Selector verification

- Confirmed from the installed Streamlit 1.47.1 frontend bundle that the native restore button uses `data-testid="stExpandSidebarButton"`.
- Confirmed the previous selectors `collapsedControl` and `stSidebarCollapsedControl` do not exist in that Streamlit bundle.

## Repeated tests

- Python compilation passed three consecutive runs.
- Streamlit 1.47 API compatibility scan passed.
- Actual application Streamlit AppTest passed three consecutive runs.
- Local Streamlit startup returned HTTP 200 in three consecutive runs.
- Exact-selector DOM tests passed three consecutive runs:
  - restore control visible after collapse
  - restore control clickable
  - sidebar restored
  - main content expanded while hidden
  - EDL logo remained horizontally centered
- Final clean ZIP extraction, compilation, import, static validation, and AppTest passed three consecutive runs.

## Integrity

- PDF Tagging remains unchanged.
- Dashboard changes from V4.4.58 remain.
- No old changelogs, old test reports, `__pycache__`, or `.pyc` files are included.
