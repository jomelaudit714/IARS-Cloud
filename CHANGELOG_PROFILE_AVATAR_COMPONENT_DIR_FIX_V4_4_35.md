# IARS V4.4.35 – Avatar Component Directory Fix

## Fixed
- Fixed Streamlit Cloud startup error:
  `StreamlitAPIException: No such component directory: '/mount/src/iars-cloud/components/avatar_drag_editor'`.
- The app no longer crashes if the component folder is missing from the deployed repository.
- The avatar drag editor HTML is embedded in `iars_auth.py` and recreated in `/tmp` at runtime when needed.
- Retained packaged folder `components/avatar_drag_editor/index.html` in the ZIP.
- Retained custom drag behavior:
  - fixed circular crop area
  - drag image inside circle
  - plus/minus zoom
  - centered popup/dialog

## Stability
- No `streamlit-cropper` package.
- No `st_cropper()` call.
