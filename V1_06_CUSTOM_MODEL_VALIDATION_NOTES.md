# KineticFittingPot v1.06 — Custom Model Workflow and Validation

Status: local review build (not deployed).

## Changes
- Shared metric-value typography standardised to 1.55 rem, including k1/k2/k3 cards.
- Custom model page places the template download first, with guidance and mathematical model in collapsed help panels.
- Workbook interpreted model and generated equations in collapsed preview.
- Explicit upload validation: workbook structure, then finite initial reaction-rate evaluation before Run is offered.
- More specific user-facing failure messages for rate-domain, invalid-volume, solver and numerical-work-limit failures, with detailed original error available in an expander.
- Original four distributed Excel workbooks' user-facing `ReactionPot` wording updated to `KineticFittingPot`; workbook structure and numerical datasets retained.
- No edits to numerical calculation engines, solver method or public computation limits.

## Validation
- Static parsing for all Python files: PASS.
- General batch smoke test: PASS (constant and composition-dependent volume).
- Fitting engine smoke test: PASS.
- New initial-rate smoke test: PASS.
- Original scientific utility modules other than shared UI: byte-for-byte unchanged.
- Workbooks were edited by importing/exporting in artifact_tool; verify all sheets in Excel on your local machine before deployment.

## Limitations
- Initial-rate evaluation catches numerical errors at t=0, not invalid expressions emerging later.
- Parser does not verify chemical physical plausibility or unit consistency.
- Negative simulated species amounts are warned about; underlying solver is unchanged.
- Public fitting remains disabled pending separate benchmark/resource-limit work.

## Suggested manual tests
1. Load supplied template unchanged; ensure green validation checks and unchanged simulation trajectories.
2. Open Help expanders; verify controls and results appear without scrolling through extensive notes.
3. Try a syntactically valid rate with division by zero at initial conditions, using a copy of the workbook. Expect reaction-specific initial-rate failure and no Run.
4. Introduce missing sheet, unknown parameter, negative initial charge, and invalid initial volume. Expect validation messages.
5. Check all bundled workbooks open in Excel and their saved calculations/data have not changed.
6. Verify long cards and scientific units on different screen widths.
