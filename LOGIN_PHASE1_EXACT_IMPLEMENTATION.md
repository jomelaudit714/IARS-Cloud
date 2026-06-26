# IARS Login Phase 1 — Exact Component Implementation

This build replaces the native Streamlit sign-in layout with a Streamlit Custom Component v2.

The component controls the full viewport, the approved left audit artwork, the right sign-in card, field positions, button sizes, spacing, responsive behavior, and navigation triggers.

## Files added or changed

- `iars_login_component.py` — exact login component HTML/CSS/JS and Streamlit host styling
- `iars_auth.py` — connects the custom login component to the existing IARS authentication logic
- `assets/login_left_panel.png` — approved left-side audit artwork
- `iars_theme.py` — login fallback and responsive style corrections

## Verification performed

- All Python files compile successfully.
- Streamlit 1.58 starts successfully with the custom component.
- The component uses the same HTML/CSS represented by `docs/LOGIN_PHASE1_IMPLEMENTED_PREVIEW.png`.
