IARS V4.5.34 — COMPLETE CLEAN DEPLOYMENT

PDF TAGGING SAVE BEHAVIOR RESTORED
- Typing inside an active textbox remains browser-local and does not trigger a Streamlit rerun.
- Saving is triggered only after clicking outside the active textbox, switching to another textbox, leaving the editor, or closing the popup.
- Outside-click and box-switch commits keep the agreed one-second delay.
- Leaving or closing the editor flushes the last change immediately.
- Recovered browser-local changes no longer auto-save when the editor opens.
- Textbox position, size, font, add/delete/duplicate, and clear changes remain pending until an explicit outside boundary or editor close.

DEPLOYMENT
1. Extract this ZIP.
2. Upload the contents directly to the GitHub repository root.
3. Replace existing files.
4. Reboot the Streamlit app.
5. Confirm v4.5.34 in the IARS header.

AUDIT EXTRACTION FREQUENCY
- Explicit Frequency Rate tags still have first priority.
- Otherwise, IARS counts the unique prior IAD reference numbers found in the issue narrative and adds one for the current audit.
- Example: 2026IAD103 + 2026IAD213 = Third Time for the current audit.
- Repeated mentions of the same reference are counted once.
- Supported formats include 2026IAD103, 2026-IAD-103, and 2026/IAD/103.

No Supabase migration is required.
