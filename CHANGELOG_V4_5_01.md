# IARS V4.5.01 — Fixed Header Position and Philippine Time

## Header position
- Removed the module-transition overlay from Streamlit's normal vertical layout flow.
- The header no longer receives an extra blank row when switching modules.
- Raised the header slightly closer to the top of the workspace.
- Applied the same fixed header position across Dashboard, Weekly Itinerary, Generate Extraction, PDF Tagging, Shared PDF Archive, Audit Workpapers, Policies & Memoranda, User Management, Master Data, and Settings.

## Transition behavior
- The transition overlay still starts immediately during module changes.
- The EDL logo remains delayed and appears only when the transition lasts longer than approximately 520 milliseconds.
- Login and logout overlays use the same detached layout treatment so they do not alter page positioning.

## Header time
- Header date and time now use Philippine Standard Time, UTC+8.
- The header displays `PHT` to make the timezone explicit.

## Version
- Updated displayed system version to `4.5.01`.
