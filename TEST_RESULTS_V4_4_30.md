# Test Results – V4.4.30

## Passed
- Python compile check passed for app.py, iars_auth.py, iars_archive.py, iars_document_library.py, iars_parser.py, iars_pdf_editor.py, and iars_theme.py.
- Reproduced the reported `aspect_ratio` issue path and confirmed `_avatar_circle_box_algorithm(..., aspect_ratio=(1,1))` now passes.
- Helper tests passed for profile image load, zoomed image generation, circle crop box generation, and JPEG output.
- Verified static state logic:
  - no duplicate avatar action keys inside Edit Profile,
  - See Avatar clears Change Avatar state,
  - Change Avatar clears See Avatar state,
  - dialog rendering uses `if / elif` to prevent more than one dialog from opening.
- Local Streamlit render started successfully using `python3 -m streamlit run app.py`.
- Local root page returned HTTP 200.

## Notes
- Streamlit deprecation warnings for `st.components.v1.html` and `use_container_width` are not the Change Avatar crash. They can be cleaned separately.
