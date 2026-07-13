# Test Results – V4.4.37

## Passed
- Clean ZIP extract test.
- Static scan: no `streamlit-cropper`.
- Static scan: no `st_cropper()`.
- Static scan: no `components.declare_component()`.
- Static scan: no `st.components.v1.html`.
- Static scan: no local component folder dependency.
- Python compile passed.
- `iars_auth` import passed.
- PIL avatar crop helper passed.
- Local Streamlit startup returned HTTP 200.
- Startup logs checked for prior errors:
  - no `No such component directory`
  - no `Segmentation fault`
  - no `NameError`
  - no `st.components.v1.html` warning caused by avatar editor
