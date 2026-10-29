# KineticFittingPot v1.04 — editorial review

## Purpose
Editorial-only revision of the accepted v1.03 light-theme build. User-facing explanations now describe methods and behaviour rather than prior development agreements, plans or specifications.

## Changes
- Revised fitting fundamentals to describe bounded multistart optimisation, weighting, parameter bounds, datasets and identifiability in present tense.
- Rephrased stoichiometry, ODE, batch-reactor and model-diagnostics fundamentals to remove roadmap language and developer-facing instructions.
- Refined explanatory text on simulation and post-fit diagnostics.
- Updated relevant Markdown documentation, including the formerly 'planned' batch numerical implementation.
- Retained educational uses of 'first', 'later' and 'should' where they describe mathematics, physical reasoning or proper scientific caution.

## Scientific integrity
All `utils/` files and bundled `data/` and `templates/` contents are byte-for-byte identical to v1.03. No calculation algorithms, defaults, optimisation settings, navigation or plotting changes are intended.

## Review status
Static Python syntax parsing passed. Full interactive inspection and scientific regression tests are still required locally. This is a **review build**, not a confirmed baseline.

## Recommended local checks
Review all Fundamentals pages, particularly Kinetic Fitting Fundamentals and Model Diagnostics Fundamentals. Confirm the wording of currently implemented capabilities matches what the interface actually produces, and that buttons and worked examples still run as before.
