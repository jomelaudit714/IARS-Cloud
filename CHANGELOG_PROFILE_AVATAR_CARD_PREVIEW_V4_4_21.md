# IARS V4.4.21 – Profile Avatar Card Preview UI

## Why this update
- V4.4.20 used the default streamlit-cropper interface. It worked, but the UI looked too plain and did not resemble the profile-card mockup.

## Fixed / Improved
- Added a polished profile-card style preview inside Change Profile Picture.
- The live preview now shows the circular avatar inside a mini version of the top-right user card.
- Reduced the cropper canvas size so portrait photos no longer appear as an oversized tall editor.
- Added clear two-step layout: `1. Position photo` and `2. Check circle result`.
- Kept the optimized 320x320 JPEG output for the saved profile photo.

## Notes
- The cropper remains the actual editing tool because Streamlit needs a component that can return the cropped image to Python.
- The preview is now styled to match the IARS top-right profile card more closely.
