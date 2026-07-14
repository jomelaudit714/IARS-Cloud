# Test Results – V4.4.55

## Static/code tests
- Version is 4.4.55.
- Built from user-confirmed V4.4.51 base.
- Camera popover is rendered after profile popover.
- Edit Profile invisible trigger width reduced to avoid camera overlap.
- Change Avatar dialog compact CSS present.
- Forgot Password is not a `st.form_submit_button`.
- Sign In remains the only submit button in sign-in form.
- PDF Tagging top-level import remains original.
- PDF Tagging Components v2 remains present in `iars_pdf_editor.py`.
- Avatar Components v2 is absent from `iars_auth.py`.
- No `components.v1`.
- No `components.html`.
- No `st.components.v1.html`.
- No `components.declare_component`.
- No `streamlit-cropper`.
- No `st_cropper()`.

## Functional tests
- Python compile passed.
- Auto-fit avatar crop helper tested using multiple image aspect ratios.
- Local Streamlit startup returned HTTP 200 in available environment.
- Clean ZIP extract checked.
