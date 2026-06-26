# Login Phase 1 — Viewport Fit Fix

This revision keeps the approved login design and corrects the desktop page-size issue.

## Changes

- Removes Streamlit's hidden top spacing on the login route.
- Locks the login screen to the available browser viewport.
- Prevents vertical and horizontal page scrolling on desktop.
- Uses responsive `100dvh` sizing for the two-panel layout.
- Adds a compact layout for browser viewports up to 720 px high.
- Keeps the approved EDL visual panel, form layout, and navy buttons.
- Does not change authentication, account approval, Supabase, archive, extraction, or Master Data logic.

## Deployment

Upload the ZIP contents directly to the repository root, replacing the existing files. Reboot the Streamlit app and refresh at 100% browser zoom.
