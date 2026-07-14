# Changelog — V4.4.60

## Base

Built from the clean V4.4.59 ZIP.

## Default sidebar after sign-in

Streamlit 1.47 saves the collapsed state in browser localStorage under keys beginning with `stSidebarCollapsed-`. That saved browser value takes priority over `initial_sidebar_state="expanded"`.

This build now:

- creates a one-time expansion token after every successful manual sign-in
- clears the remembered collapsed values once
- clicks Streamlit's native `stExpandSidebarButton` when required
- opens the workspace with the sidebar visible after sign-in
- stops immediately after expansion, so the user may still hide the sidebar manually afterward

## Restore button

- corrected the toolbar rule that was hiding the parent of `stExpandSidebarButton`
- keeps the exact native Streamlit restore control visible and clickable after manual collapse
- retains the existing EDL navy-and-gold design
- keeps the main interface expanded while the sidebar is hidden

## Unchanged

- EDL theme, logo, colors, fonts, borders, shadows, icons, and header
- Dashboard changes from V4.4.58
- avatar/camera and login Enter-key fixes
- original PDF Tagging implementation
