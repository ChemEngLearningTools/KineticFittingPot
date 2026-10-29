# Post-fit Model Diagnostics

KineticFittingPot v1.28 extends the post-fit diagnostic workflow described on **Model Diagnostics Fundamentals**. The first operational block remains deliberately **rate-free**: it challenges the experimental data against the assumed stoichiometric structure before interpreting residuals from the fitted kinetic law.

## Completed-fit workbook input

The page starts from the completed KineticFittingPot kinetic-fitting workbook. It reuses the original model, datasets and raw experimental observations retained in that workbook together with the fit-result sheets.

For a closed reaction network with stoichiometric matrix `S`, every left-null-space vector `l` satisfying

`l^T S = 0`

defines a mole invariant

`l^T n = constant`.

The invariant space has dimension

`number of species - rank(S)`.

## Independent invariant basis

Because a null-space basis is not unique, KineticFittingPot converts exact stoichiometric relationships to small integer coefficients and searches for a sparse, same-sign independent basis where possible. The displayed independent basis spans the complete invariant space.

For the biodiesel A/B/C example:

- species: TG, DG, MG, MeOH, ME, Gly;
- rank(S) = 3;
- independent full-model invariants = 3;
- measured species: TG, DG, MG, ME;
- measured-only invariant dimension = 1.

A simple independent full-model basis is:

1. `MeOH + ME = constant`
2. `TG + DG + MG + Gly = constant`
3. `3TG + 2DG + MG + ME = constant`

Only the third relationship is fully observed in the experimental data.

## Simple integer conserved quantities

Independent invariants are not the only chemically readable conserved totals. KineticFittingPot therefore provides a second finite search for **primitive non-negative integer invariants** with coefficients

`0 <= l_i <= Lmax`.

Scaled duplicates are removed by requiring the greatest common divisor of the non-zero coefficients to be one. The default search uses `Lmax = 4`.

For the six-species biodiesel network this default search returns 29 primitive simple conserved quantities. They contain no additional independent information: all lie in the same three-dimensional left-null space. Their value is interpretability and the possibility of identifying a conserved total that uses a convenient subset of measured channels.

The exhaustive search is deliberately disabled when the coefficient box would become combinatorially large.

## Measured-only constraints

A generic full-model null-space basis can hide a useful fully observed balance. KineticFittingPot therefore solves a second left-null-space problem using only the rows of `S` corresponding to experimentally measured species. This identifies every independent invariant that can be evaluated directly from raw measurements without inserting model-predicted unmeasured species.

For the biodiesel data the direct measured relationship remains

`3TG + 2DG + MG + ME = constant`.

## Stoichiometric-consistency monitoring

For a fully observed invariant in a constant-volume closed batch, KineticFittingPot evaluates the raw measured balance at every time where all participating species are available. The earliest complete observation is used as the reference value and the displayed signal is

`epsilon_B(t) = [B(t) - B(t_ref)] / |B(t_ref)|`.

This is a rate-free data-consistency diagnostic. It does not use fitted rate constants or fitted trajectories.

## Measurement-uncertainty propagation

If `Experimental_Data` supplies a positive `Sigma_kmol_m3`, KineticFittingPot uses it for that observation. Otherwise the user supplies a diagnostic uncertainty model

`sigma_i = sqrt[(p |C_i|)^2 + sigma_floor^2]`.

The balance uncertainty for independent measurement errors is

`sigma_B^2 = sum_i (l_i V sigma_i)^2`.

For `t > t_ref`, the uncertainty of the balance difference is propagated as

`sigma_DeltaB = sqrt[sigma_B(t)^2 + sigma_B(t_ref)^2]`.

The plot shows the corresponding ±1 sigma and ±2 sigma envelopes around perfect stoichiometric consistency. These are **measurement-uncertainty bands**, not classical SPC control limits.

The baseline measurement is also used as the normalising scale; denominator uncertainty is not included in this first sensitivity calculation.

## Stoichiometric data reconciliation

For the selected fully observed invariant, KineticFittingPot calculates the minimum uncertainty-weighted correction to the measured concentration vector subject to the balance constraint.

For measured vector `y`, reconciled vector `x`, diagonal covariance `Sigma` and one constraint `l^T x = B0`:

`min (x-y)^T Sigma^-1 (x-y)`

subject to

`l^T x = B0`.

Each constant-volume dataset uses its earliest complete measured balance as the fixed reference `B0` in this calculation.

The diagnostics report:

- raw and reconciled concentration values;
- correction `x* - y`;
- correction relative to assumed/supplied sigma;
- species-level ranking of reconciliation corrections;
- dataset-level weighted correction statistics;
- exact post-reconciliation balance closure.

Raw observations are never overwritten. Reconciled values are diagnostic estimates only. If reconciled data are later used for kinetic fitting, the raw-data and reconciled-data fits should be compared explicitly.

The current closed-form reconciliation assumes independent channel errors and does not impose non-negativity. If the unconstrained solution becomes negative, KineticFittingPot reports the issue rather than clipping values and breaking the equality constraint.

## Deliberate boundary of the rate-free block

Direct raw concentration-balance monitoring and reconciliation are currently restricted to constant-volume closed-batch datasets. Variable-volume/open systems require explicit process-boundary terms.

Dynamic residual diagnostics, local Jacobian/correlation analysis, profiled-objective calculations, explicit zero-rate kinetic-term tests and the completed diagnostics-workbook export are implemented below. The rate-free balance/reconciliation boundary remains unchanged.

## Dynamic residual diagnostics (v1.27)

After the rate-free stoichiometric block, KineticFittingPot now evaluates the residuals from the completed fit.

