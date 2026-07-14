# Changelog — V4.4.64

## Root cause

Streamlit Cloud successfully installed V4.4.63, but the dependency resolver
selected `pyarrow==25.0.0`. Apache Arrow has confirmed a SIGSEGV defect in that
release's bundled mimalloc when Arrow is used from multiple threads. Streamlit
runs application scripts in ScriptRunner threads, which matches the affected
execution pattern.

## Correction

- Added `pyarrow==24.0.0` to `requirements.txt`.
- Added `ARROW_DEFAULT_MEMORY_POOL=system` at the very beginning of
  `app.py`, before pandas and application modules are imported.
- Kept Streamlit at 1.47.1, pandas at 2.2.3, and the V4.4.63 PDF dependencies.

## Unchanged

- Generate Extraction parser and mapping rules
- isolated extraction worker
- PDF Tagging
- Dashboard and sidebar
- avatar and login functions
- Supabase and archive modules
