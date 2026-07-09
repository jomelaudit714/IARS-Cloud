# IARS V4.4.30 – Change Avatar Error Fix

## Fixed
- Fixed the Change Avatar crash:
  - `_avatar_circle_box_algorithm()` now accepts additional cropper arguments such as `aspect_ratio`.
- Fixed the Streamlit dialog error:
  - The avatar flow now opens only one dialog per script run.
  - Opening See Avatar automatically clears Change Avatar state.
  - Opening Change Avatar automatically clears See Avatar state.
- Centered the See Avatar / Change Avatar small menu button text.

## Retained
- Single invisible click target over the existing avatar camera badge.
- No duplicate visible camera icon.
- No See Avatar / Change Avatar buttons inside Edit Profile.
- Small See Avatar dialog.
- Small Change Avatar dialog with upload, zoom +/- and circle crop.
