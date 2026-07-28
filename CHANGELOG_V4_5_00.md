# IARS V4.5.00 — Fixed Header Position and Delayed EDL Loader

## Changes

- Fixed the authenticated page header moving downward after switching modules.
- Applied one consistent top spacing to Dashboard, Weekly Itinerary, Audit Workpapers, Policies & Memoranda, PDF Tagging, Generate Extraction, User Management, Master Data, Settings, and the other authenticated pages.
- Detached the navigation/login/logout transition HTML from Streamlit's normal vertical layout so a hidden transition can no longer create blank space above the header.
- The full-page transition cover starts immediately to conceal partial rendering, but the EDL logo, title, and progress line wait approximately 520 milliseconds before appearing.
- Fast transitions complete without showing the EDL logo.
- Slow module transfers, successful login, and logout show the EDL transition automatically.
- Kept the selected sidebar module synchronized before rerender, including PDF Tagging and Generate Extraction.
- Updated the visible system version to `4.5.00` and versioned the related transition/session keys to avoid stale state from V4.4.99.
- No extraction, PDF Tagging, archive, policy, Weekly Itinerary, database, permission, or classification logic was changed.
