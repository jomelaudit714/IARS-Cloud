# IARS V4.4.67 PDF Tagging Compatibility Patch

## Root cause

The PDF Tagging editor uses `st.components.v2.component`. Custom Components V2
is not available in Streamlit 1.47.1, so opening PDF Tagging raises:

`AttributeError: module 'streamlit.components' has no attribute 'v2'`

## Files to replace

After extracting this patch, replace these three files in the current IARS
GitHub repository:

1. `requirements.txt`
2. `iars_pdf_editor.py`
3. `iars_parser.py`

Do not replace `app.py`, `iars_auth.py`, `iars_theme.py`, `iars_archive.py`, or
any other file.

## What this preserves

- Streamlit is upgraded to `1.58.0`, which supports Components V2.
- `pyarrow==24.0.0` remains pinned to avoid the PyArrow 25 crash.
- Existing PDF/OCR dependency pins remain unchanged.
- The original PDF Tagging v2.9 editor is retained.
- The V4.4.66 Operations Audit `Accounts Confirmation` exclusion rule is retained.
- Current sidebar, duplicate notification, extraction worker, login, avatar, and
  archive fixes remain untouched.

## Deployment

1. Replace the three files above.
2. Commit and push to GitHub.
3. In Streamlit Cloud, reboot the app.
4. Wait for dependencies to reinstall.
5. Refresh the browser using `Ctrl + F5`.
