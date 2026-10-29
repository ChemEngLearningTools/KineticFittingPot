# KineticFittingPot v1.21 — blank internal Plotly title fix

- Baseline: v1.20 accepted figure layout.
- Targeted fix: replace `title=None` on fitting/validation trajectory plots with `title=dict(text="")`, so the internal Plotly title renders as an explicit empty string instead of an undefined placeholder.
- Keep the external dataset title, horizontal legend, margins and plotted traces unchanged.
- No changes to numerical models, fitting engine, diagnostics, workbook formats or public safeguards.
- Locally verify both a fitted and held-out validation dataset plot, at the user's browser width, before accepting this build.
