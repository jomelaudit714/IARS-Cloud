# IARS V4.4.53 – Streamlit 1.47 Image Compatibility

## Base
- Built from V4.4.52.

## Why
- V4.4.52 successfully moved past the previous Streamlit Cloud segmentation fault.
- The Cloud log then showed a runtime TypeError on `st.image(..., width="stretch")` because Streamlit 1.47.1 does not support string width for images.

## Fixed
- Replaced `st.image(..., width="stretch")` with `st.image(..., use_container_width=True)` for image calls only.
- Kept stable dependency pins from V4.4.52.
- Kept simple auto-fit avatar flow.
- Kept centered See Avatar and Change Avatar dialogs.
- Kept stale dialog cleanup.

## Kept intact
- PDF Tagging remains original and untouched.
- No lazy PDF Tagging.
- No disabled PDF Tagging.
- No avatar component.
- No cropper.

## Remaining environment note
- The Cloud log also shows `SupabaseException: Invalid API key`.
- That is caused by Streamlit Cloud Secrets and must be corrected in the app secrets.
