# Test Results — V4.4.72

## Actual uploaded report: 2026IAD095

Source issue titles:

- `NO CASH COLLECTIONS DURING AUDIT`
- `STOCK OVERAGE: P1,500`

Expected and verified output:

- output rows: 1
- Type: Operations Audit
- ignored issue absent: Yes
- Issue: `STOCK OVERAGE: P1,500`
- Findings: `Stock Overage (below P3,000.00)`
- Score: `-2`
- Audited By1: `Fritz Paul Llanes`
- User: `Fritz`
- Scope Date: `March 06,`

## Regression checks

- Actual 2026IAD095 extraction: passed 3 consecutive runs
- Actual 2026IAD094 combined no-variance extraction: passed 3 consecutive runs
- `P1,500`, `P 1,500`, `₱1,500`, and `PHP 1,500` amount parsing: passed
- `P3,000` threshold boundary: passed
- Python compilation: passed 3 consecutive runs
- Clean ZIP extraction and validation: passed 3 consecutive runs
- No `__pycache__` or `.pyc` files included
