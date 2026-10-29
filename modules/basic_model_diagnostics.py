from __future__ import annotations

import io
import streamlit as st
import pandas as pd
import numpy as np

from utils.deployment import is_public_cloud, public_cloud_workbook_violations
from utils.model_diagnostics_engine import (
    parse_completed_fit_workbook, stoichiometric_diagnostics,
    residual_diagnostic_points, ModelDiagnosticsValidationError,
)
from utils.model_diagnostics_export import build_model_diagnostics_workbook
from utils.ui import workspace_header, chips, metric_card, navigate, show_dataframe


def render() -> None:
    workspace_header(
        "Basic Model Diagnostics",
        "Review stored fitted trajectories, residuals and stoichiometric structure from a completed fitting workbook, without rerunning optimisation.",
        section="Kinetic fitting", accent="#2868ad",
    )
    chips([("Completed fit", "blue"), ("Stored predictions", ""),
           ("Residual summaries", "blue"), ("Stoichiometric checks", "")])
    st.info("Basic diagnostics read existing fitting results and do not carry out additional kinetic parameter estimation. Residual quality alone does not establish parameter identifiability.")
    uploaded = st.file_uploader("Upload completed kinetic-fitting results workbook (.xlsx)", type=["xlsx"], key="basic_diagnostics_upload")
    if uploaded is None:
        st.caption("Download a completed fitting workbook from Kinetic Parameter Fitting, then upload it here.")
        if st.button("Open Kinetic Parameter Fitting →", key="basic_to_fit_empty"):
            navigate("Kinetic Parameter Fitting")
        return
    raw = uploaded.getvalue()
    if is_public_cloud():
        issues = public_cloud_workbook_violations(raw)
        if issues:
            for issue in issues:
                st.error(issue)
            return
    try:
        info = parse_completed_fit_workbook(raw)
        diag = stoichiometric_diagnostics(info)
        points = residual_diagnostic_points(raw, info)
    except Exception as exc:
        st.error(f"The workbook could not be used for basic diagnostics: {exc}")
        return
    if is_public_cloud() and len(points) > 500:
        st.error("Basic diagnostics on the public server support at most 500 stored observation rows.")
        return
    cols = st.columns(4)
    for col, (name, value, detail) in zip(cols, [
        ("Datasets", len(info.problem.datasets), "completed fit"),
        ("Measured species", len(info.measured_species), "with observations"),
        ("Observations", len(points), "stored fit predictions"),
        ("Fitted parameters", len(info.fitted_parameters), "estimated values"),
    ]):
        with col:
            metric_card(name, str(value), detail, compact=True)
    st.markdown("## Fitted parameters")
    show_dataframe(pd.DataFrame([{"Parameter": k, "Fitted value": v}
                                 for k, v in info.fitted_parameters.items()]), use_container_width=True, hide_index=True)
    st.markdown("## Stoichiometric consistency")
    st.write("These are structural properties of the uploaded reaction network; they do not prove that an estimated kinetic parameter is unique.")
    show_dataframe(pd.DataFrame([
        {"Quantity": "Species", "Value": diag["species_count"]},
        {"Quantity": "Reactions", "Value": diag["reaction_columns"]},
        {"Quantity": "Stoichiometric rank", "Value": diag["rank"]},
        {"Quantity": "Independent closed-batch invariants", "Value": diag["invariant_dimension"]},
        {"Quantity": "Measured-only invariants", "Value": diag["measured_invariant_dimension"]},
    ]), use_container_width=True, hide_index=True)
    st.markdown("## Stored model-versus-measurement residuals")
    st.caption("Residual = fitted value − measured value. Positive values indicate overprediction.")
    if not points:
        st.warning("No stored fitted-prediction observations were found.")
        return
    frame = pd.DataFrame([{
        "Dataset": p.dataset_id, "Time (s)": p.time_s,
        "Species": p.species_id, "Measured": p.measured_value,
        "Fitted": p.fitted_value,
        "Residual": p.residual_model_minus_measured,
    } for p in points])
    st.markdown("### Residual summary by species")
    summary = []
    for species, group in frame.groupby("Species", sort=False):
        residuals = group["Residual"].to_numpy(dtype=float)
        summary.append({"Species": species, "Observations": len(group),
                        "Bias": float(np.mean(residuals)),
                        "RMSE": float(np.sqrt(np.mean(residuals ** 2))),
                        "MAE": float(np.mean(np.abs(residuals)))})
    show_dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
    import plotly.express as px
    for dataset, group in frame.groupby("Dataset", sort=False):
        st.markdown(f"### {dataset} — fitted and observed")
        tidy = group.melt(id_vars=["Time (s)", "Species"], value_vars=["Measured", "Fitted"],
                          var_name="Series", value_name="Concentration")
        fig = px.line(tidy, x="Time (s)", y="Concentration", color="Species", line_dash="Series",
                      markers=True, template="plotly_white")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Residuals versus time")
    fig = px.scatter(frame, x="Time (s)", y="Residual", color="Species", facet_row="Dataset",
                     template="plotly_white")
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b")
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Residuals versus fitted value")
    fig = px.scatter(frame, x="Fitted", y="Residual", color="Species", template="plotly_white")
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Show stored observation table"):
        show_dataframe(frame, use_container_width=True, hide_index=True)
    st.markdown("## Download basic diagnostics")
    try:
        output = build_model_diagnostics_workbook(raw, info, diag,
                    reactionpot_version="KineticFittingPot v1.09 (basic diagnostics)")
        st.download_button("Download basic-diagnostics workbook", output,
            file_name="kinetic_fit_basic_diagnostics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as exc:
        st.warning(f"Basic diagnostics export could not be created: {exc}")
    if st.button("Open Kinetic Parameter Fitting →", key="basic_to_fit"):
        navigate("Kinetic Parameter Fitting")
