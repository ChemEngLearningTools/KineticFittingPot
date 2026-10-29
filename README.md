# KineticFittingPot v1.01 standalone

Standalone extraction of the kinetic modelling, fitting and diagnostics workflow.

## Local Windows installation

Recommended folder: `C:\nmjw2\KineticFittingPot`

1. Extract this build into the folder.
2. Double-click `run_KineticFittingPot.bat`.
3. On first run the launcher creates `.venv` and installs the pinned requirements.
4. Use `test_KineticFittingPot.bat` to run the bundled smoke/regression tests.

The original source application is not modified by this standalone build.


## v1.01 home/navigation update

The Home page now follows the ReactionPot section-selector pattern. Choose one of four sections and only the corresponding coloured workspace cards are shown. The local launcher also opens the browser automatically.


## v1.15 benchmark extension
Run `test_KineticFittingPot_Public_Readiness.bat`. Read V1_15_EXTENDED_BENCHMARK_NOTES.md.

## v1.16 public fit safety
Run `test_KineticFittingPot_Public_Worker.bat` to test nonblocking admission, worker hard timeout and reuse after timeout. Public mode can be previewed using `KINETICFITTINGPOT_MODE=public_cloud`. See `V1_16_PUBLIC_WORKER_SAFEGUARDS_NOTES.md`.
