IARS V4.5.35 — Smooth PDF Tagging Boundary Save

Deployment:
1. Extract this ZIP.
2. Upload all files and folders directly to the GitHub repository root.
3. Replace the existing files.
4. Reboot the Streamlit app and confirm v4.5.35.

PDF Tagging behavior:
- Typing, moving, resizing, font-size changes, adding, duplicating and deleting remain browser-local while actively editing.
- Saving is triggered only by clicking outside the active textbox, switching to another textbox, leaving, or closing the editor.
- Outside-click and box-switch saving uses a 1.2-second delay.
- The editor restores the exact dialog and page-canvas scroll positions after Streamlit's component rerun, so tagging continues at the same location.
- Leaving or closing flushes immediately to protect the latest edit.

No Supabase migration is required.
