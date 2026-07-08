# V4.4.16 - Profile Menu, Upload Smoothness and Refresh Session Fix

Implemented fixes based on the submitted refresher video:

1. Top-right profile card trigger
   - Expanded and realigned the invisible click area over the actual top-right user card.
   - Kept the trigger visually clean with no visible extra box.

2. Close button tooltip cleanup
   - Removed the help/tooltip text from the X close button so the unwanted close notification no longer appears.

3. Profile picture upload smoothness
   - Improved the upload label and compact uploader area.
   - Added immediate optimized square preview before saving.
   - Added a clear message when Save Picture is clicked without selecting a file.
   - Keeps JPG/PNG auto-fit behavior by square-cropping and resizing to 320 x 320.

4. Browser refresh behavior
   - Added a signed persistent browser-session token in the app URL query state.
   - If Remember me is checked, the login can survive browser refresh for 7 days.
   - If Remember me is not checked, the login can still survive a normal refresh within the configured session timeout.
   - Sign Out now clears the saved session token and auth query parameters.

No new Supabase SQL table is required for this build.
