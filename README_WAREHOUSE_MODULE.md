# IARS V4.5.11 — Warehouse Excel Conversion Module

## Sidebar structure

- Excel Conversion
  - Warehouse — active module
  - Sales Personnel
    - LOGP — placeholder for next project
    - Invoice — placeholder for next project

## Warehouse conversion

The module accepts a SAP Warehouse `.xlsx` file and creates the approved `For Uploading` workbook.

- Starts capturing at Item No. `A01AMB01`
- Captures Item Description, Inventory UoM and In Stock
- Removes straight and curly apostrophes from product names
- Generates login_date and sap_date using Philippine date
- Generates sap_no, locations, stock_status and remarks from the filename
- Uses `Balance` as the default task
- Leaves `id` and `count_qty` blank
- Uses the signed-in user's full name as `auditor_name`
- Produces the approved 13-column Excel template

LOGP and Invoice are intentionally shown as disabled placeholders because their separate conversion rules are the next project.
