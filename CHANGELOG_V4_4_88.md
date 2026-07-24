# Changelog — V4.4.88

## PDF Tagging auditor/task assignment correction

PDF text extraction does not always follow the visual order of the page. In the
reference report, `AUDITOR: CRIS` is visually inside Issue 4, but the extracted
plain text emits the tag before the Issue 4 title. The prior carry-forward logic
therefore changed Issue 3 to Cris too early.

V4.4.88 now reads the actual PDF page coordinates of these persistent tags:

- Auditee
- Auditor
- Task ID

Each tag is attached to the issue row it visually occupies. It then carries
forward only from that issue until a newer tag of the same field appears.
Coordinate-based tags are authoritative over unreliable plain-text ordering.

For `tagged_2026IAD269_Eldia_Marvihills.pdf` the result is now:

- Issues 1, 2 and 3: Patricia / Task ID 001
- Issue 4: Cris / Task ID 002

## Sticky dialog close control

The title bar and X close control now remain visible while users scroll inside
long dialogs. This applies globally to Streamlit dialogs, including:

- PDF Tagging
- Policies & Memoranda previews/folders
- Shared PDF Archive previews
- Weekly Itinerary previews
- other existing dialog-based modules

## Unchanged

- Existing classification and suppression rules
- Generate Extraction layout and archive behavior
- PDF Tagging carry-forward semantics
- Dashboard, sidebar, authentication and document-library functions
