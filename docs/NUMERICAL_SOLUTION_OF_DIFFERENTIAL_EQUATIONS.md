# Numerical Solution of Differential Equations — KineticFittingPot Fundamentals

KineticFittingPot v1.23 adds a concise numerical-integration Fundamentals workspace adapted from the supplied `ODE_Integration(2C).pdf` notes.

This page focuses on the numerical principles needed to interpret dynamic reactor simulations, rather than providing a full numerical-analysis treatment. Its purpose is to establish the numerical ideas needed to understand KineticFittingPot's current dynamic simulators and more general dynamic reactor models.

## Core sequence

1. Analytical solutions can be obtained for selected ODEs, especially simple linear models, but coupled nonlinear reactor models generally require numerical integration.
2. An initial-value problem is written as

   `dy/dt = f(t, y, u), y(t0) = y0`.

3. Euler's method is used only as a transparent illustration of advancing a solution from an initial condition.
4. KineticFittingPot's existing models use SciPy `solve_ivp` with RK45 and adaptive internal step sizes.
5. Requested output times are not necessarily internal integration steps.
6. Known-time discontinuities should normally be made explicit integration boundaries: integrate to the boundary, change the operating condition, then restart.
7. State-triggered changes whose time is not known in advance are located using event/zero-crossing detection.
8. These ideas also apply to fed-batch feed schedules, recipe steps, set-point changes and state-triggered operating logic.

## KineticFittingPot numerical defaults referenced on the page

Established reactor models typically use:

- `solve_ivp`
- RK45
- `rtol = 1e-6`
- `atol = 1e-9`

No numerical engine is changed by v1.23.

## Source provenance

The supplied original notes are bundled unchanged as:

`data/reference/ODE_Integration(2C).pdf`
