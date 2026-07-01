# IARS v4.4.12 — PDF Tagging caret and autosave timing

- Increased automatic Streamlit synchronization idle time to 1.8 seconds.
- Auto-sync is postponed while a textbox is focused or another editor interaction is active.
- A return click inside an existing textbox now places the caret at the exact clicked character.
- Prevented the browser default pointer behavior from moving the caret to the end of the text.
- Added geometry-based caret placement as a reliable fallback.
- Preserved long-press drag, border drag, blue-handle resize, per-textbox font size, and browser-local autosave.
