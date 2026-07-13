# IARS V4.4.38 – Native Drag-like Avatar Editor

## Fixed / Improved
- Added native Streamlit drag-like avatar movement controls.
- No HTML/component path.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `st.components.v1.html`.
- No `components.declare_component()`.
- No local component folder dependency.

## Avatar editor
- Fixed circular preview.
- Zoom minus/plus.
- Arrow buttons move the image inside the circle:
  - Up
  - Down
  - Left
  - Right
- Movement speed:
  - Fine
  - Normal
  - Coarse
- Optional fine-tune sliders remain inside an expander.
- Center button resets image position.

## Note
Actual mouse-drag is not possible in Streamlit without browser JavaScript/HTML/component code.
This version gives drag-like positioning while avoiding the crash path seen in Streamlit Cloud.
