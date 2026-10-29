# Model Diagnostics Fundamentals

KineticFittingPot uses post-fit diagnostics to answer a question that optimisation alone cannot answer:

> Does the fitted model deserve to be believed?

The diagnostic sequence is:

**data consistency → residual behaviour → parameter certainty → model structure**.

## 1. Fitting is not the end of modelling

A successful optimiser only establishes that parameter values have been found that minimise the selected objective. It does not prove that the measurements are internally consistent, residuals behave like experimental error, the fitted parameters are identifiable, every rate term is necessary, or the mechanism is physically correct.

## 2. Rate-free stoichiometric consistency

For a closed batch reactor,

`dn/dt = V S r`

and with `dξ = V r dt`,

`dn = S dξ`.

Any vector `l` satisfying

`l^T S = 0`

defines a stoichiometric invariant:

`l^T n = constant`

or

`l^T Δn = 0`.

This relationship depends on stoichiometry, not the fitted rate law.

### Balance classes

- **Fully observed invariant** — direct rate-free measurement-consistency check.
- **Partially observed invariant** — chemically valid, but an unmeasured species must be estimated first.
- **Elemental / charge balance** — strong structural check where formulae and boundaries are known.
- **Model-predicted total** — useful post-fit diagnostic but not an independent data-quality test.
- **Open-system balance** — must contain flow, sampling, transfer and changing-volume terms.

## 3. Biodiesel worked invariant

For

`TG + MeOH <-> DG + ME`

`DG + MeOH <-> MG + ME`

`MG + MeOH <-> Gly + ME`

the measured TG, DG, MG and ME species satisfy

`3 n_TG + 2 n_DG + n_MG + n_ME = constant`.

For constant volume the same relationship holds in concentrations.

Define

`B(t) = 3 C_TG + 2 C_DG + C_MG + C_ME`

and

`epsilon_B(t) = [B(t)-B(0)]/B(0)`.

This is a fully observed rate-free stoichiometric-consistency diagnostic.

## 4. Stoichiometric-consistency monitoring

A balance residual versus time is useful, but a single evolving kinetic time course is not automatically a classical Phase I/Phase II SPC problem. Points are serially related because the chemical state evolves.

A systematic trend should first trigger checks of units/basis, calibration, detector drift/dilution, sampling loss, evaporation/transfer, phase partitioning, changing volume/flow, unmeasured species, omitted reactions, stoichiometric coefficients, process boundary and only then broader model mismatch.

## 5. Data reconciliation

For measured vector `y`, reconciled vector `x`, exact linear constraint `H x = h`, and measurement covariance `Sigma`, solve

`min (x-y)^T Sigma^-1 (x-y)`

subject to the constraint.

For linear constraints, when `H Sigma H^T` is nonsingular,

`x* = y - Sigma H^T (H Sigma H^T)^-1 (H y - h)`.

The adjustment is

`delta = x* - y`

and a weighted inconsistency statistic is

`J_rec = (x*-y)^T Sigma^-1 (x*-y)`.

Raw data must never be silently replaced by reconciled values. Fitting reconciled data is an explicitly labelled sensitivity analysis.

## 6. Dynamic residuals

For an observation,

`e_i(t_j) = y_i,model(t_j) - y_i,obs(t_j)`.

Useful views include residuals versus time, residuals versus fitted value, grouping by species and dataset, Q-Q/empirical distributions, and cross-species relationships.

If experimental `sigma_i` is known, `z_i=e_i/sigma_i` is an uncertainty-standardised residual. Species-scaled residuals are not formal statistical standardisation.

Conventional ACF should be reserved for sufficiently regular sampling; KineticFittingPot must not silently interpolate irregular observations to fabricate an ACF.

## 7. Local parameter diagnostics

With residual Jacobian

`J_ij = d e_i / d theta_j`,

nearly proportional columns indicate parameter trade-offs. Under local least-squares assumptions,

`Cov(theta_hat) ≈ s^2 (J^T J)^-1`

and parameter correlations follow from the covariance matrix. This is a local approximation and can be misleading near bounds or for strongly nonlinear objectives.

## 8. Profile likelihood

For parameter `theta_j` fixed at a trial value, KineticFittingPot can compute a profiled least-squares objective. Under an appropriate Gaussian error model this corresponds to profile likelihood up to scaling and additive constants:

`Q_p(theta_j*) = min_{theta_-j} Q(theta_j*, theta_-j)`.

A sharp interior profile indicates stronger identification; a flat profile indicates weak identification; a one-sided/bound-limited profile suggests that only a limit may be supported.

## 9. Testing reversible terms

For a reverse rate constant `k_r >= 0`, compare the unrestricted model with the constrained model `k_r=0`.

`Delta Q = Q_(k_r=0) - Q_full`.

Little deterioration means the data do not require the reverse term. A substantial deterioration plus a finite interior profile gives stronger support for including it. This supports the empirical rate term; it does not prove an elementary molecular mechanism.

## 10. Model adequacy is not mechanism proof

A good mass-action fit means the observed dynamics are adequately represented over the experimental domain. Before adding complex intrinsic kinetics, examine temperature effects, activity/concentration differences, volume changes, mixing/sampling delays, mass transfer, adsorption/catalyst dynamics, diffusion, sensor behaviour, uncertain initial conditions, and missing/lumped species.

## 11. KineticFittingPot workflow

Raw measurements → stoichiometric consistency → optional reconciliation → kinetic fit → residual diagnostics → parameter identifiability → model-structure tests.
