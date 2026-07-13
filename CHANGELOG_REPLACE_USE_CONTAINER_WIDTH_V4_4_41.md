# IARS V4.4.41 – Replace Deprecated use_container_width

## Fixed
- Replaced all `use_container_width=True` with `width="stretch"`.
- Replaced all `use_container_width=False` with `width="content"`.
- This addresses the latest Streamlit Cloud log pattern where `use_container_width` warnings appeared immediately before the segmentation fault.

## Retained
- V4.4.40 removal of old v1 HTML transition guard.
- Avatar drag using Components v2 pattern.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.v1`.
- No `components.html`.
- No `components.declare_component`.

## Files patched
- app.py
- iars_auth.py
- iars_theme.py
