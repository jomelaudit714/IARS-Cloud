# IARS V4.4.42 – Remove Avatar Components v2

## Fixed
- Removed avatar Components v2 drag editor from `iars_auth.py`.
- Latest Streamlit Cloud logs showed segmentation fault even after v1 HTML and `use_container_width` warnings were removed.
- The likely remaining trigger was the avatar component path, so avatar editing now uses native Streamlit controls only.

## Retained
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `use_container_width`.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.declare_component`.
- PDF Tagging remains unchanged and still uses its existing Components v2 editor.

## Avatar editor
- Upload photo.
- Zoom minus/plus.
- Move photo with arrow buttons.
- Movement speed: Fine / Normal / Coarse.
- Optional sliders for precise positioning.
- Server-side PIL crop and save.
