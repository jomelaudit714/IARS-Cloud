# Changelog — V4.4.72

## Operations Audit stock-overage extraction fix

The PDF page can be extracted by pdfplumber as one table containing multiple
issues. V4.4.71 skipped the whole table when it found the ignored issue title
`NO CASH COLLECTIONS DURING AUDIT`, which also removed the valid next issue
`STOCK OVERAGE: P1,500`.

### Corrections

- Removed whole-table skipping for ignored Operations Audit issue titles.
- Ignored titles are now filtered per extracted issue row in `build_records()`.
- A valid issue appearing after an ignored issue in the same PDF table is retained.
- Monetary parsing now recognizes currency-marked whole amounts such as:
  - `P1,500`
  - `P 1,500`
  - `₱1,500`
  - `PHP 1,500`
- `STOCK OVERAGE: P1,500` is classified as
  `Stock Overage (below P3,000.00)` with score `-2`.
- Updated Master Data includes Fritz Paul Llanes as an active Internal Auditor.

### Unchanged

- `NO CASH COLLECTIONS DURING AUDIT` remains ignored for Operations Audit.
- Accounts Confirmation remains excluded only at the individual issue-title level.
- Combined cash-and-stock no-variance reports still produce one No Findings row.
- Financial Audit parsing is unchanged.
