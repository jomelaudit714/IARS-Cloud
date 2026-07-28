# Test Results — V4.5.01

## Passed
- Python bytecode compilation for `app.py` and `iars_auth.py`.
- Python AST parsing for both patched files.
- Verified matching V4.5.01 navigation, logout-state, and Sign Out widget keys.
- Verified header uses a fixed UTC+8 Philippine timezone and displays `PHT`.
- Verified known conversion: `08:40 UTC` displays as `04:40 PM PHT`.
- Browser CSS layout simulation confirmed identical header position with and without the module-transition element.
- Verified the module, login, and logout overlays use the detached standalone transition marker.
- Verified displayed system version is `4.5.01`.

## Limitation
A complete Supabase-connected Streamlit Cloud runtime test was not possible because the uploaded package contains patch files rather than the entire deployed repository and its secrets.
