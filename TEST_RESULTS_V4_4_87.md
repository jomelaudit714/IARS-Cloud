# Test Results — V4.4.87

## Classification tests

- `INCOMPLETE DETAILS IN PCV` + `no affixed signature of the recipient`:
  `Omission & Alteration Of Details in Documents` — passed.
- `recipient signature was not affixed` in a PCV narrative — passed.
- Receiver-signature omission plus Circular recommendation: omission
  classification retained as the higher-priority rule — passed.
- Incomplete PCV details without signature omission but with Circular
  recommendation: written-policy nonconformity — passed.

## PDF Tagging carry-forward tests

- Auditee, Auditor, and Task ID applied to the first issue and continued across
  the next PDF page — passed.
- A later Auditee tag replaced only Auditee — passed.
- A later Auditor and Task ID tag replaced those fields while retaining the
  current Auditee — passed.
- Operations Audit explicit Auditor tag overrode Prepared/Audited by — passed.
- Operations Audit without an Auditor tag retained Prepared/Audited by — passed.

## Package checks

- Python compilation: passed 3 consecutive runs.
- Version label and Settings version: 4.4.87.
- No cache or `.pyc` files included.
