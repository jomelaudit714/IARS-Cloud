# Test Results — V4.4.58

## Code and compatibility

- Python compilation passed three consecutive runs.
- Streamlit 1.47 API compatibility scan passed.
- The only remaining `width="stretch"` belongs to the original PDF Tagging Components v2 call.
- PDF Tagging top-level import and component implementation remain intact.
- No avatar custom component or cropper dependency was introduced.

## Streamlit execution

- Exact Streamlit 1.47.1 imported successfully.
- The actual application started locally and returned HTTP 200 in three consecutive runs.
- The actual application passed Streamlit AppTest three consecutive runs without application exceptions.
- A Dashboard harness using the final theme passed Streamlit AppTest three consecutive runs:
  - five metric cards rendered
  - Archive Status absent
  - Quick Actions absent
  - System Overview absent
  - Recent Archive Activity present

## Sidebar behavior

A browser DOM/CSS test passed three consecutive runs:

- EDL logo horizontal center difference: 0 px
- Restore button hidden while sidebar is open
- Restore button visible after collapse
- Restore button size: 38 × 38 px
- Main content width increased after collapse
- Sidebar restored successfully

## Helper checks

- Avatar auto-fit JPEG generation passed landscape, portrait, and square image tests.
- Final clean ZIP extraction, compilation, static validation, and import checks were repeated before release.

## Environment note

The local execution environment emitted an unrelated `artifact_tool` spreadsheet warmup message before Python startup. It did not originate from IARS, and the Streamlit app still returned HTTP 200.
