# Test Results — IARS V4.5.03

## Passed

- Python bytecode compilation: `app.py`, `iars_auth.py`
- Python AST parsing: `app.py`, `iars_auth.py`
- Static structure checks:
  - fixed header ID and viewport coordinates present
  - header position no longer depends on the Dashboard marker
  - fixed-header content spacer present
  - profile popover click target covers the top-right user card
  - sign-in form contains exactly one submit control
  - Forgot Password is a link, not a submit control
  - Philippine timezone and `PHT` label retained
  - displayed version is `4.5.03`
  - replacement login artwork exists
- Headless Chromium CSS simulation:
  - Dashboard header top/left/right: `6 / 266 / 1341 px`
  - non-Dashboard header top/left/right: `6 / 266 / 1341 px`
  - computed position: `fixed`
  - computed transform: `none`
  - transparent profile click target received the click
- ZIP integrity and extraction test

## Environment limitation

A full production test against the user's live Supabase and Streamlit Cloud deployment was not possible from the local patch environment. The patch was validated through compilation, structural checks, image inspection, and browser CSS simulation.
