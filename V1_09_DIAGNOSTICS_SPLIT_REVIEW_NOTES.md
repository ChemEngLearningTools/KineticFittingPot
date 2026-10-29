# v1.09 — Basic / Advanced Diagnostics and Table Alignment

- Basic Model Diagnostics is now linked directly under Kinetic Parameter Fitting and is enabled in public mode. It reads the completed fitting workbook and uses its stored Fit_Predictions; no optimisation or forward ODE integration is initiated. The public limit is 500 stored rows, with upload prechecks.
- Advanced Model Diagnostics retains the existing full workspace and is restricted in public mode. It is listed under Further Analysis. The previous navigation name remains as an alias for compatibility.
- Fitting, custom simulation, and advanced diagnostics display tables use a common static HTML table helper up to 150 rows; numeric columns are centered and display up to six significant figures. Larger tables retain Streamlit's native grid.
- Original engines and workbook schemas remain unchanged.
- This is a local review build: public fitting and diagnostics should undergo performance and input-hardening tests before deployment.

Validation: the existing diagnostics engine smoke test passes after updating the homepage assertions. Python syntax and archive-integrity tests pass. Full Streamlit interactive tests were unavailable in this environment.
Basic export currently includes the stoichiometric summary; residual tables and figures are displayed in the interface, but are not appended as separate workbook sheets in this first review build.
