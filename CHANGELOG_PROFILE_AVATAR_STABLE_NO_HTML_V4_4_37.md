# IARS V4.4.37 – Stable Avatar Editor Without HTML Components

## Fixed
- Removed the crash path from avatar editing.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.declare_component()`.
- No `st.components.v1.html` usage for avatar editing.
- No local component folder dependency.

## Reason
Streamlit Cloud logs showed segmentation fault after `st.components.v1.html` warnings.  
To keep the app stable, the avatar editor now uses only native Streamlit controls plus PIL image processing.

## Avatar editor
- Upload photo
- Zoom in / zoom out
- Move photo left / right
- Move photo up / down
- Circular preview
- Save / Cancel

## Note
Mouse-drag requires JavaScript/HTML component behavior. That path was removed because it caused Streamlit Cloud crashes in this deployment.
