# IARS V4.4.31 – Change Avatar Crash Fix

## Fixed
- Fixed `UnboundLocalError: orig_file` from `streamlit-cropper`.
- Kept the cropper resize path enabled because `streamlit-cropper==0.2.2` crashes when `should_resize_image=False`.
- Kept `_avatar_circle_box_algorithm` compatible with extra cropper keyword arguments such as `aspect_ratio`.
- Added a single avatar dialog mode to prevent See Avatar and Change Avatar from opening together.
- Camera menu actions now route through one mode setter.

## Notes
- The warnings about `st.components.v1.html` and `use_container_width` are deprecation warnings only and are not the Change Avatar crash.
