# KineticFittingPot v1.08 — public fitting review

- Public fitting enabled using the existing SciPy engine, with central configurable caps in `utils/deployment.py`.
- Public fitting currently allows 8 fitted parameters, 6 selected datasets, 500 observations, 12 species/reactions, 2 MB uploads, 3 starts and 150 optimiser evaluations per start.
- Cooperative budget: 3,600 actual ODE integrations, 400,000 RHS evaluations or 60 seconds (no hard deadline guarantee during blocking/native calls).
- Budget exhaustion terminates the current fit with a warning and **does not** report it as converged.
- Optimiser failure and non-convergence are distinguished; local fitting retains its previous controls.
- Observation coverage now uses a compact centred table, omitting redundant decimal places.
- Heavy post-fit diagnostics remain disabled on public deployment.

**Before public deployment**: benchmark representative catalytic, biodiesel and 8-parameter/6-dataset problems on the intended host and verify the time limit and concurrent-user behaviour. The current timeout is cooperative, not a verified hard process-level timeout.
