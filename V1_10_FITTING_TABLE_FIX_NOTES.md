# v1.10 — Fitting preview table crash fix

## Fixed

- `show_dataframe()` now accepts a Pandas `Styler` as well as ordinary DataFrames. It unwraps the original numeric DataFrame before rendering, preventing `ValueError: DataFrame constructor not properly called!`.
- The redundant `_center_numeric` Styler conversion in `modules/kinetic_fitting.py` now passes the DataFrame unchanged; numerical alignment is handled by the shared table renderer.

## Scope

No fitting algorithms, model evaluations, datasets, workbook schemas, deployment limits, or scientific calculations were changed. The fix targets the exception raised immediately after uploading the fitting example, as well as the same potential error at other fitting tables.

## Verification

- Source syntax compilation of all application Python modules.
- Checks of both normal DataFrame and Pandas Styler input paths to `show_dataframe` (static logic / structural checks; not a live Streamlit session).
- Scientific module file checksums compared against v1.09.
- ZIP integrity and contained file list checked.

Please retest uploading the catalytic example in Kinetic Parameter Fitting, the fit parameter preview and final results tables, then Basic and Advanced Diagnostics. This is a targeted correction, not a final deployed baseline.
