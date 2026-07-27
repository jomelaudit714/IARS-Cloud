# IARS V4.4.91 — PDF Tagging Autosave

## PDF Tagging improvements

- Text entered in a tag box is backed up locally within about 20 milliseconds.
- After typing stops, the completed tag state is synchronized to Streamlit in about 900 milliseconds.
- Clicking outside the active textbox commits and saves the text immediately.
- Right-clicking outside the active textbox commits and saves the text before the PDF right-click action continues.
- Clicking outside the PDF editor iframe, hiding the page, or closing the popup also flushes the active textbox.
- Input-method composition is protected so partially composed characters are not saved prematurely.
- The component registration was advanced to v31 to prevent the browser from retaining the previous editor script.

## Unchanged

- Tag box creation, dragging, resizing, font sizing, and styling
- Full-document continuous PDF Tagging view
- Auditee, Auditor, and Task ID carry-forward rules
- Generate Extraction and archive logic
- Popup close behavior and all other application modules
