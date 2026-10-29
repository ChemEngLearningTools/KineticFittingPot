# v1.12 — Shared table height fix

The shared `show_dataframe` helper no longer forwards `height=None` to `st.dataframe`. Omitted heights use the installed Streamlit default. Explicit positive pixel heights, `stretch` and `content` are passed through. Other values raise an informative error.

This affects the native-table fallback, used by tables with >150 rows, >18 columns, with native keyword options, or explicit heights. The small HTML table path is unchanged. No scientific engine, data, worksheet or other UI module was changed.

Recheck Advanced Model Diagnostics > Parameter-level local diagnostics using the same completed fitting workbook. Also check fitting preview and Basic Diagnostics. Full Streamlit interactive tests are still required locally.
