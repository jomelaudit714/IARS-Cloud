# TEST_RESULTS_V4_4_18

## Static Checks
- `python -m py_compile app.py iars_auth.py iars_theme.py iars_archive.py iars_document_library.py iars_parser.py iars_pdf_editor.py` passed.

## Local Render Checks
- Streamlit server started successfully in headless mode.
- `/_stcore/health` returned `ok`.
- Unauthenticated login/setup render completed without script exception.
- Authenticated dashboard simulation completed without script exception.
- Profile menu rendered with Update Username, Update Password, Save Picture, Remove Picture, and front-end Sign Out link.
- Sidebar navigation simulation to Generate Extraction completed without script exception.
- Sign-out route simulation returned to the login page with Username and Password fields only.

## Notes
- Live Supabase credential validation and live Storage upload cannot be fully executed in this sandbox because the deployed app's production Streamlit Secrets are not available here.
- The runtime warning about `st.components.v1.html` is a Streamlit deprecation warning from the local test environment; it did not stop rendering or health checks.
