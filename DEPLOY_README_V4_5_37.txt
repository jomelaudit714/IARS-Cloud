IARS V4.5.37 — PDF Tagging No-Rerun Boundary Save

PDF Tagging changes:
- Typing and pauses never save.
- Only three boundaries schedule a save: click outside the active textbox,
  switch to another textbox, or leave/close the tagging editor.
- Every boundary waits 1.2 seconds.
- Ordinary boundary saves write only to the browser-local PDF workspace.
  They do not call Streamlit, do not rerun the app, do not jump the PDF to
  the top, and do not close the dialog.
- The latest local tags are synchronized to Python only when Generate Tagged
  PDF is explicitly clicked. Generation then continues automatically.

Deployment:
1. Extract this ZIP.
2. Upload all contents directly to the GitHub repository root.
3. Replace existing files.
4. Reboot Streamlit and confirm v4.5.37.

No Supabase migration is required.
