# Changelog — V4.4.71

## Operations Audit combined no-variance correction

- Corrected matching for cash no-variance titles such as `NO SHORTAGE/OVERAGE ON CASH COLLECTION COUNT`.
- Corrected matching for stock/inventory no-variance titles such as `NO SHORTAGE/OVERAGE ON STOCK INVENTORY`.
- When both are present in one Operations Audit report, they are consolidated into one output row.
- The consolidated issue is `No Cash Collection Overage/Shortage and No Stock Overage/Shortage`.
- The consolidated category is `No Findings`.
- Actual cash or stock shortages/overages remain separate findings and retain amount-based categorization.
