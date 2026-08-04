# Sales Personnel Invoice Conversion

## Required filename format
The filename must begin with `Invoice`, contain an employee name or surname, and contain a recognized remarks value.

Examples:
- `Invoice Davido Good.xlsx`
- `Invoice Rey Van Davido Sotex.xlsx`
- `Invoice Davido Sold Out.xlsx`
- `Invoice Davido Regular.xlsx` (`Regular` is converted to `Good`)

## Source mapping
| Source | Output |
|---|---|
| Column C on each `INV` row | `docu_date` |
| Column E on each `INV` row | `prod_name` |
| Column F on each `INV` row | `inv_qty` |
| Column G on each `INV` row | `prod_uom` |
| Column J on each `INV` row | `inv_no` |
| Column B beside `LOGP` in column A | `logp_no` |

Only rows marked `INV` in source column A are converted.
