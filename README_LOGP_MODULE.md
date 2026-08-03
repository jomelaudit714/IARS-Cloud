# Sales Personnel LOGP Conversion Module

## Sidebar

- Excel Conversion
  - Warehouse
  - Sales Personnel
    - LOGP — active
    - Invoice — next project

## Required source headers

- Item No.
- Item Description
- Quantity
- UoM Name
- Warehouse/ASR

The source header location is detected by name. The converter intentionally uses the first `Quantity` column because the SAP sample contains another Quantity field later in the sheet.

## Filename example

`LOGP 61005123 DAVIDO GOOD - 06-22-2026.xlsx`

Generated metadata:

- `logp_no`: `61005123`
- `docu_date`: `2026-06-22`
- `docu_name`: `LOGP`
- `remarks`: `Good`

## Employee mapping

`Warehouse/ASR` values such as `DAVIDO, REY VAN` are matched against the IARS Employees Master Data and converted to the official full name, such as `Rey Van Laurente Davido`.
