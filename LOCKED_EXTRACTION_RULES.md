# Locked IARS Extraction Rules — V4.5.39

These rules are regression-protected and must not be changed by unrelated releases.

1. **Policy citation precedence for completeness/best-practice issues**
   - When the recommendation or narrative cites a process, policy, procedure, guideline, memorandum, circular, SOP, manual, protocol, or written rule, classify as:
     `Nonconformity With The Written Policies, Guidelines, Process And Procedures`
   - This rule is evaluated before the generic BEST-PRACT fallback.

2. **Full semantic text before display shortening**
   - Classification, reaction, and frequency evaluate the full recommendation text.
   - Recommendation output shortening happens only after rule evaluation.

3. **Recommendation continuity and punctuation**
   - Introductory phrases such as `Again, we recommend...` remain part of the same recommendation.
   - Do not convert the comma after `Again,` into a period.
   - Do not place `Again.` alone in Recommendation1.
   - Recommendation2 is used only for a genuinely separate recommendation, not a continuation of the same thought.

4. **150-character recommendation output**
   - Recommendation1 and Recommendation2 are each limited to 150 characters.
   - If the complete recommendation fits, preserve it verbatim, including punctuation.
   - If it exceeds 150 characters, shorten safely without changing the required action or meaning.

5. **Regression process**
   - Use the latest complete deployed repository ZIP as the only release baseline.
   - Run the locked extraction tests and the actual PDF golden test before packaging.
   - Do not duplicate classification or recommendation rules in another function or release patch.
