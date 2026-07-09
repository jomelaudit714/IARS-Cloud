# IARS V4.4.28 – Avatar Badge Menu + Smaller Dialogs

## Updated behavior
- Removed the extra floating camera icon that was separate from the avatar.
- The clickable camera control is now aligned to the existing camera badge area on the avatar.
- Clicking the avatar camera badge now opens a small popup menu with:
  - **See Avatar**
  - **Change Avatar**
- Removed the duplicate **See Avatar / Change Avatar** actions from the Edit Profile popup.

## See Avatar
- Opens in a smaller dialog, intended to occupy about one-third to one-quarter of the screen.

## Change Avatar
- Opens in a smaller dialog, intended to occupy about one-third of the screen.
- Removed the extra preview card to save space.
- Uses a circular crop area.
- The circular crop area is kept visually fixed, while the user drags/positions the photo.
- Zoom control uses plus and minus controls and is clamped at the maximum zoom limit.
- Set the cropper to avoid internal auto-resizing so zooming has a visible effect.

## Performance
- Save flow continues to use cached diagnostics first to reduce save lag.
