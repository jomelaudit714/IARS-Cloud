# IARS V4.5.15 — Invoice Blister-to-Box Conversion

## Added
- Invoice rows with source UOM `blister` or `blisters` are automatically converted to `box`.
- The corresponding source quantity from column F is divided by `10`.
- The rule is case-insensitive and accepts singular or plural UOM values.
- Negative quantities retain their sign after conversion.

## Examples
- `-20 blisters` becomes `-2 box`.
- `15 Blister` becomes `1.5 box`.

## Retained
- Each Invoice document date still comes from column C of its own `INV` row.
- Product is from column E, quantity from F, UOM from G, and Invoice number from J.
- Apostrophes are removed from product names.
- INV row order is retained.
- Warehouse and LOGP conversion modules remain unchanged.
- The approved `assets/invoice_conversion_template.xlsx` is retained and remains the output template.
