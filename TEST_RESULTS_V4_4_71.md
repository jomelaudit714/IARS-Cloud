# Test Results — V4.4.71

## Actual uploaded report regression test

Test file: `AUDIT REPORT ASR NELSON CUSTODIO.pdf`

Source issue titles:

- `NO SHORTAGE/OVERAGE ON CASH COLLECTION COUNT`
- `NO SHORTAGE/OVERAGE ON STOCK INVENTORY`

Expected and obtained result:

- Audit type: `Operations Audit`
- Output rows: `1`
- Issue: `No Cash Collection Overage/Shortage and No Stock Overage/Shortage`
- Category: `No Findings`
- Scope Date: `March 7,`

The actual uploaded PDF passed this extraction test three consecutive times.

## Matcher tests

Passed cash-title formats:

- `NO SHORTAGE/OVERAGE ON CASH COLLECTION COUNT`
- `NO CASH COLLECTION SHORTAGE OR OVERAGE`
- `NO OVERAGE OR SHORTAGE IN CASH COLLECTIONS`

Passed stock-title formats:

- `NO SHORTAGE/OVERAGE ON STOCK INVENTORY`
- `NO STOCK SHORTAGE OR OVERAGE`
- `NO OVERAGE OR SHORTAGE IN INVENTORY COUNT`

Actual variance titles such as `STOCK SHORTAGE P 4,000.00` and
`STOCK OVERAGE P 1,500.00` were not treated as no-variance titles.

## Integrity

- Python compilation: 3 consecutive passes
- Only the no-variance title matchers were changed in `iars_parser.py`
- Only the displayed version was changed in `app.py`
- No `__pycache__` or `.pyc` files are included
