# IARS V4.4.34 – Avatar Drag Editor Import Fix

## Fixed
- Fixed `NameError: name 'Path' is not defined` in `iars_auth.py`.
- Added `from pathlib import Path` before the custom avatar component directory is declared.
- Retained the custom drag avatar editor from V4.4.33.
- Retained removal of `streamlit-cropper`.

## Tests
- Python import check for `iars_auth.py`.
- Python compile check for main files.
- Local Streamlit render check.
