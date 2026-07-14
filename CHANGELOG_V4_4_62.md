# Changelog — V4.4.62

## Generate Extraction stability

- Confirmed `iars_parser.py` remains byte-for-byte identical to the user-approved V4.4.51 parser.
- Confirmed the Generate Extraction workflow logic was not replaced; only Streamlit 1.47 display keywords had changed.
- Restored the PDF/OCR package versions used by V4.4.51:
  - pdfplumber 0.11.10
  - PyMuPDF 1.27.2.3
  - Pillow 12.2.0
- Runs the unchanged parser in an isolated worker process. A native PDF-engine crash can no longer terminate the main Streamlit app.
- Keeps all approved sidebar, Dashboard, avatar, login, archive, and PDF Tagging behavior.
