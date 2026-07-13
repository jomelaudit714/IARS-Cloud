# IARS V4.4.36 – Inline Drag Avatar Editor

## Fixed
- Removed custom component declaration completely.
- Removed dependency on local folder `components/avatar_drag_editor`.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.declare_component()`.

## Avatar Editor
- Uses inline HTML inside Streamlit to show:
  - fixed circular crop area
  - drag image inside the circle
  - zoom with minus/plus
- The actual saved image is cropped server-side using PIL from the uploaded file and current crop coordinates.
- This avoids the Streamlit Cloud error:
  `StreamlitAPIException: No such component directory`.

## Notes
- `st.components.v1.html` may still show a deprecation warning in Streamlit logs, but it is not the same crash path as local component declaration.
