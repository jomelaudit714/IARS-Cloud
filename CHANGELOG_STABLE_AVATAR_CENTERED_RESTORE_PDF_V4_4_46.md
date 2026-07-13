# IARS V4.4.46 – Stable Avatar, Centered Dialogs, PDF Tagging Intact

## Corrected after V4.4.45 Cloud crash
- V4.4.45 still segfaulted immediately after Uvicorn start.
- The avatar browser drag component was removed again for Cloud stability.
- Actual browser drag requires a custom JS/component path, which is the path triggering Streamlit Cloud segmentation faults.

## Kept intact
- Original PDF Tagging remains intact.
- PDF Tagging Components v2 remains present in `iars_pdf_editor.py`.
- PDF Tagging is not disabled.

## Avatar
- See Avatar dialog is centered.
- Change Avatar dialog is centered.
- Upload supports JPG, JPEG, PNG.
- Crop output is saved as JPEG.
- Stable circular crop preview remains.
- Zoom and movement controls remain.
- Browser mouse-drag is disabled to prevent Cloud crash.

## Safety retained
- No avatar Components v2 in `iars_auth.py`.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `use_container_width`.
- No `streamlit-cropper`.
- No `st_cropper()`.
