# IARS V4.4.51 – Simple Auto-Fit Avatar

## Base
- Built from the user-uploaded V4.4.43 ZIP.

## PDF Tagging
- PDF Tagging remains in its original state.
- `app.py` keeps the original top-level import of `pdf_textbox_editor`.
- `iars_pdf_editor.py` remains intact.
- PDF Tagging is not lazy-loaded, disabled, or replaced.

## Avatar
- Replaced complex avatar editor with simple upload flow.
- Upload JPG/JPEG/PNG.
- System automatically center-crops and fits the image into the circular avatar.
- Shows circular preview before saving.
- Save Avatar / Cancel / Remove Avatar only.
- No drag, no resize, no sliders, no cropper, no custom avatar component.

## Dialog fix
- See Avatar and Change Avatar dialogs are forced to the true screen center.
- Closing/canceling/saving/removing clears dialog and upload state.
- Sidebar/module navigation clears avatar dialog state to prevent stale popups from appearing later.
