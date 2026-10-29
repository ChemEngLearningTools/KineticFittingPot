# Simulate Your Own Model — Isothermal Batch Reactor

KineticFittingPot v1.17 extends the spreadsheet-defined forward simulator for general well-mixed isothermal batch reaction networks to support either constant or composition-dependent liquid volume.

## Scope

The current version supports:

- isothermal operation;
- well-mixed batch reactor;
- **constant liquid volume** or **composition-dependent liquid volume**;
- arbitrary species and reaction counts within teaching-workflow safety limits;
- concentration-based kinetic expressions;
- parameter values supplied in the workbook;
- restricted mathematical syntax rather than arbitrary executable Python.

The mathematical form is

`dn/dt = V S r(c,theta)`

with

`c = n/V`.

For composition-dependent liquid volume, KineticFittingPot recalculates

`V = sum(n_j M_j / rho_j)`

throughout the batch.

## Workbook structure

Required sheets:

1. `Model` — model name, temperature, initial volume, batch duration, output point count and `Volume_Model`.
2. `Species` — species identifiers, display names, initial concentrations, molecular weights, densities and default plot visibility.
3. `Parameters` — parameter identifiers, values, units and optional parameter-fitting metadata.
4. `Reactions` — one row per reaction containing a human-readable description, rate expression and stoichiometric coefficients.

KineticFittingPot replaces/creates:

5. `Results_TimeSeries` — time, liquid volume, species amounts/concentrations and reaction rates.
6. `Results_Summary` — selected target-species peak, initial/final volume and solver diagnostics.

## Volume model

The `Model` sheet accepts:

- `constant` — `Initial_Volume_m3` is retained throughout the batch;
- `composition_dependent` — the current liquid volume is calculated from the species inventory using molecular weight and density.

For `composition_dependent`, molecular weight and density must be positive for every species. KineticFittingPot also checks that the initial concentrations, molecular weights, densities and `Initial_Volume_m3` describe the same initial charge. It rejects an inconsistent workbook rather than silently rescaling it.

## Safe expression syntax

A rate expression may use:

- `c_<Species_ID>` concentration variables;
- identifiers defined on the Parameters sheet;
- `+`, `-`, `*`, `/`, `**` and parentheses;
- `exp()`, `log()`, `sqrt()` and `abs()`.

The expression is parsed through Python's AST and validated against a small explicit whitelist. Spreadsheet content is not passed to unrestricted `eval()`.

## Van de Vusse reference workbook

The bundled template defines the same Van de Vusse case as the dedicated KineticFittingPot isothermal simulator:

- `R1: 2 x1 -> x2`, `r1 = k1*c_x1**2`;
- `R2: x1 -> x3`, `r2 = k2*c_x1`;
- `R3: x3 -> x4`, `r3 = k3*c_x3`.

The Species sheet contains the same molecular weights and densities as the dedicated simulator. The template defaults to `composition_dependent` so the new capability is visible immediately; change `Volume_Model` to `constant` to recover the original constant-volume Excel case.

Reference regression at 60 C and a 1.0 m3 initial charge:

- composition-dependent Excel model: x3 peak about `1.82568768 kmol` at `1688.61 s`, final volume about `0.91274893 m3`;
- dedicated composition-dependent simulator: same peak amount to better than `1e-7 kmol`, displayed peak time within one second, and the same final volume to numerical precision;
- constant-volume Excel model: x3 peak about `1.83874768 kmol` at `1699.53 s`;
- dedicated constant-volume simulator: same peak amount to numerical precision and peak time within `0.01 s`.

The small displayed peak-time difference in the composition-dependent comparison arises because the dedicated simulator reports the maximum from a dense regular grid, whereas the general simulator refines the local maximum continuously.

## Why this matters for kinetic fitting

The spreadsheet format separates the model definition from the numerical solver. The kinetic-fitting workspace uses the same model definitions and ODE framework while varying selected parameter values and comparing the simulated trajectory with experimental data. The `Fit_Later`, `Lower_Bound` and `Upper_Bound` columns are available as fitting metadata but not used by the forward simulator.

---

## Public Streamlit deployment limits (v1.33)

The public KineticFittingPot deployment keeps this workspace available but applies cloud-only resource protection. The supported local Windows build is unchanged.

Public limits are: 2 MB workbook upload, 20 MB uncompressed XLSX package, 12 species, 12 reactions, 40 parameters, 24 h maximum batch duration, 1,200 output points, 20,000 ODE right-hand-side evaluations and approximately 10 s maximum solver wall time. XLSX package structure is checked before workbook parsing. These limits protect a shared teaching server and are not part of the underlying general-model formulation.
