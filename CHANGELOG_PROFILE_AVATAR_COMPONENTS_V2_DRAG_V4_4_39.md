# IARS V4.4.39 – Avatar Drag Using Components v2

## What changed
- Rebuilt avatar drag using Streamlit Components v2, following the same approach used by PDF Tagging.
- This avoids the old `st.components.v1.html` path that triggered Streamlit Cloud segmentation faults.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.declare_component()`.
- No local component folder dependency.

## Avatar editor
- Fixed circular crop area.
- Mouse-drag the picture inside the circle.
- Zoom with minus/plus and range slider.
- Server-side PIL save crop.

## Safety
- Fallback native controls remain under an expander if drag does not update.
