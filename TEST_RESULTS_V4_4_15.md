# IARS v4.4.15 Validation

- Python compilation: passed
- Profile trigger label changed to a zero-width character: passed
- Trigger button text/content hidden through CSS: passed
- JPG/PNG auto-fit pipeline: passed
  - EXIF orientation correction
  - centered square crop
  - 320 × 320 resize
  - JPEG optimization
- Supabase Storage-first save with database fallback: passed by code-path validation
- Updated SQL includes explicit `service_role` grants: passed
- Preview-only authentication bypass: not included
- Private `.streamlit/secrets.toml`: not included
