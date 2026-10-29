# KineticFittingPot v1.15 — Extended public fitting benchmarking

- App code, numerical engines and datasets remain unchanged from v1.14/v1.13.
- Updated two historical UI assertions to match the accepted v1.13 homepage and simulator layout.
- Added public fitting benchmark of six-parameter biodiesel using existing completed fitting workbook.
- Added synthetic eight-parameter/six-dataset workload based on biodiesel with two additional rate modifiers and three duplicated dataset/observation sets. **This is strictly a stress test, not independent experimental data or evidence of identifiability.**
- Each extended benchmark runs in a bounded subprocess. The subprocess timeout is a *testing harness guard*, not an application runtime protection.
- `PASS` requires convergence; `LIMIT_REACHED` explicitly identifies an enforced computation budget. `NON_CONVERGED`, `TIMEOUT` and `FAIL` are distinct outcomes.
- Output: validation_reports/KineticFittingPot_v1_15_results.md and JSON.
- Existing public limits and algorithms are preserved. Hard timeout and concurrency readiness remain outstanding.

## Initial validation run (22 October 2026, this environment)
- Historical interface smoke tests: corrected and passed.
- Biodiesel six-parameter/three-dataset case: converged, approximately 684 integrations, 290,148 RHS evaluations, 4.6 s fitting execution (machine-specific).
- Synthetic eight-parameter/six-dataset stress case: explicitly **LIMIT_REACHED** due to RHS budget (400,001 > 400,000), approximately 776 integrations. This is a correct controlled stop, **not** successful parameter fitting.
- The biodiesel result already uses about 73% of the configured RHS-call budget, so the limits should not be declared suitable for every eight-parameter/six-dataset job.
- Reports generated on Windows are needed to compare timings and workload on the intended local environment.
