# V4.5.06 Test Results

- Python compilation passed for `app.py`, `iars_auth.py`, and `iars_theme.py`.
- Browser rendering test passed at 1366x768.
- Sidebar logo center: 119 px.
- Sidebar center: 119 px.
- Separate company text computed color: `rgb(247, 231, 178)`.
- Dashboard Welcome computed top margin: `-24.8px`.
- Rendered distance from header bottom to Welcome section: approximately `23.2px` in the test layout.
- The sidebar-specific logo visibly contains light `GROUP OF COMPANIES` text.

The test used the uploaded current source files and the same sidebar/header/welcome CSS paths. A live authenticated Supabase deployment was not started because the complete repository modules and production secrets were not provided.
