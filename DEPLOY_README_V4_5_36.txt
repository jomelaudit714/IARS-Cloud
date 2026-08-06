IARS V4.5.36 — Stable PDF Tagging Boundary Save

Changes:
- Saving triggers only on click outside the active textbox box, switch to another textbox, or leave/close the PDF Tagging editor.
- Every valid save waits 1.2 seconds.
- Typing, typing pauses, window blur, visibility changes, and component cleanup do not trigger saves.
- Streamlit save reruns restore the exact dialog/PDF scroll position and active caret.
- All existing IARS modules and assets are retained.

Deployment:
1. Extract the ZIP.
2. Upload the extracted contents directly to the GitHub repository root.
3. Replace existing files.
4. Reboot Streamlit and confirm v4.5.36.
5. No Supabase migration is required.
