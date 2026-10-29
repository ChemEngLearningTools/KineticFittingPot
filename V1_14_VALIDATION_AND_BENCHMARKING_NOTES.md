# v1.14 — Validation and benchmarking

This is **not** a deployment candidate. The application code is unchanged from v1.13.

## Running

After setup, double-click `test_KineticFittingPot_Public_Readiness.bat`. It runs the core regression tests, malformed-workbook checks, public limit checks, a forced budget-stop test, and the bundled catalytic example under public limits. It writes both a Markdown and JSON report to `validation_reports/`.

To add the potentially expensive legacy Advanced Diagnostics test, run `test_KineticFittingPot_Public_Readiness.bat --full` from Command Prompt. Each legacy test runs in a child process with its own timeout. The catalytic benchmark runs in the parent process with cooperative fitting limits; this is **not** a hard timeout.

## Important gaps

The distributed bundle contains a catalytic example and an ordinary simulation template. The original biodiesel fitting example may be elsewhere in the project research data, but this runner **does not claim** a six-parameter biodiesel or full eight-parameter / six-dataset benchmark. Supply a representative validated fitting workbook before choosing final deployment limits. Full Streamlit interaction, Python version compatibility and concurrency tests are also still required.

The script does not edit workbook data, scientific engines, UI modules, or solver settings.

## First run in the build environment

The bundled first-run report records two failures of historical **presentation-text assertions**, not numerical simulation discrepancies: `smoke_test_batch_simulator.py` expects old guided-experiment phrasing, while `smoke_test_reaction_stoichiometry_fundamentals.py` expects the former Home-section structure. Those tests were deliberately left unchanged to show what requires maintenance before a clean full pass can be claimed. Their numerical portions completed before the assertions. The core fitting and public computational-budget tests passed.
