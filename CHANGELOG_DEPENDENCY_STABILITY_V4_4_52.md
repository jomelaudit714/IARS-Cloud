# IARS V4.4.52 – Dependency Stability Build

## Base
- Built from V4.4.51, which was built from the user-uploaded V4.4.43 base.

## Why
- Streamlit Cloud continued to segfault immediately after Uvicorn started even after avatar components/croppers were removed.
- The Cloud log showed very new runtime packages being installed:
  - streamlit 1.58.0
  - pandas 3.0.3
  - numpy 2.5.1
  - Pillow 12.2.0
  - PyMuPDF 1.27.2.3
  - pdfminer-six 20260107
  - supabase 2.31.0
- This build pins dependencies to safer stable versions to reduce native/runtime crash risk.

## Kept intact
- PDF Tagging remains original and untouched.
- No lazy PDF Tagging.
- No disabled PDF Tagging.
- Simple auto-fit avatar flow remains.
- Centered See Avatar and Change Avatar dialogs remain.
- Stale dialog cleanup remains.

## Requirements pinned
- streamlit==1.47.1
- pandas==2.2.3
- numpy==2.0.2
- openpyxl==3.1.5
- pdfplumber==0.11.5
- PyMuPDF==1.24.14
- Pillow==10.4.0
- pytesseract==0.3.13
- supabase==2.15.3
