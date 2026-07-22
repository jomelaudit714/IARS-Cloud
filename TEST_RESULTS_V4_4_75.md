# Test Results — V4.4.75

## Static and compilation

- Python compilation passed three consecutive runs.
- App version label is `4.4.75`.
- One Dashboard CSS helper and one Weekly Itinerary Dashboard renderer are present.
- No old version label remains in the replacement files.

## Dashboard role behavior

- Ordinary auditor with approved current itinerary: image rendered immediately.
- Ordinary auditor with approved current itinerary: no View/Open button rendered.
- Administrator: pending-approval summary rendered above the personal itinerary.
- Administrator with own approved current itinerary: personal image rendered below the pending summary.
- Administrator personal panel uses `list_user_itineraries`; other auditors' images are not selected.
- Role behavior passed three repeated harness runs.

## Current-week selection

- Current Monday-Friday itinerary is selected during the covered dates.
- The same itinerary remains current on Saturday and Sunday of that calendar week.
- A prior-week approved itinerary is not selected for the next calendar week.
- Newer revisions take priority.

## Visual CSS harness

- EDL logo center aligned with the sidebar center: passed.
- Sidebar top padding reduced to 3 px: passed.
- Dashboard topbar raised with a -25 px top margin: passed.
- Metric-card minimum height is at least 152 px: passed.
- Metric label, value, and note fonts were increased: passed.
- Five equal horizontal metric columns at desktop width: passed.

## Integrity

- No database migration is required.
- No Generate Extraction, PDF Tagging, parser, archive, document library, login, or avatar code is included in this layout patch.
- No `__pycache__` or `.pyc` files are included.
