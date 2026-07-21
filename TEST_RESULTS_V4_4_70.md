# Test Results — V4.4.70

## Operations Audit rule tests

- Cash Count and Stock Count subject + approved position → Operations Audit: passed
- Location subject such as Davao Oriental 1 + approved position → Operations Audit: passed
- Location/cash-stock subject without approved position → Financial: passed
- Exact `No Cash Collections during Audit` row ignored while next issue is retained: passed
- Stock Overage below P3,000: passed
- Stock Overage at/above P3,000: passed
- Stock Shortage below P3,000: passed
- Stock Shortage at/above P3,000: passed
- Cash and stock no-variance issues combined into one row: passed
- Combined row category `No Findings`: passed
- `No Collections Shortage or Overage` category `No Findings`: passed
- `January 1 to June 30, 2026` → `January 1 to June 30,`: passed
- Standalone `Audited by` name mapped to By01: passed
- Operations Audit Accounts Confirmation issue-only filter retained: passed
- External stock category labels with `P3,000.00`: passed

## Integrity tests

- `app.py` compilation: passed
- `iars_parser.py` compilation: passed
- clean ZIP extraction and repeated compilation: passed 3 consecutive runs
- no `__pycache__` or `.pyc` files included
