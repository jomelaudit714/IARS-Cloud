# IARS V4.4.43 – Avatar Upload Signature Helper Fix

## Fixed
- Restored `_avatar_upload_signature()` helper defensively in `iars_auth.py`.
- This fixes the Streamlit traceback:
  `NameError: name '_avatar_upload_signature' is not defined`.

## Retained
- No avatar Components v2.
- No `streamlit-cropper`.
- No `st_cropper()`.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `use_container_width`.

## Avatar editor
- Stable native Streamlit controls only:
  - upload photo
  - zoom minus/plus
  - arrow movement
  - Fine / Normal / Coarse movement speed
  - optional sliders
  - server-side PIL crop/save
