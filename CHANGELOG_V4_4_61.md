# Changelog — V4.4.61

## Root cause fixed

The Streamlit Cloud deployment failed because `app.py` imported
`force_sidebar_expanded_once` from `iars_theme.py`, but the deployed
`iars_theme.py` did not contain that function.

## Robust deployment fix

- The one-time sidebar-expansion helper now lives directly in `app.py`.
- `app.py` no longer imports `force_sidebar_expanded_once` from `iars_theme.py`.
- `app.py` no longer imports the new sidebar session-key constant from `iars_auth.py`.
- The session-state key is defined locally in `app.py`.
- This prevents the application from crashing when GitHub temporarily contains
  mixed versions of `app.py` and `iars_theme.py`.

## Sidebar behavior retained

- The sidebar opens after every successful manual sign-in.
- A user may still hide it manually afterward.
- The navy-and-gold restore button remains visible and clickable.
- The main workspace expands while the sidebar is hidden.

## Unchanged

- EDL theme, logo, colors, fonts, borders, shadows, icons, and header
- Dashboard simplification
- avatar/camera and login fixes
- original PDF Tagging implementation
