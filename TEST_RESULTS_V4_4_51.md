# Test Results – V4.4.51

## Static/code tests
- Version is 4.4.51.
- Built from user-uploaded V4.4.43 base.
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
- No `use_container_width`.
- No `streamlit-cropper`.
- No `st_cropper()`.

## Functional tests
- Python compile passed.
- Import test passed.
- Auto-fit avatar crop helper tested using multiple image aspect ratios.
- Local Streamlit startup returned HTTP 200.
- Clean ZIP extract checked.
