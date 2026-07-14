# IARS V4.4.56 – Cloud Stability for V4.4.55 Fixes

## Base lineage
- User-confirmed V4.4.51 remains the base.
- V4.4.55 camera, avatar-dialog, and login Enter-key fixes are retained.

## Why
- Streamlit Cloud installed Streamlit 1.58.0 and the newest dependency set.
- The app then returned to the previous segmentation fault immediately after Uvicorn started.

## Fixed
- Pinned Streamlit Cloud dependencies to safer versions:
  - streamlit==1.47.1
  - pandas==2.2.3
  - numpy==2.0.2
  - openpyxl==3.1.5
  - pdfplumber==0.11.5
  - PyMuPDF==1.24.14
  - Pillow==10.4.0
  - pytesseract==0.3.13
  - supabase==2.31.0
- Retained Supabase 2.31.0 so the existing current-format Supabase key remains supported.
- Replaced `st.image(..., width="stretch")` with Streamlit 1.47-compatible image sizing.

## Retained from V4.4.55
- Camera icon consistently opens See Avatar / Change Avatar.
- Change Avatar popup fits vertically.
- Enter key submits Sign In instead of Forgot Password.
- PDF Tagging remains original and untouched.
