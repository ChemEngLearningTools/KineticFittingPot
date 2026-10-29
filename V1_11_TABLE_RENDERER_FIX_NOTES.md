# KineticFittingPot v1.11 — Table Renderer Regression Fix

## Cause
The v1.10 table helper used `pd.io.formats.style.Styler` in an `isinstance` check. With Pandas versions that have not imported the style submodule, `pd.io.formats.style` does not exist, raising `AttributeError` on the first table displayed. The page aborts during the first dataset help expander, before reaching the upload widget.

## Fix
Explicitly import `Styler` from `pandas.io.formats.style` and use that class in `isinstance`, supporting both DataFrame and Styler input without affecting the numeric values. No engine, dataset, workbook, or fitting code changes.

## Testing
* Test plain DataFrame and Styler display under a simulated Streamlit interface.
* Test the fitting page reaches the upload widget when no workbook has been supplied.
* Python compilation and package integrity.

Please retest the full Excel upload and fitting flow in your local Streamlit environment; interactive full-workflow verification was not available in this runtime.
