# KineticFittingPot — Isothermal Batch Reactor Simulator

## Purpose

The KineticFittingPot **Isothermal Batch Reactor Simulation** workspace implements the Van de Vusse batch-reactor example used in the supplied teaching notes. It is designed as a transparent teaching model rather than a black-box calculator.

## Reaction network

- Reaction 1: `2 x1 -> x2`, with `r1 = k1 c1^2`
- Reaction 2: `x1 -> x3`, with `r2 = k2 c1`
- Reaction 3: `x3 -> x4`, with `r3 = k3 c3`

Species roles:

- x0: solvent
- x1: reactant
- x2: by-product
- x3: desired product
- x4: waste product

## Dynamic model

The net stoichiometric matrix is

```text
       r1  r2  r3
x0      0   0   0
x1     -2  -1   0
x2      1   0   0
x3      0   1  -1
x4      0   0   1
```

The state equation is

`dn/dt = V S r(c,T)`

with `c = n/V`.

Two volume models are implemented:

1. Constant volume — the initial liquid volume is retained throughout the simulation.
2. Composition-dependent volume — `V = sum(n_j M_j / rho_j)` is recalculated from the current species inventory.

## Reference kinetics

The rate constants are calculated using

`k_i = A_i exp(-E_i/(R T))`

The v1.7 default reference parameters are checked against the surviving MATLAB parameter file (`data/reference/ReadMyReactionDataFromMATLAB.m`):

| Reaction | A | E (kJ kmol^-1) |
| --- | ---: | ---: |
| 1 | 8088 m3 kmol^-1 s^-1 | 50434 |
| 2 | 4.7e8 s^-1 | 74650 |
| 3 | 8.73e5 s^-1 | 60889 |

v1.6 had transcribed reaction 3 as `A3 = 8.73e8` and `E3 = 60899`. The factor-of-1000 error in A3 caused x3 to be consumed almost immediately. v1.7 corrects the source data; the ODE formulation itself is unchanged.

At 60 C the corrected reference rate constants are approximately:

- `k1 ≈ 1.00e-4 m3 kmol^-1 s^-1`
- `k2 ≈ 9.27e-4 s^-1`
- `k3 ≈ 2.48e-4 s^-1`

The user can change temperature and, in the advanced controls, the A and E values.

## Numerical integration

The ODEs are integrated using `scipy.integrate.solve_ivp` with:

- method: RK45
- relative tolerance: 1e-6
- absolute tolerance: 1e-9
- adaptive internal step selection

The plotting grid is separate from the solver's internal time steps. A denser evaluation of the continuous RK45 solution is used to locate the simulated maximum of x3.

## Default reactor and charge basis

- reactor vessel volume: 1.00 m3
- nominal working volume: 0.70 m3
- x0 solvent volume: 0.35 m3
- x1 reactant volume: 0.35 m3
- initial vessel fill: 70%
- temperature: 60 C
- simulation duration: 120 min
- x2, x3 and x4 initially zero

The supplied MATLAB-checked reference case used 0.5 m3 `x0` + 0.5 m3 `x1`. KineticFittingPot retains that historical case as a regression anchor, but scales the default interface charge proportionally to 0.70 m3 so that a 1.00 m3 vessel is not implicitly shown at 100% liquid fill. The initial composition and concentrations are unchanged by this proportional scaling.

The reactor vessel volume and nominal working volume provide physical context and fill diagnostics; they do not alter the kinetic equations. Component molecular weights and densities are taken from the supplied teaching material/MATLAB parameter source.

## Suggested experiments

The workspace now places a guided **Suggested experiments with this simulation** section between the mathematical model and the simulation controls. Each experiment uses the common pattern **Try this → Look for → Think about** so that parameter changes are tied to an engineering question rather than made at random.

The initial experiment set asks the user to:

1. locate and interpret the optimum stopping time for `x3`;
2. change reactor temperature and compare rate/selectivity consequences;
3. change the initial `x0:x1` charge ratio while holding total charge near the reference working volume;
4. compare constant and composition-dependent liquid-volume assumptions;
5. change batch size while preserving composition, distinguishing intensive and extensive quantities;
6. change one Arrhenius parameter at a time and assess sensitivity to the kinetic model.

A separate **Model assumptions and adjustments** card identifies the inputs that can be changed directly in this workspace and the assumptions deliberately held fixed: well-mixed liquid phase, pure-batch operation with no inlet/outlet during reaction, and imposed isothermal reactor temperature.

## Outputs

KineticFittingPot displays:

- rate constants at the selected temperature;
- optimum stopping time based on maximum x3;
- maximum x3 amount;
- x1 conversion at that stopping point;
- x3 yield on initial x1;
- final liquid volume;
- species amounts vs time;
- concentrations vs time;
- reaction rates vs time;
- a dedicated x3 stopping-time plot;
- liquid volume vs time;
- initial / optimum / final state table;
- solver status and function-evaluation count;
- mass-conservation diagnostic.

### Species visibility

A multiselect above the dynamic trajectory plots controls which species are visible on the **amount** and **concentration** figures. x1–x4 are shown by default and x0 solvent is hidden by default because its larger amount can dominate the y-axis. Any species can be added or removed. This is a presentation control only: all species remain in the model, balances and diagnostic tables. Species colours are fixed so toggling one trace does not recolour the others.

## Diagnostic definitions

- reactant conversion: `X1 = (n1,0 - n1)/n1,0`
- desired-product yield: `Yx3 = n3/n1,0`
- displayed molar product selectivity: `Sx3/(x2+x4) = n3/(n2+n4)`

The selectivity expression is explicitly labelled as a teaching diagnostic for this network, not a universal selectivity definition.

## Scope boundary

KineticFittingPot retains this workspace as the validated isothermal forward simulator. This **isothermal workspace itself** does not include:

- fitted kinetic parameters from user experimental data;
- parameter confidence intervals;
- event-driven stopping;
- non-isothermal energy balances (now implemented in the separate Non-isothermal Batch Simulation workspace);
- heat-transfer/jacket dynamics;
- stiffness-method selection in the UI;
- arbitrary user-defined reaction networks.

These extensions are outside the scope of the current simulator.


## Retained v1.8 presentation refinement

The five primary simulation result cards use a slightly smaller value font than the shared default metric card. This prevents values/units such as `1.839 kmol` from dominating or wrapping unnecessarily while leaving the shared KineticFittingPot card style unchanged elsewhere.

The workspace is now named **Isothermal Batch Reactor Simulation** to distinguish it explicitly from the following non-isothermal development. Existing v1.6/v1.7 `?page=Batch Reactor Simulation` links remain accepted as a backward-compatible route.
