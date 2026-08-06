# Locked IARS Extraction Rules — V4.5.40

These rules are regression-protected and must not be changed by unrelated releases.

1. **Actual governing-document citation only**
   - Classify as `Nonconformity With The Written Policies, Guidelines, Process And Procedures` only when the recommendation or narrative genuinely cites governing guidance.
   - Complete-word/context matching is required.
   - `manual paper records` is an ordinary description and is not a citation to a manual.
   - `process a replenishment` uses process as a verb and is not a citation to a process.
   - Genuine examples include `Policies and Procedures`, `operations manual`, `follow the approved process`, `guideline`, `memorandum`, `circular`, `SOP`, and written rules.

2. **BEST-PRACT fallback remains protected**
   - No daily monitoring, late PCV preparation, incomplete details, documentation improvements, and similar control improvements remain `Ignore or Disregard Office/Operation Best Practices` when no governing document is genuinely cited.

3. **Full semantic text before display shortening**
   - Classification, reaction, and frequency evaluate the full recommendation text.
   - Recommendation output shortening happens only after rule evaluation.

4. **Recommendation continuity and punctuation**
   - Introductory phrases such as `Again, we recommend...` remain part of the same recommendation.
   - Recommendation2 is used only for a genuinely separate recommendation.

5. **150-character recommendation output**
   - If the complete recommendation fits within 150 characters, preserve it verbatim.
   - If it exceeds 150 characters, shorten safely without changing the required action or meaning.

6. **Regression process**
   - Use the latest complete deployed ZIP as the only release baseline.
   - Run locked tests and actual-PDF golden tests before packaging.
   - Protected modules and dependencies must remain hash-identical.