The sign convention is inherited unchanged from Kinetic Parameter Fitting:

`e = fitted/model - measured`.

Positive residuals mean the fitted model lies above the measured value.

KineticFittingPot reports residual bias, RMSE, MAE and maximum absolute residual by species, by experiment and by experiment/species. Fit-scaled residuals use the same per-species scale as the fitting objective; these are numerical scaling quantities, not statistical standard errors. Where measurement sigma is available (or an explicit diagnostic uncertainty model has been assumed), a separate uncertainty-standardised residual can also be calculated.

For a selected experiment, the page displays residual versus time and residual versus fitted value. For a selected species it adds a residual histogram and Q-Q view. These diagnostics are descriptive: they look for drift, curvature, heteroscedasticity, outliers and other structure that a visually satisfactory fitted trajectory can hide.

Cross-species residual correlation uses only common observation times within the selected experiment. Missing residuals are not interpolated.

A conventional residual ACF is guarded by the actual sampling grid. At least six unique times are required and all time intervals must be within 5% of the median interval. If the grid is irregular, KineticFittingPot withholds the ACF and reports the observed intervals rather than interpolating them. The biodiesel A/B/C time grid is therefore correctly treated as irregular.

The strongest interpretation comes when fitted-model residual structure agrees with an independent rate-free diagnostic. In the biodiesel example, Dataset B ME residuals are predominantly positive while the stoichiometric reconciliation also tends to raise the measured ME values. This is informative evidence of a channel/model inconsistency, but it does not by itself prove that the ME assay is wrong or that the kinetic mechanism is incorrect.

## Local parameter / Jacobian diagnostics (v1.28)

KineticFittingPot now evaluates the local parameter geometry at the fitted optimum. The residual Jacobian is formed numerically using the **same residual weighting used during fitting**:

`J_ij = partial e_i / partial theta_j`.

Each fitted parameter is perturbed and the full dynamic model is re-integrated. Central finite differences are used whenever possible; a one-sided difference is used automatically when the fitted point lies too close to a bound for a symmetric perturbation.

A raw Jacobian condition number depends on parameter units. KineticFittingPot therefore forms a **relative-parameter Jacobian** for singular-value analysis by scaling each Jacobian column by a local parameter scale. For a safely non-zero fitted parameter this is `abs(theta_hat)`; an effectively zero fitted value uses 1% of the finite bound span instead. The displayed singular values and condition number must therefore be interpreted as local geometry under this stated scaling, not as a unit-invariant universal property.

For each parameter the page reports the RMS weighted-residual effect associated with a 1% local parameter change. This is a local sensitivity measure with the other parameters held fixed.

KineticFittingPot also calculates the local least-squares approximation

`Cov(theta_hat) ~= s^2 (J^T J)^+`,

where `s^2 = SSE/(n-p)` when positive residual degrees of freedom are available and `+` denotes the pseudoinverse. This gives approximate local standard errors and a parameter-correlation matrix.

For `species_scaled` fitting these standard errors are **objective-based local approximations**. They should not be interpreted as experimental confidence intervals unless the chosen residual weighting is a defensible measurement-error model. Parameter correlation remains useful for exposing local trade-offs between fitted constants.

The SVD additionally provides the weakest local parameter direction: the right-singular vector associated with the smallest singular value. The overall sign of this vector is arbitrary. It identifies a relative parameter combination to which the residual vector is locally least sensitive, but it does not determine whether that direction remains weak away from the optimum.

KineticFittingPot provides diagnostic flags for numerical rank loss, genuine proximity to a fitted bound, and parameter pairs with `|rho| >= 0.8`. These are prompts for further investigation rather than automatic model-selection rules.

For the biodiesel A/B/C fit the local relative-parameter Jacobian is full rank (6/6) with condition number approximately 8.53. The strongest local parameter correlations are `k2f`–`k2r` (about +0.839) and `k3f`–`k3r` (about +0.815). KineticFittingPot can then continue to nonlinear profiled-objective analysis and explicit `k_r = 0` boundary tests on the same workspace.


## Completed model-diagnostics workbook export (v1.37)

KineticFittingPot now saves the post-fit analysis as a new downloadable Excel workbook. The uploaded completed fitting workbook remains the base record: original model/data sheets and all `Fit_*` sheets are preserved. Existing `Diag_*` sheets are replaced on re-export and a fresh structured diagnostic record is appended.

The export records the settings needed to interpret the calculation, including the selected measured invariant, assumed measurement uncertainty, simple-invariant search limit and — when available — the profile grid/span/re-optimisation settings. A SHA-256 hash of the uploaded completed-fit workbook is also stored as provenance.

The diagnostic workbook includes structured sheets for:

- stoichiometric matrix, independent invariants, measured-only invariants and the finite simple-integer invariant catalogue;
- balance-monitor definition, pointwise balance deviations and dataset summaries;
- reconciled observations plus species- and dataset-level reconciliation summaries;
- residual points and species/dataset/dataset-species summaries, with regular-grid ACF and common-time cross-species residual correlations;
- local parameter diagnostics, singular values, covariance and correlation matrices, weakest local direction, raw/scaled Jacobians and weighted residuals;
- profiled-objective summary and pointwise results, including the complete re-optimised parameter vector at every constrained point;
- explicit zero-rate boundary tests and their re-optimised parameter vectors.

Profile calculations remain deliberately user-triggered because they require repeated ODE integrations and constrained re-optimisation. If the user downloads before running profiles, the workbook records that profile results were not included. KineticFittingPot does not manufacture or silently recompute them during export.
