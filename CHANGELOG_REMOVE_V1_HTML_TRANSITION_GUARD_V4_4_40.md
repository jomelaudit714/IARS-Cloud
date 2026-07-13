# IARS V4.4.40 – Remove v1 HTML Transition Guard

## Fixed
- Removed the remaining `st.components.v1.html` usage from `iars_theme.py`.
- The old browser-side loading/transition guard is now disabled.
- This addresses the deployment log pattern where `st.components.v1.html` warnings appeared before the segmentation fault.

## Retained
- Avatar drag editor from V4.4.39 using Streamlit Components v2, same pattern as PDF Tagging.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.declare_component()`.
- No local component folder dependency.

## Notes
- PDF Tagging still uses Components v2.
- Avatar drag uses Components v2.
- The old v1 HTML route/auth transition veil is removed.
