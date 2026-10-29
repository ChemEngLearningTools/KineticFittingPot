# Batch Reactor Simulation — v1.5 problem and numerical method

KineticFittingPot v1.5 activates the Batch Reactor Simulation workspace but deliberately stops before executing the numerical simulation. Its purpose is to make the engineering model and numerical implementation explicit before interactive controls and plots are introduced.

## Reference example

The built-in simulator is based on the Van de Vusse reaction network from the supplied batch-reactor teaching notes:

- `2 x1 -> x2`, with `r1 = k1 c1^2`
- `x1 -> x3`, with `r2 = k2 c1`
- `x3 -> x4`, with `r3 = k3 c3`

The species roles are solvent `x0`, reactant `x1`, by-product `x2`, desired product `x3`, and waste product `x4`.

The source notes describe a reference batch initially containing 0.5 m3 of `x1` and 0.5 m3 of water/solvent `x0`, at 60 C, followed for approximately two hours.

The current KineticFittingPot interface keeps that historical MATLAB-checked case as the numerical reference, but the **default teaching charge is scaled proportionally to a physically explicit reactor basis**: a 1.00 m3 vessel, 0.70 m3 nominal working volume, 0.35 m3 `x0` and 0.35 m3 `x1`. Scaling both charged component volumes by the same factor preserves the initial composition and concentrations while avoiding an implicit 100% vessel fill.

## Model structure

With the solvent retained as a zero-reaction row, the state is the species-mole vector and the dynamic model is

`dn/dt = V S r(c,T)`.

For composition-dependent liquid volume, KineticFittingPot uses the additive-volume relation from the Fundamentals workspace.

## Numerical implementation

The interactive implementation uses `scipy.integrate.solve_ivp` with:

- default method: `RK45`
- relative tolerance: `1e-6`
- absolute tolerance: `1e-9`
- an output grid used for display, independent of the solver's adaptive internal time steps.

The ODE callback will perform the sequence:

`n(t) -> V -> c -> k(T) -> r -> V S r`.

The built-in simulator reports species moles/concentrations, volume, reaction rates, conversion, yield/selectivity and the batch time at which the desired product `x3` reaches its maximum.

No SciPy dependency is added in v1.5 because the solver is described but not yet executed. SciPy will be added when the interactive solver is implemented.
