# Kinetic Fitting Case Study — Biodiesel

This public KineticFittingPot case-study page demonstrates a completed local kinetic fit **and its post-fit diagnostics** without running the computationally expensive optimiser, Jacobian calculations or profile re-optimisation on the public server.

Bundled case-study records:

- `data/case_studies/KineticFittingPot_kinetic_fit_results_Biodiesel.xlsx`
- `data/case_studies/KineticFittingPot_kinetic_fit_results_Biodiesel_model_diagnostics.xlsx`

The case uses datasets A/B/C at 338 K and 7.5 wt% catalyst with methanol:oil molar ratios 18:1, 24:1 and 30:1. KineticFittingPot fits one six-parameter reversible mass-action model simultaneously across all three experiments. The model is deliberately simpler than the source paper's LHHW model and the six fitted constants are apparent kinetic parameters for this fixed temperature/catalyst domain.

## Fitting stage

The first part of the page exposes:

- the three-step reversible transesterification network;
- Excel-defined rate expressions and dataset-specific initial conditions;
- measured versus unmeasured model states;
- initial-methanol reconstruction and the normalised constant-volume convention;
- the six shared fitted parameters and their finite bounds;
- the saved fit summary (120 observations, species-scaled residuals, 20 multistarts);
- continuous forward ODE trajectories reconstructed with the saved best-fit parameter vector;
- measured observations overlaid on those trajectories;
- multistart robustness showing widely dispersed starting values but essentially identical final solutions.

## Diagnostic stage

The second part reads the saved v1.37 completed diagnostics workbook and presents four deliberately selective diagnostic blocks.

### 1. Stoichiometric consistency

For the closed six-species reaction network KineticFittingPot finds three independent stoichiometric invariants. Only one is fully observed from the measured TG, DG, MG and ME concentrations:

`3TG + 2DG + MG + ME = constant`

The public case study plots the measured balance deviation versus time for datasets A/B/C with the saved ±2 sigma propagated measurement-uncertainty bars.

Under the saved illustrative uncertainty model (3% relative one-sigma plus 0.002 kmol m^-3 absolute floor):

- A has no complete time point outside ±2 sigma;
- B has one;
- C has two.

This is used as a chemistry-based data-quality diagnostic and does not depend on the fitted kinetic constants.

### 2. Stoichiometric data reconciliation

KineticFittingPot calculates the minimum uncertainty-weighted corrections required to restore the measured invariant. The case study presents species-level RMS and maximum correction/sigma values.

The saved biodiesel result is strongly asymmetric:

- TG: RMS correction about 0.94 sigma; one of 30 observations exceeds 2 sigma;
- DG: RMS correction about 0.44 sigma; none exceed 2 sigma;
- MG: RMS correction about 0.22 sigma; none exceed 2 sigma;
- ME: RMS correction about 2.00 sigma; 12 of 30 observations exceed 2 sigma and 5 exceed 3 sigma; maximum about 4.70 sigma.

The interpretation is deliberately cautious. This does not prove that ME alone is wrong because the reconciliation allocation depends on the assumed measurement uncertainties. It does identify the ME measurement method, calibration and uncertainty as the first experimental issue to investigate.

The page also shows a compact residual table to distinguish stoichiometric inconsistency from kinetic fit quality. ME has the largest absolute RMSE because of its larger concentration scale, but its fit-scaled RMSE is small. The ME concern therefore arises independently from the stoichiometric balance rather than simply from a poor fitted ME trajectory.

### 3. Local parameter identifiability

The saved scaled local Jacobian has:

- numerical rank 6/6;
- condition number about 8.53;
- approximate local relative standard errors from about 5.8% to 24.6%;
- strongest forward/reverse correlations of about 0.84 for k2f/k2r and 0.81 for k3f/k3r.

The parameter-correlation heat map is shown publicly. k1r has the largest approximate local relative standard error (about 24.6%) and the weakest singular-vector direction is dominated by k1r. The conclusion is that the six-parameter solution is locally identifiable, but k1r is less precisely determined than the other fitted constants.

### 4. Profile-objective and zero-rate tests

The saved profiles constrain k1r, k2r and k3r over a multiplicative range while re-optimising all remaining fitted parameters. The saved profile minima occur at the fitted solution and no improved solution was found elsewhere in the explored grids.

Explicit zero-boundary tests give approximate objective-SSE increases of:

- k1r = 0: +23%;
- k2r = 0: +159%;
- k3r = 0: +178%.

The case-study interpretation is that reversibility is strongly supported for reactions 2 and 3. Reverse reaction 1 is less tightly constrained, consistent with the local Jacobian diagnostics, but eliminating k1r still gives a material deterioration in fit.

No formal statistical-significance language is used because experimentally established observation-error distributions are not available for this case.

## Case-study conclusion

The public conclusion is intentionally evidence-based rather than absolute:

- the simple reversible mass-action model is supported by the available data as a useful kinetic representation over the conditions studied;
- one six-parameter vector describes all three methanol:oil experiments;
- the local parameter Jacobian has full rank;
- profile minima agree with the fitted solution;
- removing reverse terms worsens the best achievable fit, particularly for reactions 2 and 3;
- the independent stoichiometric balance reveals measurement inconsistencies, with the saved reconciliation strongly flagging ME under the assumed uncertainty model.

The case therefore demonstrates the complete KineticFittingPot workflow:

`Excel-defined model -> multi-experiment fit -> challenge the data -> challenge the parameters -> challenge the model`

Detailed pointwise residuals, reconciled observations, Jacobians, covariance/correlation matrices and full profile re-optimised parameter vectors remain in the downloadable completed diagnostics workbook rather than cluttering the public teaching page.
