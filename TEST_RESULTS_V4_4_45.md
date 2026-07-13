# Test Results – V4.4.45

## Static/code tests
- Version is 4.4.45.
- PDF Tagging Components v2 remains present in `iars_pdf_editor.py`.
- Avatar drag Components v2 present in `iars_auth.py`.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `use_container_width`.
- No `streamlit-cropper`.
- No `st_cropper()`.

## Functional tests
- Avatar crop helper tested using several zoom/x/y combinations.
- Avatar upload signature helper tested.
- Local Streamlit startup returned HTTP 200.
- Separate avatar test app started for isolated avatar component validation.


## Browser automation note
- Attempted Playwright/Chromium browser automation against a separate avatar-only Streamlit test app.
- The local Streamlit test app started, but Chromium navigation was blocked by the execution environment with `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- Because of that environment restriction, browser pointer-drag could not be fully automated here.
- The avatar drag JavaScript, zoom controls, state sync wiring, and crop helper were still validated by static/component-code checks and server startup tests.
