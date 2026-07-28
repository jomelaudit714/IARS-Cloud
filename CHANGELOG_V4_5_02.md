# IARS V4.5.02 — Uniform Sticky Header and Enter-to-Sign-In Fix

## Changes

- Matched the authenticated header position of all modules to the approved Dashboard header position.
- Applied a measured 29-pixel recovery to non-Dashboard modules so Generate Extraction, PDF Tagging, Shared PDF Archive, Weekly Itinerary, Audit Workpapers, Policies & Memoranda, User Management, Master Data, and Settings no longer render the header lower than Dashboard.
- Added a matching negative bottom margin so module content also moves upward and no empty band remains below the header.
- Made the authenticated header sticky near the top while scrolling.
- Retained Philippine Standard Time in the header using UTC+8 and the `PHT` label.
- Moved the EDL artwork in the login left panel farther to the right to align it with the `INTERNAL AUDIT REPORT SYSTEM` text.
- Added a hidden first Sign In submit control. Pressing Enter after typing the password now performs the same action as clicking the visible `Sign In` button and no longer opens `Forgot password`.
- Retained the delayed EDL transition logo for slower module, login, and logout transitions.
- Updated the displayed system version to `4.5.02`.
