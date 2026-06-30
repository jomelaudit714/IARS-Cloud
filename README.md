# IARS Login Phase 2 — Smooth Tabs + Approved Interface

This package keeps the current IARS functions and replaces only the login experience.

## Login changes

- Uses the approved EDL Internal Audit split-screen design.
- Uses the approved left visual panel with the original EDL logo.
- Fits the desktop viewport without page scrolling on the Sign In tab.
- Uses native Streamlit forms, so typing does not rerun or erase input.
- Sign In, Sign Up, Verify Account, and Reset Password are persistent tabs.
- Switching tabs happens in the browser and uses a short fade/slide transition.
- Long Sign Up and Reset Password forms scroll inside the right card instead of moving the entire page.
- No custom JavaScript login component is used.

## Deployment

1. Extract the ZIP.
2. Upload the contents directly to the GitHub repository root.
3. Replace the current files and folders.
4. Keep your existing Streamlit Secrets.
5. Commit the changes and reboot Streamlit.
6. Refresh the app with Ctrl + F5 at 100% browser zoom.

No new Supabase SQL migration is required if the current multi-user login tables already exist.
