# IARS V4.4.86 Test Results

## Classification tests

- Missing receiver signature in a PCV involving cash/fund receipt: passed
- Missing receiver signature takes precedence over policy recommendation: passed
- Recommendation citing a memorandum/policy/circular/procedure: passed
- Cash advance cash overage -> No Findings: passed
- Cash advance minimal overage -> No Findings: passed
- Cash advance minimal cash overage in narrative -> No Findings: passed
- Cash advance minimal cash shortage -> Immaterial Findings: passed
- Cash advance no overage/shortage -> No Findings: passed
- Non-cash-advance overage retains normal overage classification: passed

## Existing suppression behavior

- No Findings and Immaterial Findings removed when another actual finding exists
  under the same Task ID: passed
- No Findings/Immaterial Findings retained when no actual finding exists: passed

## Regression tests using actual uploaded reports

- ASR Nelson Custodio combined no-variance output: passed
- TSS Espinase stock overage output and ignored no-cash issue: passed
- ELDIA Marvihills Circular no. 4 and no. 6 recommendations: passed

## Technical validation

- `app.py` and `iars_parser.py` compilation: passed three consecutive runs
- Clean ZIP extraction and compilation: passed three consecutive runs
- No `__pycache__` or `.pyc` files included
