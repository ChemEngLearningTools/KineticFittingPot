# v1.22 — Fitting/validation figure layout restoration

- Restored the **exact v1.19** figure-title and Plotly layout path for fitting trajectories; no external Streamlit fitting heading and no added top-margin override.
- Validation trajectories retain an external dataset heading (to prevent collision with long titles), dashed predictions and open-diamond observations; legend remains horizontal immediately above chart with a compact 90-pixel top margin, instead of the 155-pixel margin in v1.20–v1.21.
- Only `modules/kinetic_fitting.py` changed in application code. No changes to scientific calculations, dataset selection, workbook exports, diagnostics, public fitting worker, or budgets.
- The horizontal legend may occupy more than two rows on unusually narrow devices; please visually confirm for biodiesel on the local screen.
- Review build only; confirm both fitted and held-out validation figures before recording as baseline.
