# IARS V4.5.05 — Login Panel and Sidebar Text Fix

## Changes
- Login left-panel artwork now uses `object-fit: contain` with no translate or scale transform, preventing the poster from appearing zoomed or cropped.
- The approved `assets/login_left_panel.png` is included unchanged.
- The internal system sidebar text `EDL GROUP OF COMPANIES` is now a brighter pale-cream color (`#F7E7B2`) with stronger readability.
- Visible application version updated to `4.5.05`.

## Files to replace
- `app.py`
- `iars_auth.py`
- `iars_theme.py`
- `assets/login_left_panel.png`
