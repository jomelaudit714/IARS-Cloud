# Test Results

- Python compilation passed: `app.py`, `iars_auth.py`, `iars_theme.py`.
- AST parsing passed for all three Python files.
- 100 repeated render-function cycles passed for login and sidebar branding.
- Verified login artwork is emitted through the new HTML/data-URI renderer, not `st.image()`.
- Verified sidebar logo is emitted through the new HTML/data-URI renderer, not `st.image()`.
- Verified `object-fit: contain`, centered positioning, and no transform/scale rules are present.
- Verified `assets/login_left_panel.png` exactly matches the supplied `login_left_panel(2).png` by SHA-256 hash.
- Verified `assets/sidebar_edl_logo.png` exactly matches the supplied `sidebar_edl_logo.png` by SHA-256 hash.
- Verified image dimensions: login panel `1122×1402`; sidebar logo `470×325`.
- Created a 1366×768 render-layout preview showing the full login artwork and readable sidebar branding.

A complete Supabase-connected Streamlit production test was not possible because only the three source files and assets were supplied, not the entire repository and secrets.
