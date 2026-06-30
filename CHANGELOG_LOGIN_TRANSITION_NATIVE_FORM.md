# Login Transition and Native Form Update

- Preserved the existing EDL logo and login artwork from the supplied June 26 viewport-fit package.
- Removed the interactive custom login component from the active application.
- Replaced username, password, Remember me, and Sign In controls with one native Streamlit form.
- Form values are submitted only when Sign In is clicked, preventing per-keystroke reruns, disappearing text, and CachedForwardMsg errors.
- Changed Sign Up, Verify Account, and Back navigation to callback-based state updates, eliminating the previous second explicit rerun.
- Added a short 0.22-second fade-and-rise animation to the right account panel only.
- Kept the left branded EDL panel fixed and unchanged during account-view transitions.
- Kept Forgot Password in the original Remember-me row using an internal account-view link.
