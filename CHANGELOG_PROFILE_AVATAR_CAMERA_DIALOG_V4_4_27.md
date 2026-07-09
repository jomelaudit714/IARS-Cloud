# IARS V4.4.27 – Separate Camera Popup + Circle Editor

## Updated avatar behavior
- Clicking the small camera icon on the top-right user card now opens a **separate avatar editor dialog**.
- The avatar editor is no longer shown under the username/password area.
- The user-card popup still contains the **See Avatar** and **Change Avatar** actions.
- **See Avatar** opens a separate dialog with the larger avatar view.
- **Change Avatar** opens the separate editor dialog.

## Avatar editor changes
- Removed the extra preview card to save space.
- The editor now focuses on one crop area only.
- The crop area is styled as a circle to better match the target avatar output.
- The edit flow now uses only:
  - upload photo
  - zoom in / zoom out (+ and -)
  - drag crop positioning
  - Save / Cancel
- The zoom control is clamped so it stops increasing once the maximum zoom is reached.

## Performance-related updates
- Profile storage diagnostics now use cached results before forcing a refresh during save, to reduce save lag.
