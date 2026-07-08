# Test Results — IARS v4.4.17

## Static checks
- `python -m py_compile *.py` completed successfully.

## Local render simulation
- Created a local Streamlit profile-menu render harness using the actual theme/header/profile-menu functions.
- Streamlit AppTest rendered the profile menu without exceptions.
- Verified the expected profile actions rendered:
  - Update Username
  - Update Password
  - Save Picture
  - Remove Picture
  - Sign Out

## Behavior validated by source implementation
- Profile menu uses `st.popover(..., on_change="ignore")`, so opening/closing the top-right user card is handled by the browser front-end and does not trigger a full Streamlit script rerun.
- Profile setup diagnostics are not executed on menu open; they execute only during save/remove picture actions.
