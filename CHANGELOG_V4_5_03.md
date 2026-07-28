# IARS V4.5.03 — Root-Cause UI Fixes

## Corrected

- Replaced module-dependent header offsets with one viewport-fixed header position.
- Header now uses the same `top`, `left`, and `right` coordinates on Dashboard and all other modules.
- Added a dedicated content spacer so the fixed header does not overlap page content.
- Realigned the transparent Streamlit profile popover trigger with the visual top-right user card.
- Preserved the separate avatar camera trigger above the user-card trigger.
- Changed Forgot Password from a form submit button to a normal link.
- The sign-in form now contains only one submit button, so Enter in Username or Password submits Sign In.
- Replaced the login artwork with an edge-to-edge image and moved only the EDL logo to the horizontal center of the “INTERNAL AUDIT REPORT SYSTEM” title block.
- Retained Philippine time (`PHT`, UTC+8) in the header.
- Retained delayed EDL transition branding for slower module, login, and logout transitions.

## Version

- Displayed system version: `4.5.03`
