# KineticFittingPot v1.13 — Case Studies homepage section

Based on the locally tested v1.12 Advanced Diagnostics table-fix build.

## Change
- New **Case Studies** section added to the home page between **Further Analysis** and **Learning & Reference**.
- The existing **Kinetic Fitting Case Study — Biodiesel** card moved out of Learning & Reference into Case Studies.
- Supporting copy updated to distinguish worked applications from fundamentals.
- Existing homepage cards, routes, biodiesel workspace, inputs, fitting engines, data and workbook templates preserved.

## Verification
- Python source compiles.
- Biodiesel is present once in home.py, in CASE_STUDIES, and retains its page registration in app.py.
- Compared to v1.12, only `modules/home.py`, `BUILD_INFO.txt` and this notes file are changed/added.
- Full local interactive acceptance test remains for the user.

## Local installation
Replace your local KineticFittingPot application files with this package (retain your local `.venv` and personal files). Start as usual and verify homepage section order and that the Biodiesel card opens the existing case-study page.
