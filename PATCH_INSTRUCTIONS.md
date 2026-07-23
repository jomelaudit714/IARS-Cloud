# IARS V4.4.81 Deployment Instructions

This patch is based on the deployed V4.4.80 application.

## Replace these files in GitHub

1. `app.py`
2. `iars_pdf_editor.py`

Commit the changes, reboot the Streamlit application, then press `Ctrl + F5` in the browser.

## Database and dependencies

- No Supabase SQL is required.
- No `requirements.txt` change is required.

## Expected results

- Policies & Memoranda: all PDF pages appear in one clear, scrollable popup.
- Shared PDF Archive: all PDF pages appear in one clear, scrollable popup.
- PDF Tagging: all pages appear as continuous tag canvases in one popup.
- Generate Extraction: Clear Records is beside the Excel download button.
