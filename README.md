# IARS v4.4.1 — Deployment-Fixed Login UI

This is the complete IARS application package with the corrected, tested login interface.

## Login corrections

- Left and right panels are equal height at 1365 × 768.
- Username and password fields have complete borders.
- The password-eye section is inside and aligned with the password field.
- “Remember me” stays on one line.
- The “or” divider does not overlap the account actions.
- Sign Up is exactly the same width and height as Sign In, with a complete 2 px border and approved plus-person icon.
- Verify Your Account is centered, blue, borderless, and uses the approved shield-check icon.
- The authorization notice remains at the bottom of the right panel.
- The native Streamlit sign-in form remains stable while typing.
- The full-screen transition mask remains in place until the authenticated workspace is ready.

## Deployment

1. Extract the ZIP.
2. Upload the **contents** of the extracted folder to the root of the GitHub branch connected to Streamlit.
3. Confirm that `app.py`, `iars_auth.py`, and `iars_theme.py` are directly in the repository root—not inside another folder.
4. Keep your existing Streamlit Secrets. This ZIP includes only `.streamlit/secrets.toml.example`.
5. Commit all replaced files together.
6. In Streamlit, open **Manage app → Reboot app**.
7. Hard refresh the deployed page using `Ctrl + F5`.

Build marker: `4.4.1-deployment-fixed`

See `TEST_RESULTS_V4_4_1.md` and the files in `docs/` for the browser-tested preview and measurements.
