# Test Results – V4.4.54

## Static/code tests
- Version is 4.4.54.
- Supabase secret sanitizer exists.
- `create_auth_client` wraps invalid Supabase config with safer diagnostics.
- Streamlit remains pinned to 1.47.1.
- Image calls do not pass `width="stretch"`.
- PDF Tagging top-level import remains original.
- PDF Tagging Components v2 remains present in `iars_pdf_editor.py`.
- Avatar Components v2 is absent from `iars_auth.py`.
- Simple auto-fit avatar flow is present.
- Centered dialog CSS is present.
- Stale dialog cleanup on navigation is present.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `streamlit-cropper`.
- No `st_cropper()`.

## Functional tests
- Python compile passed.
- Import test passed.
- Secret sanitizer tested against raw key, quoted key, Bearer prefix, and line-break cases.
- Auto-fit avatar crop helper tested using multiple image aspect ratios.
- Local Streamlit startup returned HTTP 200.
- Clean ZIP extract checked.
