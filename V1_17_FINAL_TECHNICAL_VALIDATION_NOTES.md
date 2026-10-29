# KineticFittingPot v1.17 — Final technical validation (local review)

- Derived from the v1.16 public worker safeguards baseline. **Application source and scientific algorithms are unchanged.**
- New `test_KineticFittingPot_Final_Readiness.bat` runs the consolidated validation and produces Markdown/JSON results in `validation_reports`. Its test suite includes core numerical smoke tests, diagnostics engine, case study, shared worker admission/timeout/recovery, and static deployment checks.
- New `run_KineticFittingPot_Public_Preview.bat` runs Streamlit in forced public mode on Windows for manual interface assessment; use the original `run_KineticFittingPot.bat` for normal local mode. Close one server before launching the other.
- The consolidated script checks route selection in `app.py` statically. **It does not simulate real browser interaction, multiple actual Streamlit sessions, or cloud platform behaviour.**
- Confirm public-mode fitting workbook handling, busy and numerical-stop messages, Basic Diagnostics, Advanced Diagnostics lock; confirm local Advanced Diagnostics works.
- Python dependencies remain pinned as in v1.16. A pinned manifest does not prove that all packages are supported on a specific cloud image; cloud smoke testing remains essential.
- Do not call this a confirmed backup until validation results and user-led final review are accepted. Do not deploy yet.
