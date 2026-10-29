# KineticFittingPot v1.23 — About section update

Based strictly on confirmed v1.22 pre-deployment source archive (23 October 2026).

## Changes
- Clarified public versus local availability and computational safeguards.
- Added developer attribution, project website and contact/feedback guidance.
- Reused `PUBLIC_CONTACT_EMAIL` from `utils.deployment` (currently mark29464@gmail.com).
- Strengthened educational/research-use explanation and removed obsolete future-deployment/version wording.
- No fitting, diagnostics, simulation, numerical, workbook or navigation changes.

## Validation
- Python source syntax compilation and ZIP integrity checked in the build environment.
- All original v1.22 source files compared by SHA-256; the only changed existing file is `modules/about.py`.
- Full Windows regression suite and browser UI checks should be rerun by the user prior to release.

## Status
Candidate v1.23 final user review build; not yet deployment-approved.
