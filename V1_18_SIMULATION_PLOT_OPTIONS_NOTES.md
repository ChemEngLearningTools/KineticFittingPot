# KineticFittingPot v1.18 — Simulation Plot Options (local review)

Based on confirmed v1.17 technical baseline. Scope is simulation plots only; independent fit/validation datasets are planned for v1.19.

## Changes
- Shared `utils/trajectory_plots.py` transforms saved molar inventories into mole fractions, mass fractions, net conversion, and overall selectivity.
- Built-in batch simulation and Excel-defined model simulation offer an **Additional species plot** selector. Existing amount, concentration, rate and volume plots remain as default and are not removed.
- Mass fractions use model molecular weights. Undefined conversions/selectivities raise an explanatory message or draw a gap instead of generating inf/nan spikes.
- Conversion reports **net disappearance**, not reaction-specific conversion; product/reactant selectivity is net molar product formation per mole of net reactant disappearance divided by a **user-specified theoretical product/reactant molar ratio**. This is not reaction-path selectivity; chemical interpretation remains model-specific.
- The Excel-defined simulation plot area is a Streamlit fragment so changing plot controls does not erase results by triggering the page's Run button guard.

## Checks performed
- `python -m compileall` on modules and utils: PASS
- Mole/mass fraction normalization, conversion/selectivity transformations, invalid molecular weights: PASS
- Built-in batch simulator smoke test: PASS
- Excel-defined general batch solver smoke test: PASS

## Outstanding manual checks
- Browser interaction, in particular changing plot variable after an Excel-defined run without re-running the calculation.
- Zero/negative inventories and degenerate chemistry; interpretation of selectivity for complex networks.
- v1.19 validation dataset extension, then complete regression and backup.

No changes were made to the ODE solver, fitting engine, worker safeguards or public computation budgets.
