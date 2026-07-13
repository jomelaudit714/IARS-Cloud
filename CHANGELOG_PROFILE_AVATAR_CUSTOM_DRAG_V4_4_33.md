# IARS V4.4.33 – Custom Drag Avatar Editor

## Fixed / Improved
- Added a custom lightweight avatar drag editor component.
- Removed dependency on `streamlit-cropper`; no third-party cropper package is used.
- Restored drag behavior:
  - fixed circular crop area
  - image is dragged inside the circle
  - plus/minus zoom expands/shrinks the image
  - output is returned as a 320x320 JPEG data URI
- Retained:
  - avatar camera badge menu
  - See Avatar
  - Change Avatar
  - centered dialogs
  - Save / Cancel

## Stability
- This avoids the `streamlit-cropper` `orig_file` crash and the segmentation fault path.
