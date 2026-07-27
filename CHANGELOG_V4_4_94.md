# IARS V4.4.94 — Unnumbered Continuation Issue Capture

## Fixed

A distinct finding is no longer lost when it appears in a separate table row without a repeated Issue No., including when the row begins on the next PDF page.

Reference layout handled:

- Issue No. 2: `OTHER ISSUES: INCOMPLETE RECEIPT INFORMATION`
- Next page / blank Issue No.: `OUTDATED DAILY MONITORING`

The parser now creates two separate records in document order while inheriting the same:

- Issue No.
- Task ID
- Auditee
- Auditor
- activity context

The recommendation in the continuation row is assigned to the continuation issue rather than merged into the preceding issue.

## Preserved

- Multiple titles located inside one finding cell remain separately captured.
- No Findings and Immaterial Findings suppression rules remain unchanged.
- Sales Count and Change Fund grouping remains unchanged.
- PDF Tagging carry-forward and V4.4.92 boundary autosave remain unchanged.
- Existing classification and audit rules remain unchanged.
