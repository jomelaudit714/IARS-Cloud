# IARS V4.4.22 – Custom Profile Avatar Preview

## Fixed
- Removed the default tall cropper interface that appeared as a long white panel inside the profile menu.
- Replaced it with a compact custom profile-card preview that shows the actual circular avatar result before saving.
- Added functional controls for Zoom, Move left/right, and Move up/down so the user can adjust the picture without the laggy/tall cropper UI.
- Saved output remains optimized as a 320x320 JPEG.

## Notes
- This version intentionally does not use `streamlit-cropper`; it avoids the interface shown in the user's video.
