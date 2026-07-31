# IARS V4.5.08 — Login and Sidebar Asset Fix

## Root fixes
- Replaced the login artwork with the supplied `login_left_panel(2).png` as `assets/login_left_panel.png`.
- Replaced the sidebar logo with the supplied `sidebar_edl_logo.png`.
- Changed login artwork rendering from Streamlit `st.image()` to a data-URI HTML image so the browser uses one controlled element.
- Enforced `object-fit: contain`, centered positioning, no transform, no scale, and a matching navy background.
- Changed sidebar logo rendering from Streamlit `st.image()` to a data-URI HTML image so generic Streamlit image CSS cannot darken, square, or replace it.
- Kept the sidebar text `EDL GROUP OF COMPANIES` in pale cream `#F7E7B2`.
- Updated the visible system version to `4.5.08`.

## Files changed
- `app.py`
- `iars_theme.py`
- `assets/login_left_panel.png`
- `assets/sidebar_edl_logo.png`

## Included unchanged source
- `iars_auth.py`
- Other supplied assets
