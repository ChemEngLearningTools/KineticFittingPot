# KineticFittingPot v1.19 — Independent validation datasets

Local review build based on the accepted v1.18 simulation-plotting release. **Not a new confirmed backup and not approved for deployment.**

## Scope

- `Datasets.Use_for_Fit = Yes` remains the sole source of fitting datasets; their observations alone contribute to the least-squares objective, species scaling and parameter estimates.
- `Use_for_Fit = No` preserves a dataset and its experimental observations as an independent holdout. Its own initial concentrations and volume model are used for a post-fit model prediction.
- Fitting and validation trajectories are labelled separately; validation predictions use dashed lines and measured validation values use open diamonds.
- Fitting residuals remain separate; validation residuals, raw SSE and raw RMSE are calculated only after parameter estimation.
- Downloaded fit-results workbooks include separate `Validation_Predictions`, `Validation_Residuals`, `Validation_Summary` sheets if validation datasets are supplied. The original fitting sheets remain fitting-only.
- Public worker evaluates holdouts within the same killable process and computation budgets. Combined fitting + validation dataset/observation counts respect public limits.
- No model ODE, reaction-rate, optimiser, parameter-fitting objective or simulation plotting computations from v1.18 have been changed.

## Verification

- `tools/test_validation_holdout_v119.py`: PASS; fitting parameters and SSE unchanged after adding an excluded validation dataset, 19 independent observations predicted, separate Excel tables verified.
- Existing kinetic fitting regression: PASS.
- Public worker busy/timeout/recovery: PASS.
- Built-in and general batch, stoichiometry, diagnostics engine, biodiesel case study and initial rate checks: PASS when run individually.
- Full final-readiness suite and full interactive Streamlit/browser verification must be rerun by user, particularly the public holdout fit and its output workbook.

## Local review procedure

1. Keep the confirmed v1.17 backup intact; install v1.19 in the working/test directory.
2. In the fitting Excel workbook, mark one experiment `Use_for_Fit = No` while retaining the corresponding `Experimental_Data` rows. Keep at least one fitted dataset with more fitted observations than fitted parameters.
3. Confirm the preview identifies the held-out dataset; run fit. Check fitted and validation figures, separate residual metrics and `Validation_*` workbook sheets.
4. Check an unchanged all-Yes workbook gives the same estimates as before.
5. Review both default local mode and public-preview fitting. Public budgets apply to fitting and validation together.
