# IARS V4.4.86 Changelog

## Classification rules added

### Missing receiver or recipient signature

A PCV, PCR, petty cash voucher/request, cash voucher, cash receipt or comparable
cash/fund receiving document is classified as:

**Omission & Alteration Of Details in Documents**

when the issue title or narrative states that the Received By portion, receiver
or recipient has no/missing signature. This rule has priority over a policy or
circular reference in the recommendation.

### Written-policy recommendation

A recommendation directing the auditee to review, refer to, follow or comply
with a memorandum, memo, circular, policy, procedure, process, guideline, SOP,
manual, protocol, rule or related written requirement is classified as:

**Nonconformity With The Written Policies, Guidelines, Process And Procedures**

### Cash advance variance rules

For a cash-advance issue:

- No shortage/overage wording -> **No Findings**
- Cash overage -> **No Findings**
- Minimal overage -> **No Findings**
- Minimal cash overage -> **No Findings**
- Minimal cash shortage -> **Immaterial Findings**
- Minimal shortage -> **Immaterial Findings**

The existing row-suppression behavior is retained. If another actual finding
exists under the same Task ID, the No Findings or Immaterial Findings row is not
included in the generated output.

## Unchanged

- Generate Extraction interface and archive workflow
- Operations Audit rules
- PDF Tagging
- Shared PDF Archive
- Policies & Memoranda
- Weekly Itinerary
- Authentication and Dashboard
