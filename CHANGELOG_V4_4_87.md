# Changelog — V4.4.87

## Receiver-signature classification

- Added the exact narrative scenario `no affixed signature of the recipient`.
- `INCOMPLETE DETAILS IN PCV` is classified as
  `Omission & Alteration Of Details in Documents` when its narrative states
  that the recipient/receiver signature was not affixed.
- PCV and PCR abbreviations are treated as cash/fund receiving-document context
  even when the words `cash` or `fund` do not appear elsewhere in the issue.
- This receiver-signature rule retains priority over a recommendation that also
  cites a memorandum, circular, policy, guideline, process, or procedure.

## PDF Tagging carry-forward rule

- Auditee, Auditor, and Task ID tags continue through every succeeding issue and
  PDF page until a newer tag of the same type appears.
- A new Auditee tag changes only Auditee; the existing Auditor and Task ID remain.
- A new Auditor tag changes only Auditor; the existing Auditee and Task ID remain.
- A new Task ID changes only Task ID; the existing Auditee and Auditor remain.
- Frequency Rate and Reaction remain issue-specific and are not carried forward.
- For Operations Audit, Prepared/Audited by remains the default By01, but an
  explicit Auditor tag now has priority and carries forward until replaced.
- The full-document PDF Tagging popup now displays this rule to users.
