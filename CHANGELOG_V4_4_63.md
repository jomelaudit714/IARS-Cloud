# Changelog — V4.4.63

## Dependency installation fix

The V4.4.62 dependency set could not install because:

- Streamlit 1.47.1 requires Pillow below version 12.
- pdfplumber 0.11.10 requires Pillow 12.2.0 or newer.

Those two requirements cannot be satisfied together.

## Corrected compatible stack

- `streamlit==1.47.1`
- `pdfplumber==0.11.9`
- `Pillow==11.3.0`
- `PyMuPDF==1.27.2.3`

`pdfplumber==0.11.9` supports Pillow 9.1 or newer, while Streamlit 1.47.1 supports Pillow below 12. Pillow 11.3.0 satisfies both.

## Retained unchanged

- Original IARS parser logic
- Isolated extraction worker
- Generate Extraction workflow and output structure
- Dashboard and sidebar behavior
- EDL theme, logo, colors, fonts, cards, borders, and shadows
- Avatar/camera and login fixes
- Original PDF Tagging implementation
