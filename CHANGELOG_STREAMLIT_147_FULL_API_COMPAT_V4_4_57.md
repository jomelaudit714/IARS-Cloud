# IARS V4.4.57 – Full Streamlit 1.47 API Compatibility

## Base lineage
- User-confirmed V4.4.51 remains the base.
- V4.4.55 camera, avatar-dialog, and login Enter-key fixes remain.
- V4.4.56 stable Cloud dependency pins remain.

## Root cause fixed
V4.4.56 pinned Streamlit to 1.47.1 but still contained newer Streamlit API syntax:
- `st.button(..., width="stretch")`
- `st.form_submit_button(..., width="stretch")`
- `st.download_button(..., width="stretch")`
- `st.dataframe(..., width="stretch")`
- `st.data_editor(..., width="stretch")`
- `st.popover(..., key=..., width="content", on_change="ignore")`

## Changes
- Replaced built-in widget/data `width="stretch"` with `use_container_width=True`.
- Wrapped each popover in `st.container(key=...)` to preserve CSS targeting.
- Changed popovers to Streamlit 1.47-supported arguments only:
  - `label`
  - `help`
  - `use_container_width`
- PDF Tagging Components v2 width handling remains untouched.

## Retained
- Camera icon opens See Avatar / Change Avatar.
- Change Avatar popup fits vertically.
- Enter submits Sign In instead of Forgot Password.
- PDF Tagging remains original and untouched.
