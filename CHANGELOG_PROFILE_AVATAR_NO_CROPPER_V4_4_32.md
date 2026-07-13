# IARS V4.4.32 – Stable Avatar Editor Without streamlit-cropper

## Fixed
- Removed `streamlit-cropper` dependency and component usage.
- This avoids the Streamlit Cloud segmentation fault and the prior `orig_file` cropper crash.
- Retained the existing avatar camera badge menu:
  - See Avatar
  - Change Avatar
- See Avatar and Change Avatar still open centered dialogs.
- Change Avatar now uses pure Streamlit + PIL processing:
  - Upload photo
  - Zoom in/out
  - Horizontal/vertical positioning
  - Circular output preview
  - Save/Cancel

## Notes
- The previous drag-based component was removed because it was causing deployment/runtime crashes.
- This build prioritizes deployment stability and smooth save behavior.
