# Locked IARS Extraction Rules — V4.5.38

These rules are regression-protected and must not be changed by unrelated releases.

1. **Policy citation precedence for completeness/best-practice issues**
   - When the recommendation or narrative cites a process, policy, procedure, guideline, memorandum, circular, SOP, manual, protocol, or written rule, classify as:
     `Nonconformity With The Written Policies, Guidelines, Process And Procedures`
   - This rule is evaluated before the generic BEST-PRACT fallback.

2. **Full semantic text before display truncation**
   - Classification, reaction, and frequency evaluate the full recommendation text.
   - Recommendation output shortening happens only after rule evaluation.

3. **Recommendation length**
   - Recommendation1 and Recommendation2 are each limited to 150 characters, including the ellipsis when truncation is required.

4. **Regression process**
   - Use the latest complete deployed repository ZIP as the only release baseline.
   - Run `python -m pytest tests/test_locked_extraction_rules.py` and the actual PDF golden test before packaging.
   - Do not duplicate classification logic in another function or release patch.
