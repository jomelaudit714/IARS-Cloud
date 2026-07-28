# Test Results — IARS V4.5.00

- `app.py` Python compilation: PASS
- `iars_auth.py` Python compilation: PASS
- AST parsing for both files: PASS
- Navigation callback and unique transition-token validation: PASS
- Login transition-state validation: PASS
- Logout callback/query/state validation: PASS
- Transition markup detachment validation: PASS
- Common authenticated-header spacing selector validation: PASS
- Delayed loader selector and timing validation: PASS
- Version-label and versioned-key validation: PASS
- Headless Chromium CSS simulation: PASS
  - transition wrapper did not occupy the normal vertical layout
  - loader card opacity remained `0` before the delay
  - loader card became visible after the delay
  - transition mask became hidden after the ready marker

The supplied package contains only the two deployment files rather than the complete IARS repository, so a full Supabase-connected Streamlit Cloud run was not possible in this environment. The Python files and the transition/layout behavior were tested locally through compilation, AST checks, static assertions, and a browser CSS simulation.
