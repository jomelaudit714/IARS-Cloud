# IARS v4.4.17 — Smooth Top-Right Profile Menu

## Fixed
- Replaced the top-right profile-menu trigger with a front-end Streamlit popover using `on_change="ignore"` so opening and closing the user card no longer triggers a full app rerun.
- Removed the separate close/X Streamlit rerun path that caused white-screen flicker and lag.
- Added a short instruction inside the menu: close by clicking the top-right user card again or anywhere outside the menu.
- Moved Supabase profile table/storage diagnostics out of menu-open rendering. Diagnostics now run only when saving/removing a profile picture.
- Kept profile picture auto-fit behavior: JPG/PNG is centered, square-cropped, compressed, and resized to 320 × 320.
- Updated app header version to v4.4.17.

## Notes
- No new Supabase SQL is required if `SUPABASE_PROFILE_SETUP.sql` was already executed.
- The profile menu save/update actions still rerun only when data is actually submitted, which is normal Streamlit behavior.
