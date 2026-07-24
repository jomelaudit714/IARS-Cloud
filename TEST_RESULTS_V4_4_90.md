# Test Results — V4.4.90

- Python syntax compilation: passed 3 consecutive runs.
- Persistent-close helper presence and invocation: passed.
- Version label and Settings version: passed.
- Browser DOM simulation using the Streamlit 1.58/BaseWeb-style scrolling modal:
  - floating close appeared when the dialog opened;
  - remained fixed and visible after scrolling more than 1,500 px;
  - stayed aligned with the dialog's right edge;
  - clicked the native close action successfully;
  - disappeared automatically after the dialog closed.
- Clean ZIP extraction and compilation: passed 3 consecutive runs.
- No `__pycache__` or `.pyc` files are included.
