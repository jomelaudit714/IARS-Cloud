# IARS V4.4.85 Changelog

## Shared PDF Archive

- Fitted every header label inside its corresponding border.
- Adjusted column proportions for Audit Reference, Auditee Name, Uploaded Date,
  Uploaded By, View, and Download.
- Header text may wrap cleanly when required instead of extending beyond a cell.
- Removed `filename` from the Search placeholder. The visible prompt is now:
  `Audit reference, auditee, or uploader`.
- Retained the continuous grid, View button, Download button, full-document
  preview, and hidden internal filename used for download and preview.

## Generate Extraction

- Reworked Clear Records as a normal Streamlit callback.
- Removed the additional explicit rerun that caused a visible double refresh.
- Generated records and their editor state are cleared before Streamlit's normal
  rerun.
- Confirmation is shown as a small toast, avoiding a layout jump.

## Policies & Memoranda

- Fitted all header labels inside their corresponding borders.
- Converted the folder results into a compact continuous grid without detached
  rows or cells.
- Corrected the View button placement. It now renders in the View column instead
  of the Uploaded By column.
- Retained the Download column, title search, full-document preview, folders,
  subject/process categories, and administrator controls.
