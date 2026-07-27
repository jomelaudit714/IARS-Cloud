# IARS V4.4.93

## Sales Count and Change Fund grouping
- Treats Sales Count, Daily Sales Count, Daily Sales Count and Collection, and a separate Change Fund Count as one audit task.
- Uses one Task ID for the related Sales Count and Change Fund rows.
- When one section has an actual finding and the other is No Findings/Immaterial Findings, only the actual finding is exported.
- When both sections have actual findings, both are exported under the same Task ID.
- When both sections have no actual finding, only one consolidated No Findings row is exported.

## Sales Count shortage and overage classification
Actual shortage/overage in a Sales Count task, including its separate Change Fund Count, never uses Immaterial Findings. The extracted amount selects:
- Cash/Fund/Collection Overage (P1,000.00 and above)
- Cash/Fund/Collection Overage (below P1,000.00)
- Cash/Fund/Collection Shortage (P3,000.00 and above)
- Cash/Fund/Collection Shortage (below P3,000.00)

No-variance wording remains No Findings.

## Multiple issues under one table number
- Captures multiple distinct issue-title and narrative blocks inside one numbered table row.
- Keeps valid actual findings as separate output records.
- No Findings and Immaterial Findings blocks are suppressed when another actual finding exists under the same task.
- Carries the same Auditee, Auditor and Task ID unless a later tag changes them.
