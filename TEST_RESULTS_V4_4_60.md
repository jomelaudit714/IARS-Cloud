# Test Results — V4.4.60

## Root-cause verification

The installed Streamlit 1.47 frontend bundle was inspected directly:

- native restore button: `stExpandSidebarButton`
- saved state key prefix: `stSidebarCollapsed-`
- saved browser state is read before the configured initial sidebar state
- Components v1 iframe policy includes `allow-same-origin` and `allow-scripts`

## Repeated tests

- Python compilation: passed 3 consecutive runs
- successful manual sign-in session flag: passed 3 consecutive AppTest runs
- one-shot sidebar-reset component rendering: passed 3 consecutive AppTest runs
- component iframe parent-button click: passed 3 consecutive browser simulations
- native restore button visibility/clickability: passed 3 consecutive browser simulations
- actual application AppTest: passed 3 consecutive isolated runs
- local Streamlit startup: returned HTTP 200 in 3 consecutive runs
- Streamlit 1.47 API compatibility scan: passed

## Functional behavior verified

- remembered collapsed state is cleared after successful sign-in
- sidebar is expanded after sign-in
- the one-shot reset stops after expansion
- user may manually hide the sidebar afterward
- restore button appears after manual hide
- restore button returns the sidebar
- main content expands while sidebar is hidden

## Integrity

- PDF Tagging remains unchanged
- Dashboard simplification remains
- no old changelogs, old test reports, `__pycache__`, or `.pyc` files are included
