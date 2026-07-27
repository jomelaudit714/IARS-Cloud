# IARS V4.4.92

## PDF Tagging text commit behavior

- Removed idle synchronization while the user is continuously typing.
- Active textbox text is committed within one second only after:
  - clicking outside the active textbox; or
  - switching to another textbox.
- Active textbox text is flushed immediately when:
  - leaving the PDF editor;
  - hiding/unloading the editor; or
  - closing/unmounting the PDF Tagging popup.
- Browser-local backup still updates while typing to reduce the risk of lost characters.
- Removed the separate context-menu/right-click commit path. A right click is treated only by the normal outside-pointer behavior.

## Streamlit Components v2 crash fix

- Normalized PDF editor file IDs and component keys so they cannot contain the reserved `__` delimiter.
- Bumped the PDF editor component registration to `iars_pdf_textbox_editor_v32`.
- Preserved the existing local-storage key version so previously tagged boxes remain recoverable.

## Version

- Updated the application version label to 4.4.92.
