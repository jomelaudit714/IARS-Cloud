# IARS V4.4.47 – Crop Circle Selection Avatar Editor

## Concept change
- Instead of dragging the picture, the avatar editor now presents the workflow as moving the crop circle/selection area.
- The final avatar is based on the selected crop circle area.

## Cloud-safe implementation
- Mouse-dragging the crop circle still requires browser JavaScript/component code and caused Streamlit Cloud segmentation faults in prior builds.
- This version uses native Streamlit movement controls:
  - move crop circle left/right/up/down
  - center crop circle
  - fine/normal/coarse movement speed
  - zoom in/out
  - optional sliders
  - live circular avatar preview

## Kept intact
- Original PDF Tagging remains intact.
- PDF Tagging Components v2 remains present in `iars_pdf_editor.py`.
- PDF Tagging is not disabled.

## Safety retained
- No avatar Components v2 in `iars_auth.py`.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `use_container_width`.
- No `streamlit-cropper`.
- No `st_cropper()`.
