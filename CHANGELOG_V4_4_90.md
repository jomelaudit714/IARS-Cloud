# Changelog — V4.4.90

## Persistent popup close control

The previous sticky-close CSS did not remain visible on the deployed Streamlit
1.58 modal structure. Streamlit 1.58 uses BaseWeb modals, where the modal
container can scroll independently of the close button's intended sticky
ancestor.

V4.4.90 adds a lightweight parent-document controller that:

- detects the currently open Streamlit dialog;
- creates a fixed circular close control aligned with the popup's upper-right edge;
- keeps the control visible while scrolling anywhere inside a long popup;
- triggers the native Streamlit close action when clicked;
- hides itself automatically when the dialog closes;
- works for PDF Tagging, Policies & Memoranda, Shared PDF Archive, Weekly
  Itinerary, and other Streamlit dialogs.

No extraction, tagging, archive, document-library, authentication, or database
logic was changed.
