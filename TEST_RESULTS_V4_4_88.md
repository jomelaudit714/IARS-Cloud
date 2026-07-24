# Test Results — V4.4.88

## Actual tagged report

Reference: `tagged_2026IAD269_Eldia_Marvihills.pdf`

Expected and verified:

- WITHOUT STAMPED PAID — Patricia Anne S. Del Rosario — Task ID 001
- REIMBURSEMENT EXCEEDING P1,000.00 — Patricia Anne S. Del Rosario — Task ID 001
- NO CASH SHORTAGE/OVERAGE — Cris Canonoy — Task ID 002

The suppressed minimal-overage issue also retains Patricia / Task ID 001 before
suppression, proving carry-forward starts at the visually tagged first issue.

## Dialog behavior

A browser harness scrolled a long dialog by 900 pixels. The close button's
screen Y-position remained unchanged, confirming the sticky title/close rule.

## Repeated checks

- Python compilation: passed 3 consecutive runs
- Actual tagged PDF extraction: passed 3 consecutive runs
- Coordinate tag-to-issue mapping: passed
- Sticky close browser harness: passed
- Clean ZIP extraction and compilation: passed 3 consecutive runs
- No `__pycache__` or `.pyc` files included
