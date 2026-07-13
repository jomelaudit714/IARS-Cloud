# Test Results – V4.4.40

## Passed
- Static scan: no `components.v1`.
- Static scan: no `components.html`.
- Static scan: no `st.components.v1.html`.
- Static scan: no `components.declare_component`.
- Static scan: no `streamlit-cropper`.
- Python compile passed.
- `iars_auth` import passed.
- `iars_theme` import passed.
- Avatar PIL crop helper passed.
- Local Streamlit startup returned HTTP 200.
- Startup log scan passed for prior v1 HTML and segmentation fault strings.

## Change
- Disabled old transition/loading guard because it used v1 HTML and appeared in crash logs.
