# IARS V4.4.99 — Smooth Login, Navigation and Logout

## Changes

- Sidebar navigation now uses pre-rerun callbacks, so the newly selected module is highlighted immediately.
- Fixed the old orange highlight remaining on PDF Tagging after opening Generate Extraction.
- Added a full-page EDL transition mask only for module navigation, successful login, and logout.
- Dashboard and module contents are revealed only after the page completes rendering, preventing cards and panels from appearing one by one.
- Successful login shows the EDL logo while the authenticated workspace is prepared.
- Logout uses a native Streamlit callback and shows the EDL logo while the session is securely cleared and the login page is rebuilt.
- Transition masks use unique navigation tokens so a previous ready marker cannot hide a new transition early.
- Added reduced-motion support.
- No extraction, classification, PDF Tagging, archive, policy, database, or permission logic was changed.
