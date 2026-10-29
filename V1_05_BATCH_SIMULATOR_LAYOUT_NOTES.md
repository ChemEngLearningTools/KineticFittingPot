# KineticFittingPot v1.05 — Batch simulator layout review

Based on v1.04. This is a local review build, not deployed.

## Changes (interface module only)
- Removed references to accompanying batch-reactor notes and the historical MATLAB implementation from the built-in simulator's user-facing text.
- Retained the Van de Vusse name, reactions, underlying mathematical content and physical modelling assumptions.
- Replaced the long bulleted species list with a compact, two-column species/role table.
- Moved the stoichiometric matrix, state/rate vectors, balances, integrator description, and assumptions into a single collapsed **Mathematical model and numerical method** expander.
- Moved the six **Suggested experiments** below all calculated results, figures and diagnostics.
- Renamed **Run simulation** to **Simulation results**, preserving reactive recomputation.

## Validation scope
- Python syntax compiled successfully.
- All scientific utilities, data, and templates are unchanged from v1.04.
- Interactive rendering and numerical regression should be tested locally.

## Suggested review
Check species table sizing, expand mathematical model, use default batch simulation, inspect all figures and diagnostic metrics, and confirm the six experiments now appear last.
