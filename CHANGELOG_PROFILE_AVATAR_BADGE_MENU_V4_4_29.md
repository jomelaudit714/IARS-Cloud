# IARS V4.4.29 – Single Avatar Camera Badge Fix

## Fixes
- Removed the duplicate visible camera icon on the top-right user card.
- The only visible camera icon is now the existing avatar camera badge.
- The invisible Streamlit click target is aligned over that existing badge only.
- The small camera popup menu now contains only:
  - See Avatar
  - Change Avatar
- Removed the duplicate See Avatar / Change Avatar actions from the Edit Profile popup.

## See Avatar
- Opens a smaller dialog for the avatar image.

## Change Avatar
- Opens a smaller dialog for upload and edit.
- Removed the extra preview card.
- Uses circular crop styling.
- The crop window is visually fixed as a circle.
- User interaction is focused on dragging/positioning the photo and zooming using plus/minus.
- Zoom now remounts the cropper with the zoom value included in the component key so the image visibly expands/shrinks when the zoom changes.

## Save performance
- The save flow keeps the updated avatar in the current session cache instead of forcing an immediate full profile refetch.
