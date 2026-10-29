# KineticFittingPot v1.20 — Validation figure title and legend layout

## Scope
Presentation-only fix in `modules/kinetic_fitting.py` for fitted and independent-validation trajectory figures.

- Dataset ID, description and FITTING / VALIDATION designation appear in a separate Streamlit heading above the Plotly chart.
- Plotly chart no longer embeds its title in the same space as the legend.
- Horizontal legend remains above the plotting area, with a larger dedicated top margin for wrapped entries.
- Colour mapping, validation dashed model lines, open-diamond experimental markers, residuals, fit logic, and numerical computations are unchanged.

## Local verification
Run `test_KineticFittingPot_Final_Readiness.bat` and examine the validation plots in a browser, including the 5-species biodiesel figure at your normal window width. The automated suite does not perform pixel-level visual checking.

## Status
Local review build only; retain the last confirmed backup unchanged.
