from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from statistics import NormalDist

from utils.general_batch_model import ModelValidationError
from utils.kinetic_fitting_engine import FittingValidationError
from utils.model_diagnostics_engine import (
    ModelDiagnosticsValidationError,
    balance_points_with_uncertainty,
    classify_invariants,
    format_invariant,
    local_parameter_diagnostics,
    profiled_objective_diagnostics,
    parse_completed_fit_workbook,
    reconcile_observations_for_invariant,
    residual_autocorrelation,
    residual_diagnostic_points,
    simple_nonnegative_integer_invariants,
    stoichiometric_diagnostics,
    time_grid_regularity,
)
from utils.model_diagnostics_export import build_model_diagnostics_workbook
from utils.ui import chips, metric_card, navigate, teaching_table, workspace_header, show_dataframe


ACCENT = "#22c55e"
COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692"]


def _dark(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#17314f"),
        margin=dict(l=25, r=25, t=60, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def _rgba(hex_colour: str, alpha: float) -> str:
    text = hex_colour.lstrip("#")
    r, g, b = (int(text[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _summary_cards(info, diag) -> None:
    summary = info.summary
    cols = st.columns(6)
    items = [
        ("Datasets", str(len(info.problem.datasets)), "completed fit"),
        ("Measured species", str(len(info.measured_species)), ", ".join(info.measured_species)),
        ("Species in model", str(diag["species_count"]), "stoichiometric rows"),
        ("Rate columns", str(diag["reaction_columns"]), "defined rate expressions"),
        ("Stoich. rank", str(diag["rank"]), "independent reaction directions"),
        ("Mole balances", str(diag["invariant_dimension"]), "independent invariants"),
    ]
    for col, item in zip(cols, items):
        with col:
            metric_card(*item, compact=True)

    fit_cols = st.columns(4)
    fit_items = [
        ("Fit parameters", str(len(info.fitted_parameters)), ", ".join(info.fitted_parameters)),
        ("Best weighted SSE", f"{float(summary.get('Best weighted SSE', np.nan)):.4g}" if summary.get("Best weighted SSE") is not None else "—", str(summary.get("Weighting", ""))),
        ("Raw RMSE", f"{float(summary.get('Best raw RMSE', np.nan)):.4g}" if summary.get("Best raw RMSE") is not None else "—", "kmol m⁻³"),
        ("Measured-only balances", str(diag["measured_invariant_dimension"]), "direct rate-free checks"),
    ]
    for col, item in zip(fit_cols, fit_items):
        with col:
            metric_card(*item, compact=True)


def _stoichiometric_matrix(info) -> None:
    model = info.problem.model
    st.markdown("### Stoichiometric matrix used by the fit")
    if len(model.reaction_ids) <= 12 and len(model.species_ids) <= 24:
        def fmt(value: float) -> str:
            x = float(value)
            if abs(x - round(x)) < 1e-10:
                return str(int(round(x)))
            return f"{x:.5g}"
        rows = [
            [sid, *[fmt(v) for v in model.stoichiometric_matrix[i, :]]]
            for i, sid in enumerate(model.species_ids)
        ]
        teaching_table(
            ["Species", *model.reaction_ids],
            rows,
            alignments=["left", *(["center"] * len(model.reaction_ids))],
        )
    else:
        data = {"Species": list(model.species_ids)}
        for j, rid in enumerate(model.reaction_ids):
            data[rid] = [float(v) for v in model.stoichiometric_matrix[:, j]]
        show_dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    st.caption(
        "KineticFittingPot uses species as rows and defined rate expressions/reaction columns as columns. "
        "Forward/reverse rate columns may be stoichiometrically dependent even though their kinetic expressions are different."
    )


def _constraint_table(info, diag) -> None:
    species_ids = info.problem.model.species_ids
    rows = []
    for i, item in enumerate(diag["classified_full_basis"], start=1):
        status = "Fully observed" if item.fully_observed else "Requires " + ", ".join(item.missing_species)
        rows.append([
            f"B{i}",
            format_invariant(item.coefficients, species_ids),
            status,
        ])
    if rows:
        teaching_table(
            ["Independent constraint", "Mole-balance relationship", "Raw-data status"],
            rows,
            alignments=["center", "left", "left"],
        )
    else:
        st.info("This stoichiometric matrix has full row rank, so it has no non-trivial closed-batch mole invariants.")

    st.caption(
        "These are independent generators of the invariant space. The invariant space contains infinitely many linear combinations, "
        "so the three biodiesel relationships shown here are not the only conserved totals that can be written down."
    )


def _simple_integer_constraint_table(info) -> dict | None:
    st.markdown("## Simple integer conserved quantities")
    st.markdown(
        "Independent invariants tell us the dimension of the conserved subspace, but other linear combinations can be more intuitive. "
        "KineticFittingPot can therefore enumerate **primitive non-negative integer** conserved quantities within a small coefficient range. "
        "Scaled duplicates are removed; these relationships contain no new independent information."
    )
    c1, c2 = st.columns([1, 3])
    with c1:
        max_coeff = st.slider(
            "Maximum coefficient",
            min_value=1,
            max_value=6,
            value=4,
            step=1,
            key="diag_integer_max_coeff",
            help="Search coefficient vectors l with 0 ≤ lᵢ ≤ this value, retaining only primitive vectors satisfying lᵀS = 0.",
        )
    with c2:
        st.caption(
            "The default 0–4 search is intentionally small and chemically readable. For large species sets, exhaustive enumeration is disabled rather than allowing a combinatorial search to grow silently."
        )

    try:
        simple = simple_nonnegative_integer_invariants(
            info.problem.model.stoichiometric_matrix,
            max_coefficient=max_coeff,
        )
    except ModelDiagnosticsValidationError as exc:
        st.warning(str(exc))
        return None

    classified = classify_invariants(simple, info.problem.model.species_ids, info.measured_species)
    st.metric("Primitive simple conserved quantities found", len(simple))
    rows = []
    for i, item in enumerate(classified, start=1):
        status = "Fully observed" if item.fully_observed else "Requires " + ", ".join(item.missing_species)
        rows.append({
            "#": i,
            "Conserved quantity": format_invariant(item.coefficients, info.problem.model.species_ids),
            "Raw-data status": status,
            "Species used": len(item.participating_species),
            "Coefficient sum": int(sum(item.coefficients)),
        })
    if rows:
        show_dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(520, 72 + 35 * len(rows)))
    else:
        st.info("No primitive non-negative integer conserved quantities were found within the selected coefficient range.")

    fully_observed_count = sum(item.fully_observed for item in classified)
    st.caption(
        f"Within this finite search KineticFittingPot found {fully_observed_count} relationship{'s' if fully_observed_count != 1 else ''} that use measured species only. "
        "The number of **independent** invariants is unchanged; the catalogue simply exposes alternative chemically readable linear combinations."
    )
    return {"max_coefficient": int(max_coeff), "classified": classified}


def _measured_constraint_table(info, diag) -> None:
    species_ids = info.problem.model.species_ids
    basis = diag["measured_basis"]
    st.markdown("## Constraints available from the measured species alone")
    st.markdown(
        "KineticFittingPot solves the left-null-space problem again **after restricting S to the measured species rows**. "
        "This is important: a fully observed invariant may be a linear combination of the full-model basis vectors and should not be missed merely because a different algebraic basis was chosen."
    )
    if not basis:
        st.warning(
            "No non-trivial invariant can be formed entirely from the measured species in this workbook. "
            "Any stoichiometric balance check would require at least one unmeasured or reconstructed species."
        )
        return
    rows = []
    for i, coeffs in enumerate(basis, start=1):
        participating = ", ".join(sid for sid, c in zip(species_ids, coeffs) if c != 0)
        rows.append([f"M{i}", format_invariant(coeffs, species_ids), participating])
    teaching_table(
        ["Measured constraint", "Direct raw-data relationship", "Measured channels used"],
        rows,
        alignments=["center", "left", "left"],
    )
    st.success(
        f"{len(basis)} independent constraint{' is' if len(basis)==1 else 's are'} available without using the fitted rate law or model-predicted unmeasured species."
    )


def _uncertainty_controls(info) -> tuple[float, float]:
    st.markdown("### Measurement-uncertainty model")
    supplied = sum(1 for obs in info.problem.observations if obs.sigma is not None and np.isfinite(obs.sigma) and obs.sigma > 0)
    total = len(info.problem.observations)
    c1, c2 = st.columns(2)
    with c1:
        relative_pct = st.number_input(
            "Assumed relative measurement uncertainty (1σ, %)",
            min_value=0.0,
            max_value=25.0,
            value=3.0,
            step=0.5,
            key="diag_relative_sigma_pct",
            help="Used only when the workbook does not supply a positive Sigma_kmol_m3 for that observation.",
        )
    with c2:
        absolute_floor = st.number_input(
            "Absolute uncertainty floor (1σ, kmol m⁻³)",
            min_value=0.0,
            value=0.002,
            step=0.001,
            format="%.4f",
            key="diag_absolute_sigma_floor",
            help="Combined in quadrature with the relative term. This prevents near-zero concentration measurements from being treated as perfectly precise.",
        )
    if supplied:
        st.caption(
            f"Positive workbook sigma values are used in preference to the assumptions above ({supplied} of {total} observation rows provide sigma). "
            "Missing sigma values use σ = √[(p·|C|)² + σ_floor²]."
        )
    else:
        st.caption(
            "This workbook does not provide pointwise measurement sigma values. KineticFittingPot therefore uses the explicit sensitivity assumption "
            "σ = √[(p·|C|)² + σ_floor²]. These are diagnostic assumptions, not experimentally established assay uncertainties."
        )
    return float(relative_pct) / 100.0, float(absolute_floor)


def _consistency_monitor(info, diag):
    basis = list(diag["measured_basis"])
    if not basis:
        return None
    species_ids = info.problem.model.species_ids
    st.markdown("## Stoichiometric-consistency monitoring")
    options = {
        f"M{i} · {format_invariant(coeffs, species_ids)}": coeffs
        for i, coeffs in enumerate(basis, start=1)
    }
    label = st.selectbox("Measured invariant to monitor", list(options), index=0, key="diag_measured_invariant")
    coeffs = options[label]
    relative_fraction, absolute_floor = _uncertainty_controls(info)

    try:
        points = balance_points_with_uncertainty(
            info,
            coeffs,
            assumed_relative_fraction=relative_fraction,
            absolute_floor=absolute_floor,
        )
    except ModelDiagnosticsValidationError as exc:
        st.warning(str(exc))
        return None
    if not points:
        variable = [d.dataset_id for d in info.problem.datasets if d.volume_model != "constant"]
        if variable:
            st.warning(
                "Direct raw concentration balance monitoring is not shown for the selected workbook because the relevant dataset(s) are not constant-volume. "
                "For variable-volume/open systems KineticFittingPot must account explicitly for the process boundary before calling the result a mole balance."
            )
        else:
            st.warning("No common observation times contain every species required by this measured invariant.")
        return None

    df = pd.DataFrame([
        {
            "Dataset": p.dataset_id,
            "Time_s": p.time_s,
            "Time_min": p.time_s / 60.0,
            "Balance": p.balance_value,
            "Baseline": p.baseline_value,
            "Deviation": p.normalized_deviation,
            "Deviation_pct": None if p.normalized_deviation is None else 100.0 * p.normalized_deviation,
            "Deviation_sigma_pct": None if p.normalized_deviation_sigma is None else 100.0 * p.normalized_deviation_sigma,
            "Balance_sigma": p.balance_sigma,
        }
        for p in points
    ])

    fig = go.Figure()
    for i, (dataset_id, group) in enumerate(df.groupby("Dataset", sort=False)):
        colour = COLORS[i % len(COLORS)]
        x = group["Time_min"].to_numpy(dtype=float)
        sig = group["Deviation_sigma_pct"].fillna(0.0).to_numpy(dtype=float)
        # ±2 sigma envelope around the stoichiometrically consistent value zero.
        fig.add_trace(go.Scatter(x=x, y=-2.0 * sig, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=x, y=2.0 * sig, mode="lines", line=dict(width=0), fill="tonexty",
            fillcolor=_rgba(colour, 0.08), showlegend=False, hoverinfo="skip",
        ))
        # ±1 sigma envelope.
        fig.add_trace(go.Scatter(x=x, y=-sig, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=x, y=sig, mode="lines", line=dict(width=0), fill="tonexty",
            fillcolor=_rgba(colour, 0.16), showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=x,
            y=group["Deviation_pct"],
            mode="lines+markers",
            name=str(dataset_id),
            line=dict(width=2, color=colour),
            marker=dict(size=7, color=colour),
        ))
    fig.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
    fig.update_layout(
        title="Measured stoichiometric-balance deviation with propagated uncertainty",
        xaxis_title="Time (min)",
        yaxis_title="Normalised balance deviation (%)",
    )
    st.plotly_chart(_dark(fig), use_container_width=True)
    st.caption(
        "Shaded envelopes are propagated measurement-uncertainty bands around perfect stoichiometric consistency: darker = ±1σ, lighter = ±2σ. "
        "For t > t₀, KineticFittingPot propagates uncertainty in B(t) − B(t₀) assuming independent measurement errors. The measured reference balance is used as the normalising scale."
    )

    summary_rows = []
    for dataset_id, group in df.groupby("Dataset", sort=False):
        valid = group.dropna(subset=["Deviation_pct"])
        if valid.empty:
            continue
        later = valid[valid["Time_s"] > float(valid.iloc[0]["Time_s"])].copy()
        sig = later["Deviation_sigma_pct"].to_numpy(dtype=float) if not later.empty else np.asarray([], dtype=float)
        dev = later["Deviation_pct"].to_numpy(dtype=float) if not later.empty else np.asarray([], dtype=float)
        z = np.divide(dev, sig, out=np.full_like(dev, np.nan), where=sig > 0) if len(dev) else np.asarray([], dtype=float)
        outside = int(np.sum(np.abs(dev) > 2.0 * sig)) if len(dev) else 0
        finite_z = np.abs(z[np.isfinite(z)]) if len(z) else np.asarray([], dtype=float)
        max_2sigma = float(np.max(2.0 * sig)) if len(sig) else 0.0
        summary_rows.append({
            "Dataset": dataset_id,
            "Reference time (min)": float(valid.iloc[0]["Time_min"]),
            "Reference balance": float(valid.iloc[0]["Baseline"]),
            "Maximum |deviation| (%)": float(valid["Deviation_pct"].abs().max()),
            "RMS deviation (%)": float(np.sqrt(np.mean(np.square(valid["Deviation_pct"].to_numpy(dtype=float))))),
            "Largest ±2σ band (%)": max_2sigma,
            "Points outside ±2σ": outside,
            "Maximum |deviation|/σ": float(np.max(finite_z)) if len(finite_z) else np.nan,
            "Complete time points": int(len(valid)),
        })
    summary_df = pd.DataFrame(summary_rows)
    if summary_rows:
        show_dataframe(summary_df, use_container_width=True, hide_index=True)

    st.caption(
        "The reference is the earliest time at which every species in the selected invariant is measured. "
        "For the biodiesel A/B/C workbook this is t = 0. The calculation uses raw experimental observations, not fitted trajectories."
    )
    st.info(
        "A point outside an assumed ±2σ envelope is evidence that the selected measurement-error model alone has difficulty explaining the balance error; it is not a classical SPC alarm or proof of missing chemistry. "
        "A sustained trend is often more informative than one excursion. Check units/basis, calibration, sampling, phase loss and process-boundary assumptions before blaming the kinetic law."
    )

    return {
        "label": label,
        "coefficients": coeffs,
        "relative_fraction": relative_fraction,
        "absolute_floor": absolute_floor,
        "balance_dataframe": df,
        "summary_dataframe": summary_df,
    }


def _data_reconciliation(info, context) -> dict | None:
    st.markdown("## Stoichiometric data reconciliation")
    st.markdown(
        "The balance profile tells us that measurements are inconsistent with the selected stoichiometric constraint. "
        "Reconciliation asks a different question: **what is the smallest uncertainty-weighted correction to the measured channels that restores that constraint?**"
    )
    st.latex(r"\min_{\mathbf x}(\mathbf x-\mathbf y)^T\Sigma^{-1}(\mathbf x-\mathbf y)\qquad\text{subject to}\qquad \mathbf l^T\mathbf x=B_0")
    st.caption(
        "Data reconciliation uses a diagonal measurement covariance matrix (independent channel errors) and treats each dataset's earliest complete measured balance as the fixed reference B₀. "
        "The same workbook sigma / assumed uncertainty model used above supplies the weights."
    )

    try:
        rec = reconcile_observations_for_invariant(
            info,
            context["coefficients"],
            assumed_relative_fraction=context["relative_fraction"],
            absolute_floor=context["absolute_floor"],
        )
    except ModelDiagnosticsValidationError as exc:
        st.warning(str(exc))
        return None
    if not rec:
        st.warning("No complete constant-volume observations are available for reconciliation with this invariant.")
        return None

    df = pd.DataFrame([
        {
            "Dataset": r.dataset_id,
            "Time_s": r.time_s,
            "Time_min": r.time_s / 60.0,
            "Species": r.species_id,
            "Measured": r.measured_value,
            "Reconciled": r.reconciled_value,
            "Correction": r.correction,
            "Sigma": r.sigma,
            "Correction_over_sigma": r.standardized_correction,
            "Balance_before": r.balance_before,
            "Balance_after": r.balance_after,
            "Target_balance": r.target_balance,
            "Weighted_inconsistency": r.weighted_inconsistency,
        }
        for r in rec
    ])

    # Global channel ranking: which measured channels carry the largest corrections?
    ranking_rows = []
    for species, group in df.groupby("Species", sort=False):
        corr = group["Correction"].to_numpy(dtype=float)
        z = group["Correction_over_sigma"].to_numpy(dtype=float)
        z = z[np.isfinite(z)]
        ranking_rows.append({
            "Species": species,
            "Mean correction (kmol m⁻³)": float(np.mean(corr)),
            "RMS correction (kmol m⁻³)": float(np.sqrt(np.mean(np.square(corr)))),
            "Maximum |correction| (kmol m⁻³)": float(np.max(np.abs(corr))),
            "RMS |correction|/σ": float(np.sqrt(np.mean(np.square(z)))) if len(z) else np.nan,
            "Maximum |correction|/σ": float(np.max(np.abs(z))) if len(z) else np.nan,
        })
    ranking = pd.DataFrame(ranking_rows).sort_values("Maximum |correction|/σ", ascending=False)
    st.markdown("### Which measurement channels carry the inconsistency?")
    show_dataframe(ranking, use_container_width=True, hide_index=True)

    # Dataset-level weighted inconsistency, counting each time only once.
    time_stats = df[["Dataset", "Time_s", "Time_min", "Weighted_inconsistency"]].drop_duplicates()
    ds_rows = []
    for dataset_id, group in time_stats.groupby("Dataset", sort=False):
        vals = group["Weighted_inconsistency"].dropna().to_numpy(dtype=float)
        ds_rows.append({
            "Dataset": dataset_id,
            "Total weighted correction statistic": float(np.sum(vals)) if len(vals) else np.nan,
            "Largest single-time statistic": float(np.max(vals)) if len(vals) else np.nan,
            "Time points": int(len(group)),
        })
    dataset_summary = pd.DataFrame(ds_rows)
    st.markdown("### Reconciliation summary by dataset")
    show_dataframe(dataset_summary, use_container_width=True, hide_index=True)

    datasets = list(dict.fromkeys(df["Dataset"].astype(str).tolist()))
    selected_dataset = st.selectbox("Dataset to inspect", datasets, index=0, key="diag_reconcile_dataset")
    ddf = df[df["Dataset"].astype(str) == str(selected_dataset)].copy()
    species_options = list(dict.fromkeys(ddf["Species"].astype(str).tolist()))
    selected_species = st.selectbox("Species for raw vs reconciled comparison", species_options, index=0, key="diag_reconcile_species")
    sdf = ddf[ddf["Species"].astype(str) == str(selected_species)].sort_values("Time_min")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sdf["Time_min"], y=sdf["Measured"], mode="lines+markers", name="Measured",
        line=dict(width=2), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=sdf["Time_min"], y=sdf["Reconciled"], mode="lines+markers", name="Reconciled",
        line=dict(width=2, dash="dash"), marker=dict(size=7),
    ))
    fig.update_layout(
        title=f"Dataset {selected_dataset} · {selected_species}: raw versus reconciled",
        xaxis_title="Time (min)",
        yaxis_title="Concentration (kmol m⁻³)",
    )
    st.plotly_chart(_dark(fig), use_container_width=True)

    fig2 = go.Figure()
    for i, (species, group) in enumerate(ddf.groupby("Species", sort=False)):
        group = group.sort_values("Time_min")
        fig2.add_trace(go.Scatter(
            x=group["Time_min"], y=group["Correction_over_sigma"], mode="lines+markers",
            name=str(species), line=dict(width=2, color=COLORS[i % len(COLORS)]),
            marker=dict(size=7, color=COLORS[i % len(COLORS)]),
        ))
    fig2.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
    fig2.add_hline(y=2.0, line_dash="dot", line_color="#9ca3af")
    fig2.add_hline(y=-2.0, line_dash="dot", line_color="#9ca3af")
    fig2.update_layout(
        title=f"Dataset {selected_dataset} · reconciliation correction relative to assumed σ",
        xaxis_title="Time (min)",
        yaxis_title="Correction / σ",
    )
    st.plotly_chart(_dark(fig2), use_container_width=True)

    negative = df[df["Reconciled"] < -1e-12]
    if not negative.empty:
        st.warning(
            f"The unconstrained linear reconciliation produced {len(negative)} negative reconciled concentration value(s). "
            "KineticFittingPot has not clipped them because clipping would break the exact balance constraint. Non-negativity is not enforced by this unconstrained reconciliation calculation; a constrained method would be needed to impose it."
        )

    with st.expander("Show reconciled observation table"):
        display = df[[
            "Dataset", "Time_min", "Species", "Measured", "Reconciled", "Correction", "Sigma",
            "Correction_over_sigma", "Balance_before", "Balance_after", "Target_balance",
        ]].copy()
        show_dataframe(display, use_container_width=True, hide_index=True)

    st.warning(
        "Raw measurements are not replaced or overwritten. Reconciled values are a diagnostic aid. "
        "When reconciled observations are used for fitting, compare their results with fits to the original raw observations. Reconciliation does not overwrite the measured data."
    )
    return {
        "observations": df,
        "species_summary": ranking,
        "dataset_summary": dataset_summary,
    }


def _dynamic_residual_diagnostics(info, raw: bytes, context) -> dict | None:
    st.divider()
    st.markdown("## Dynamic residual diagnostics")
    st.markdown(
        "Stoichiometric consistency challenged the **measurements** without using the rate law. Residual diagnostics now challenge the **fitted dynamic model** by asking whether the differences between fitted and observed values contain systematic structure."
    )
    st.latex(r"e_i(t_j)=y_i^{\mathrm{model}}(t_j)-y_i^{\mathrm{measured}}(t_j)")
    st.caption(
        "KineticFittingPot keeps the same sign convention used by Kinetic Parameter Fitting: **positive residual = fitted model above the measured value**. "
        "A visually convincing fitted trajectory can still leave biased, time-related or species-specific residual patterns."
    )

    if context is not None:
        relative_fraction = float(context["relative_fraction"])
        absolute_floor = float(context["absolute_floor"])
        st.caption(
            "Uncertainty-standardised residuals reuse the measurement-uncertainty assumptions selected in the stoichiometric section above. "
            "Fit-scaled residuals are separate: they reproduce the species scaling used by KineticFittingPot's species-scaled fitting objective and are not statistical standard errors."
        )
    else:
        relative_fraction = 0.03
        absolute_floor = 0.002
        st.caption(
            "No measured stoichiometric invariant supplied uncertainty controls on this workbook, so uncertainty-standardised residuals use the diagnostic defaults 3% relative 1σ plus 0.002 kmol m⁻³ absolute floor."
        )

    try:
        points = residual_diagnostic_points(
            raw,
            info,
            assumed_relative_fraction=relative_fraction,
            absolute_floor=absolute_floor,
        )
    except ModelDiagnosticsValidationError as exc:
        st.warning(str(exc))
        return None
    if not points:
        st.warning("No fitted prediction rows are available for residual diagnostics.")
        return None

    df = pd.DataFrame([
        {
            "Dataset": p.dataset_id,
            "Time_s": p.time_s,
            "Time_min": p.time_s / 60.0,
            "Species": p.species_id,
            "Measured": p.measured_value,
            "Fitted": p.fitted_value,
            "Residual": p.residual_model_minus_measured,
            "Species_scale": p.species_scale,
            "Fit_scaled_residual": p.fit_scaled_residual,
            "Effective_sigma": p.effective_sigma,
            "Uncertainty_standardized_residual": p.uncertainty_standardized_residual,
        }
        for p in points
    ])

    st.markdown("### Residual summary by measured species")
    species_rows = []
    for species, group in df.groupby("Species", sort=False):
        residual = group["Residual"].to_numpy(dtype=float)
        scaled = group["Fit_scaled_residual"].dropna().to_numpy(dtype=float)
        z = group["Uncertainty_standardized_residual"].dropna().to_numpy(dtype=float)
        species_rows.append({
            "Species": species,
            "Observations": int(len(group)),
            "Bias, model − measured (kmol m⁻³)": float(np.mean(residual)),
            "RMSE (kmol m⁻³)": float(np.sqrt(np.mean(np.square(residual)))),
            "MAE (kmol m⁻³)": float(np.mean(np.abs(residual))),
            "Maximum |residual| (kmol m⁻³)": float(np.max(np.abs(residual))),
            "Fit-scaled RMSE": float(np.sqrt(np.mean(np.square(scaled)))) if len(scaled) else np.nan,
            "RMS residual / assumed σ": float(np.sqrt(np.mean(np.square(z)))) if len(z) else np.nan,
        })
    species_summary = pd.DataFrame(species_rows).sort_values("RMSE (kmol m⁻³)", ascending=False)
    show_dataframe(species_summary, use_container_width=True, hide_index=True)

    st.markdown("### Residual summary by experiment")
    dataset_rows = []
    for dataset, group in df.groupby("Dataset", sort=False):
        residual = group["Residual"].to_numpy(dtype=float)
        scaled = group["Fit_scaled_residual"].dropna().to_numpy(dtype=float)
        z = group["Uncertainty_standardized_residual"].dropna().to_numpy(dtype=float)
        dataset_rows.append({
            "Dataset": dataset,
            "Observations": int(len(group)),
            "Bias, model − measured (kmol m⁻³)": float(np.mean(residual)),
            "RMSE (kmol m⁻³)": float(np.sqrt(np.mean(np.square(residual)))),
            "MAE (kmol m⁻³)": float(np.mean(np.abs(residual))),
            "Maximum |residual| (kmol m⁻³)": float(np.max(np.abs(residual))),
            "Fit-scaled RMSE": float(np.sqrt(np.mean(np.square(scaled)))) if len(scaled) else np.nan,
            "RMS residual / assumed σ": float(np.sqrt(np.mean(np.square(z)))) if len(z) else np.nan,
        })
    dataset_summary = pd.DataFrame(dataset_rows)
    show_dataframe(dataset_summary, use_container_width=True, hide_index=True)

    st.markdown("### Residual summary by experiment and species")
    grouped_rows = []
    for (dataset, species), group in df.groupby(["Dataset", "Species"], sort=False):
        residual = group["Residual"].to_numpy(dtype=float)
        scaled = group["Fit_scaled_residual"].dropna().to_numpy(dtype=float)
        grouped_rows.append({
            "Dataset": dataset,
            "Species": species,
            "Observations": int(len(group)),
            "Bias, model − measured (kmol m⁻³)": float(np.mean(residual)),
            "RMSE (kmol m⁻³)": float(np.sqrt(np.mean(np.square(residual)))),
            "MAE (kmol m⁻³)": float(np.mean(np.abs(residual))),
            "Maximum |residual| (kmol m⁻³)": float(np.max(np.abs(residual))),
            "Fit-scaled RMSE": float(np.sqrt(np.mean(np.square(scaled)))) if len(scaled) else np.nan,
        })
    dataset_species_summary = pd.DataFrame(grouped_rows)
    show_dataframe(dataset_species_summary, use_container_width=True, hide_index=True)
    st.caption(
        "This grouped view is often more informative than a single global species statistic: opposite biases in different experiments can cancel when all datasets are pooled."
    )

    datasets = list(dict.fromkeys(df["Dataset"].astype(str).tolist()))
    selected_dataset = st.selectbox(
        "Experiment for residual plots",
        datasets,
        index=0,
        key="diag_residual_dataset",
    )
    ddf = df[df["Dataset"].astype(str) == str(selected_dataset)].copy()

    st.markdown("### Residual versus time")
    fig = go.Figure()
    for i, (species, group) in enumerate(ddf.groupby("Species", sort=False)):
        group = group.sort_values("Time_min")
        colour = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=group["Time_min"],
            y=group["Residual"],
            mode="lines+markers",
            name=str(species),
            line=dict(width=2, color=colour),
            marker=dict(size=7, color=colour),
            customdata=np.column_stack([group["Measured"], group["Fitted"]]),
            hovertemplate=(
                "Time=%{x:.3g} min<br>Residual=%{y:.5g}<br>Measured=%{customdata[0]:.5g}<br>Fitted=%{customdata[1]:.5g}<extra>%{fullData.name}</extra>"
            ),
        ))
    fig.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
    fig.update_layout(
        title=f"Dataset {selected_dataset} · residual versus time",
        xaxis_title="Time (min)",
        yaxis_title="Residual, model − measured (kmol m⁻³)",
    )
    st.plotly_chart(_dark(fig), use_container_width=True)
    st.caption(
        "Look for sustained positive/negative bias, early/late structure or one species behaving differently from the rest. "
        "Connecting residual points is used only to make temporal structure easier to see; it does not imply observations are independent or evenly spaced."
    )

    st.markdown("### Residual versus fitted value")
    fig2 = go.Figure()
    for i, (species, group) in enumerate(ddf.groupby("Species", sort=False)):
        colour = COLORS[i % len(COLORS)]
        fig2.add_trace(go.Scatter(
            x=group["Fitted"],
            y=group["Residual"],
            mode="markers",
            name=str(species),
            marker=dict(size=9, color=colour),
            customdata=np.column_stack([group["Time_min"], group["Measured"]]),
            hovertemplate=(
                "Fitted=%{x:.5g}<br>Residual=%{y:.5g}<br>Time=%{customdata[0]:.3g} min<br>Measured=%{customdata[1]:.5g}<extra>%{fullData.name}</extra>"
            ),
        ))
    fig2.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
    fig2.update_layout(
        title=f"Dataset {selected_dataset} · residual versus fitted value",
        xaxis_title="Fitted concentration (kmol m⁻³)",
        yaxis_title="Residual, model − measured (kmol m⁻³)",
    )
    st.plotly_chart(_dark(fig2), use_container_width=True)
    st.caption(
        "Curvature, a funnel-shaped spread or a species-specific offset can indicate systematic model inadequacy or an inappropriate error model. "
        "KineticFittingPot does not use residual-versus-observed as the primary view because the observed value also appears inside the residual and can induce visual correlation."
    )

    species_options = list(dict.fromkeys(ddf["Species"].astype(str).tolist()))
    selected_species = st.selectbox(
        "Species for distribution / Q–Q / ACF inspection",
        species_options,
        index=0,
        key="diag_residual_species",
    )
    sdf = ddf[ddf["Species"].astype(str) == str(selected_species)].sort_values("Time_s").copy()

    st.markdown("### Residual distribution and Q–Q view")
    residual_values = sdf["Residual"].dropna().to_numpy(dtype=float)
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=residual_values,
        nbinsx=max(5, min(15, int(np.ceil(np.sqrt(max(1, len(residual_values)))) * 2))),
        name=str(selected_species),
    ))
    fig3.add_vline(x=0.0, line_dash="dash", line_color="#ffffff")
    fig3.update_layout(
        title=f"Dataset {selected_dataset} · {selected_species}: residual distribution",
        xaxis_title="Residual, model − measured (kmol m⁻³)",
        yaxis_title="Count",
        showlegend=False,
    )
    st.plotly_chart(_dark(fig3), use_container_width=True)

    if len(residual_values) >= 3:
        ordered = np.sort(residual_values)
        n = len(ordered)
        nd = NormalDist()
        probs = (np.arange(1, n + 1, dtype=float) - 0.5) / n
        theoretical = np.asarray([nd.inv_cdf(float(p)) for p in probs], dtype=float)
        mean = float(np.mean(ordered))
        sd = float(np.std(ordered, ddof=1)) if n > 1 else 0.0
        reference = mean + sd * theoretical
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=theoretical,
            y=ordered,
            mode="markers",
            name="Residuals",
            marker=dict(size=9),
        ))
        fig4.add_trace(go.Scatter(
            x=theoretical,
            y=reference,
            mode="lines",
            name="Normal reference",
            line=dict(dash="dash"),
        ))
        fig4.update_layout(
            title=f"Dataset {selected_dataset} · {selected_species}: Q–Q view",
            xaxis_title="Theoretical standard-normal quantile",
            yaxis_title="Ordered residual (kmol m⁻³)",
        )
        st.plotly_chart(_dark(fig4), use_container_width=True)
    else:
        st.info("At least three residuals are required for a Q–Q view.")
    st.caption(
        "The distribution and Q–Q views are descriptive. Approximate normality is not required for a kinetic model to be useful, but strong skew, heavy tails or isolated points can reveal an unsuitable least-squares error model or problematic measurements."
    )

    st.markdown("### Cross-species residual correlation")
    pivot = ddf.pivot_table(index="Time_s", columns="Species", values="Residual", aggfunc="mean")
    species_corr = list(pivot.columns)
    if len(species_corr) >= 2:
        corr = pivot.corr(min_periods=3)
        counts = pd.DataFrame(index=species_corr, columns=species_corr, dtype=float)
        for a in species_corr:
            for b in species_corr:
                counts.loc[a, b] = int(pivot[[a, b]].dropna().shape[0])
        z = corr.to_numpy(dtype=float)
        text = np.empty(z.shape, dtype=object)
        for i in range(z.shape[0]):
            for j in range(z.shape[1]):
                text[i, j] = "—" if not np.isfinite(z[i, j]) else f"{z[i, j]:.2f}<br>n={int(counts.iloc[i,j])}"
        fig5 = go.Figure(data=go.Heatmap(
            z=z,
            x=species_corr,
            y=species_corr,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu",
            reversescale=True,
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y} vs %{x}<br>r=%{z:.3f}<extra></extra>",
        ))
        fig5.update_layout(
            title=f"Dataset {selected_dataset} · residual cross-correlation at common observation times",
            xaxis_title="Species",
            yaxis_title="Species",
        )
        st.plotly_chart(_dark(fig5), use_container_width=True)
        st.caption(
            "Correlations use only genuinely common observation times within the selected experiment; KineticFittingPot does not interpolate missing residuals. "
            "With short kinetic datasets, correlation estimates can be unstable and should be interpreted as structural clues rather than formal proof."
        )
    else:
        st.info("At least two species with overlapping residual observations are required for cross-correlation.")

    st.markdown("### Residual autocorrelation (only when the sampling grid supports it)")
    regularity = time_grid_regularity(sdf["Time_s"].to_numpy(dtype=float), tolerance_fraction=0.05)
    if bool(regularity["regular"]):
        acf = residual_autocorrelation(residual_values, max_lag=min(10, max(1, len(residual_values) // 2)))
        if acf:
            lag = [row[0] for row in acf]
            rho = [row[1] for row in acf]
            median_dt = float(regularity["median_interval"])
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(x=lag, y=rho, name="ACF"))
            fig6.add_hline(y=0.0, line_color="#ffffff")
            fig6.update_layout(
                title=f"Dataset {selected_dataset} · {selected_species}: residual ACF",
                xaxis_title=f"Lag (sampling interval ≈ {median_dt / 60.0:.3g} min)",
                yaxis_title="Autocorrelation",
                showlegend=False,
            )
            st.plotly_chart(_dark(fig6), use_container_width=True)
            st.caption(
                "This is a descriptive conventional ACF. Serial residual structure can suggest missing dynamics, but formal significance limits are not added because short fitted kinetic series and estimated model parameters complicate the usual white-noise assumptions."
            )
    else:
        intervals = np.asarray(regularity["intervals"], dtype=float)
        interval_text = ", ".join(f"{v/60.0:.3g}" for v in intervals[:12])
        if len(intervals) > 12:
            interval_text += ", …"
        st.info(
            f"ACF not shown for Dataset {selected_dataset} / {selected_species}. {regularity['reason']} "
            f"Observed intervals (min): {interval_text}. KineticFittingPot does not interpolate an irregular sequence simply to manufacture a conventional ACF."
        )

    # A small model-facing interpretation summary, without arbitrary pass/fail thresholds.
    largest_species = species_summary.iloc[0]
    st.info(
        f"The largest species-wise raw RMSE in this workbook is currently **{largest_species['Species']}** "
        f"({float(largest_species['RMSE (kmol m⁻³)']):.4g} kmol m⁻³). This is a descriptive ranking, not proof that the corresponding assay or kinetic equation is wrong. "
        "The strongest interpretation comes when residual structure agrees with independent evidence such as the rate-free stoichiometric-consistency/reconciliation results above."
    )
    return {
        "relative_fraction": relative_fraction,
        "absolute_floor": absolute_floor,
        "points": df,
        "species_summary": species_summary,
        "dataset_summary": dataset_summary,
        "dataset_species_summary": dataset_species_summary,
    }


def _local_parameter_jacobian_diagnostics(info) -> dict | None:
    st.markdown("## Local parameter / Jacobian diagnostics")
    st.markdown(
        "These diagnostics examine the fitted objective **locally around the optimum**. KineticFittingPot perturbs each fitted parameter, "
        "re-evaluates the full dynamic model, and forms the Jacobian of the same residual vector used during fitting. "
        "They are useful for detecting weak local directions and parameter trade-offs, but they do not replace profile-likelihood analysis."
    )

    try:
        result = local_parameter_diagnostics(info)
    except (ModelDiagnosticsValidationError, FittingValidationError, ModelValidationError, RuntimeError) as exc:
        st.warning(f"Local parameter diagnostics are unavailable: {exc}")
        return None
    except Exception as exc:
        st.warning(f"Unexpected local parameter diagnostic error: {exc}")
        return None

    p = len(result.parameter_ids)
    n = len(result.weighted_residuals)
    off_diag = []
    for i in range(p):
        for j in range(i + 1, p):
            value = float(result.correlation[i, j])
            if np.isfinite(value):
                off_diag.append((abs(value), value, result.parameter_ids[i], result.parameter_ids[j]))
    off_diag.sort(reverse=True)
    pair_table = pd.DataFrame([
        {"Parameter 1": a, "Parameter 2": b, "Correlation": signed, "|Correlation|": absolute}
        for absolute, signed, a, b in off_diag
    ])
    max_abs_corr = off_diag[0][0] if off_diag else np.nan
    max_pair = f"{off_diag[0][2]} ↔ {off_diag[0][3]}" if off_diag else "—"

    cols = st.columns(5)
    cards = [
        ("Jacobian size", f"{n} × {p}", "observations × fitted parameters"),
        ("Local rank", f"{result.numerical_rank}/{p}", "relative-parameter Jacobian"),
        ("Relative condition no.", f"{result.condition_number:.3g}" if np.isfinite(result.condition_number) else "∞", "scaled local geometry"),
        ("Largest |correlation|", f"{max_abs_corr:.3f}" if np.isfinite(max_abs_corr) else "—", max_pair),
        ("Residual dof", str(result.degrees_of_freedom), f"weighting: {result.weighting}"),
    ]
    for col, card in zip(cols, cards):
        with col:
            metric_card(*card, compact=True)

    st.caption(
        "The raw Jacobian depends on parameter units. For singular values and conditioning, KineticFittingPot scales each parameter by its fitted magnitude "
        "(or by 1% of its bound span when the fitted value is effectively zero). The resulting condition number therefore describes local sensitivity to relative parameter movements, not an invariant universal property of the model."
    )

    rows = []
    for item in result.parameter_rows:
        rows.append({
            "Parameter": item.parameter_id,
            "Fitted value": item.fitted_value,
            "Bound position (%)": item.bound_position_percent,
            "Nearest bound / local scale (%)": item.nearest_bound_distance_percent,
            "FD method": item.finite_difference_method,
            "FD step": item.finite_difference_step,
            "RMS effect of 1% local change": item.one_percent_effect_rms,
            "Approx. local SE": item.approximate_standard_error,
            "Approx. relative SE (%)": item.relative_standard_error_percent,
            "Strongest partner": item.strongest_correlation_parameter or "—",
            "Strongest correlation": item.strongest_correlation,
        })
    pdf = pd.DataFrame(rows)
    st.markdown("### Parameter-level local diagnostics")
    show_dataframe(
        pdf,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fitted value": st.column_config.NumberColumn(format="%.6g"),
            "Bound position (%)": st.column_config.NumberColumn(format="%.2f"),
            "Nearest bound / local scale (%)": st.column_config.NumberColumn(format="%.2f"),
            "FD step": st.column_config.NumberColumn(format="%.3e"),
            "RMS effect of 1% local change": st.column_config.NumberColumn(format="%.4g"),
            "Approx. local SE": st.column_config.NumberColumn(format="%.4g"),
            "Approx. relative SE (%)": st.column_config.NumberColumn(format="%.2f"),
            "Strongest correlation": st.column_config.NumberColumn(format="%.3f"),
        },
    )
    st.caption(
        "`Bound position (%)` is the linear position between the workbook bounds; very broad kinetic bounds can make a perfectly interior positive rate constant look numerically close to the lower end of that span. "
        "`Nearest bound / local scale (%)` instead compares the actual distance to the nearest bound with the local parameter scale used in the Jacobian analysis. "
        "The reported local standard errors come from the linearised least-squares objective, using the completed fit's residual weighting. "
        "For species-scaled fitting they are **objective-based approximations**, not measurement-error confidence intervals. A profile analysis is required before treating parameter uncertainty as strongly nonlinear or one-sided."
    )

    # Relative sensitivity magnitude -------------------------------------------------
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=[r.parameter_id for r in result.parameter_rows],
        y=[r.one_percent_effect_rms for r in result.parameter_rows],
        name="Local sensitivity",
    ))
    fig1.update_layout(
        title="Local parameter sensitivity",
        xaxis_title="Fitted parameter",
        yaxis_title="RMS weighted-residual change for a 1% local parameter change",
        showlegend=False,
    )
    st.plotly_chart(_dark(fig1), use_container_width=True)
    st.caption(
        "This comparison is based on relative/local parameter movements, so parameters with different numerical units can be compared more sensibly. "
        "A small bar means the fitted objective is locally less responsive to that parameter when all other parameters are held fixed; it does not by itself prove non-identifiability."
    )

    # Singular values ---------------------------------------------------------------
    singular = np.asarray(result.singular_values, dtype=float)
    fig2 = go.Figure()
    if len(singular):
        normalised = singular / singular[0] if singular[0] > 0 else singular
        fig2.add_trace(go.Scatter(
            x=np.arange(1, len(singular) + 1),
            y=normalised,
            mode="lines+markers",
            name="σᵢ / σ₁",
        ))
        fig2.update_yaxes(type="log")
    fig2.update_layout(
        title="Singular-value spectrum of the relative-parameter Jacobian",
        xaxis_title="Singular direction",
        yaxis_title="Normalised singular value (log scale)",
        showlegend=False,
    )
    st.plotly_chart(_dark(fig2), use_container_width=True)
    st.caption(
        "A very small final singular value means that at least one local combination of parameters changes the residual vector only weakly. "
        "The ratio of the largest to smallest retained singular value is the displayed relative condition number."
    )

    # Correlation heatmap ------------------------------------------------------------
    st.markdown("### Approximate local parameter correlation")
    corr = np.asarray(result.correlation, dtype=float)
    text = np.empty(corr.shape, dtype=object)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            text[i, j] = "—" if not np.isfinite(corr[i, j]) else f"{corr[i,j]:.2f}"
    fig3 = go.Figure(data=go.Heatmap(
        z=corr,
        x=list(result.parameter_ids),
        y=list(result.parameter_ids),
        zmin=-1,
        zmax=1,
        zmid=0,
        colorscale="RdBu",
        reversescale=True,
        text=text,
        texttemplate="%{text}",
        hovertemplate="%{y} vs %{x}<br>ρ=%{z:.4f}<extra></extra>",
    ))
    fig3.update_layout(
        title="Local parameter-correlation matrix",
        xaxis_title="Parameter",
        yaxis_title="Parameter",
    )
    st.plotly_chart(_dark(fig3), use_container_width=True)
    st.caption(
        "Large |correlation| means the local uncertainty geometry allows the corresponding fitted parameters to move together strongly while retaining a similar fit. "
        "Correlation is not causation and does not prove that either parameter should be removed."
    )

    if off_diag:
        show_dataframe(
            pair_table.head(min(10, len(pair_table))),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Correlation": st.column_config.NumberColumn(format="%.3f"),
                "|Correlation|": st.column_config.NumberColumn(format="%.3f"),
            },
        )

    # Weakest local direction --------------------------------------------------------
    weakest = np.asarray(result.weakest_direction, dtype=float)
    if len(weakest) == p and np.all(np.isfinite(weakest)):
        st.markdown("### Weakest local parameter combination")
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=list(result.parameter_ids), y=weakest, name="Weakest direction"))
        fig4.add_hline(y=0.0, line_color="#ffffff")
        fig4.update_layout(
            title="Parameter combination associated with the smallest singular value",
            xaxis_title="Parameter",
            yaxis_title="Relative-direction coefficient (largest magnitude = 1)",
            showlegend=False,
        )
        st.plotly_chart(_dark(fig4), use_container_width=True)
        st.caption(
            "This vector is expressed in the same local relative-parameter scaling used for the singular-value analysis. Its overall sign is arbitrary. "
            "It identifies the local parameter combination to which the fitted residuals are least sensitive; profile likelihood will test whether that weak direction remains weak away from the optimum."
        )

    # Practical alerts without pretending they are hard statistical tests.
    near_bound = [r.parameter_id for r in result.parameter_rows if r.nearest_bound_distance_percent <= 1.0]
    strong_pairs = [(a, b, signed) for absolute, signed, a, b in off_diag if absolute >= 0.8]
    messages = []
    if result.numerical_rank < p:
        messages.append(f"The local relative-parameter Jacobian is numerically rank deficient ({result.numerical_rank}/{p}).")
    if near_bound:
        messages.append("Parameter(s) within 1% of one local parameter scale from a fitted bound: " + ", ".join(near_bound) + ".")
    if strong_pairs:
        formatted = ", ".join(f"{a}↔{b} ({rho:+.2f})" for a, b, rho in strong_pairs[:6])
        messages.append("Strong local parameter correlations (|ρ| ≥ 0.8): " + formatted + ".")
    if messages:
        st.warning(" ".join(messages) + " These are diagnostic flags rather than automatic model-selection rules.")
    else:
        st.success(
            "No numerical rank loss, near-bound fitted parameter, or |ρ| ≥ 0.8 parameter pair was detected by the local diagnostics. "
            "This is reassuring locally, but profile likelihood is still required to test nonlinear practical identifiability."
        )
    return {"result": result, "parameter_table": pdf, "pair_table": pair_table}


def _profiled_objective_diagnostics(info, raw: bytes) -> dict | None:
    st.markdown("## Profiled objective / profile-likelihood diagnostics")
    st.markdown(
        "Local Jacobian diagnostics only describe the immediate neighbourhood of the fitted optimum. "
        "A profile fixes one fitted parameter at a sequence of values and **re-optimises every other fitted parameter** at each point. "
        "This shows how much fit quality is genuinely lost when that parameter is forced away from its optimum."
    )
    st.caption(
        "KineticFittingPot reports a **profiled least-squares objective**. It can be interpreted as a profile likelihood only when the residual weighting corresponds to an appropriate probabilistic measurement-error model. "
        "For species-scaled fits, use the profile primarily as a practical-identifiability and model-structure diagnostic rather than as a formal confidence interval."
    )

    all_ids = list(info.problem.fit_parameter_ids)
    if not all_ids:
        st.warning("No fitted parameters are available for profiling.")
        return None

    inferred_reverse = [pid for pid in all_ids if str(pid).strip().lower().endswith("r")]
    c1, c2 = st.columns([2, 1])
    with c1:
        selected = st.multiselect(
            "Parameters to profile",
            options=all_ids,
            default=inferred_reverse if inferred_reverse else all_ids,
            key="diag_profile_parameters",
            help="Each selected parameter is fixed across a grid while all remaining fitted parameters are re-optimised.",
        )
    with c2:
        zero_selected = st.multiselect(
            "Explicit k = 0 boundary tests",
            options=all_ids,
            default=inferred_reverse,
            key="diag_profile_zero_parameters",
            help="Useful for testing whether a non-negative kinetic term is actually required. The fixed parameter is allowed to be exactly zero even when the original fit used a small positive numerical lower bound.",
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        grid_points = st.number_input(
            "Profile grid points / parameter",
            min_value=5,
            max_value=21,
            value=7,
            step=2,
            key="diag_profile_grid_points",
        )
    with c4:
        span_factor = st.number_input(
            "Multiplicative profile span",
            min_value=2.0,
            max_value=100.0,
            value=10.0,
            step=2.0,
            key="diag_profile_span_factor",
            help="For positive kinetic parameters, the ordinary profile grid extends approximately from fitted/factor to fitted×factor, clipped to the original workbook bounds.",
        )
    with c5:
        max_nfev = st.number_input(
            "Max re-optimisation evaluations / point",
            min_value=40,
            max_value=500,
            value=80,
            step=20,
            key="diag_profile_max_nfev",
        )

    st.caption(
        "Reverse-rate parameters are selected by default when their IDs end in `r`; select additional fitted parameters whenever a full profile review is wanted. Profile points are solved outward from the fitted optimum and warm-started from the nearest successful constrained solution. "
        "The ordinary grid respects the original parameter bounds; selected zero-rate tests are shown separately as model-structure boundary points."
    )

    raw_hash = hashlib.sha256(raw).hexdigest()
    config = (
        raw_hash,
        tuple(selected),
        tuple(zero_selected),
        int(grid_points),
        float(span_factor),
        int(max_nfev),
    )
    state_key = "reactionpot_profile_diagnostics_result"
    config_key = "reactionpot_profile_diagnostics_config"

    run = st.button(
        "Run parameter profiles",
        type="primary",
        disabled=not bool(selected),
        key="diag_run_profiles",
    )
    if run:
        try:
            with st.spinner("Profiling parameters and re-optimising the remaining model parameters …"):
                result = profiled_objective_diagnostics(
                    info,
                    parameter_ids=tuple(selected),
                    grid_points=int(grid_points),
                    span_factor=float(span_factor),
                    max_nfev=int(max_nfev),
                    zero_boundary_parameter_ids=tuple(zero_selected),
                )
            st.session_state[state_key] = result
            st.session_state[config_key] = config
        except (ModelDiagnosticsValidationError, FittingValidationError, ModelValidationError, RuntimeError) as exc:
            st.warning(f"Profile diagnostics are unavailable: {exc}")
            return None
        except Exception as exc:
            st.warning(f"Unexpected profile diagnostic error: {exc}")
            return None

    result = st.session_state.get(state_key)
    stored_config = st.session_state.get(config_key)
    if result is None or not stored_config or stored_config[0] != raw_hash:
        st.info("Run the profiles when you are ready. This is intentionally not calculated automatically because every profile point requires repeated dynamic simulation and re-optimisation.")
        return None
    if stored_config != config:
        st.info("The profile controls have changed since the displayed result was calculated. Press **Run parameter profiles** to refresh the profiles. The diagnostics export will record the settings that produced the stored profile result.")

    st.markdown("### Profile summary")
    cards = st.columns(4)
    with cards[0]:
        metric_card("Baseline objective", f"{result.base_objective_sse:.6g}", f"weighting: {result.weighting}", compact=True)
    with cards[1]:
        metric_card("Baseline weighted RMSE", f"{result.base_weighted_rmse:.5g}", "same objective scale", compact=True)
    with cards[2]:
        metric_card("Parameters profiled", str(len(result.profiles)), "constrained re-optimisation", compact=True)
    with cards[3]:
        zero_count = sum(p.zero_boundary_point is not None for p in result.profiles)
        metric_card("Zero-boundary tests", str(zero_count), "explicit fixed k = 0", compact=True)

    if result.improved_solution_found:
        st.warning(
            "At least one constrained profile point produced an objective lower than the stored completed-fit optimum. "
            "That suggests the original fit may not be fully converged or may have missed a better basin; rerun the kinetic fit before interpreting profile widths quantitatively."
        )

    # Zero-boundary model-structure summary -----------------------------------------
    zero_rows = []
    for profile in result.profiles:
        zp = profile.zero_boundary_point
        if zp is None:
            continue
        zero_rows.append({
            "Parameter": profile.parameter_id,
            "Fitted value": profile.fitted_value,
            "Objective at k=0": zp.objective_sse,
            "Δ objective": zp.delta_sse,
            "Relative objective increase (%)": zp.relative_increase_percent,
            "Weighted RMSE at k=0": zp.weighted_rmse,
            "Optimiser success": zp.success,
            "nfev": zp.nfev,
        })
    if zero_rows:
        st.markdown("### Explicit zero-rate boundary tests")
        show_dataframe(
            pd.DataFrame(zero_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Fitted value": st.column_config.NumberColumn(format="%.6g"),
                "Objective at k=0": st.column_config.NumberColumn(format="%.6g"),
                "Δ objective": st.column_config.NumberColumn(format="%.6g"),
                "Relative objective increase (%)": st.column_config.NumberColumn(format="%.2f"),
                "Weighted RMSE at k=0": st.column_config.NumberColumn(format="%.5g"),
            },
        )
        st.caption(
            "A small deterioration at k = 0 means the data can be represented almost as well without that kinetic term. A large deterioration provides stronger evidence that the term is required over the experimental domain. "
            "This supports or challenges the **model term**; it does not prove or disprove an elementary molecular mechanism."
        )

    # Individual profiles -----------------------------------------------------------
    st.markdown("### Individual parameter profiles")
    profile_lookup = {p.parameter_id: p for p in result.profiles}
    display_pid = st.selectbox(
        "Profile to inspect",
        options=list(profile_lookup),
        index=0,
        key="diag_profile_display_parameter",
    )
    profile = profile_lookup[display_pid]
    rows = []
    for point in profile.points:
        rows.append({
            "Fixed value": point.fixed_value,
            "Value / fitted": (point.fixed_value / profile.fitted_value) if profile.fitted_value != 0 else np.nan,
            "Objective": point.objective_sse,
            "Δ objective": point.delta_sse,
            "Relative increase (%)": point.relative_increase_percent,
            "Weighted RMSE": point.weighted_rmse,
            "Success": point.success,
            "nfev": point.nfev,
        })
    pdf = pd.DataFrame(rows).sort_values("Fixed value")

    fig = go.Figure()
    if profile.fitted_value > 0 and np.all(pdf["Fixed value"].to_numpy(dtype=float) > 0):
        x = pdf["Value / fitted"]
        x_title = f"Fixed {display_pid} / fitted {display_pid}"
        fig.update_xaxes(type="log")
    else:
        x = pdf["Fixed value"]
        x_title = f"Fixed {display_pid}"
    fig.add_trace(go.Scatter(
        x=x,
        y=pdf["Relative increase (%)"],
        mode="lines+markers",
        name="Profiled objective",
        marker=dict(size=8),
        line=dict(width=2),
    ))
    fig.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
    if profile.zero_boundary_point is not None:
        zp = profile.zero_boundary_point
        # Zero cannot be placed on a log x-axis; show its objective as a labelled horizontal marker/callout.
        fig.add_annotation(
            x=0.02 if profile.fitted_value > 0 else 0.0,
            y=zp.relative_increase_percent,
            text=f"k=0: +{zp.relative_increase_percent:.1f}%",
            showarrow=True,
            arrowhead=2,
            xref="paper" if profile.fitted_value > 0 else "x",
            yref="y",
        )
    fig.update_layout(
        title=f"Profiled objective — {display_pid}",
        xaxis_title=x_title,
        yaxis_title="Objective increase relative to completed optimum (%)",
        showlegend=False,
    )
    st.plotly_chart(_dark(fig), use_container_width=True)
    st.caption(
        "A narrow, steep profile means the data constrain the parameter strongly after allowing every other fitted parameter to compensate. "
        "A broad or flat profile indicates practical non-identifiability or strong compensating parameter trade-offs. The selected profile span is a computational window, not a confidence interval."
    )

    show_dataframe(
        pdf,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fixed value": st.column_config.NumberColumn(format="%.6g"),
            "Value / fitted": st.column_config.NumberColumn(format="%.4g"),
            "Objective": st.column_config.NumberColumn(format="%.6g"),
            "Δ objective": st.column_config.NumberColumn(format="%.6g"),
            "Relative increase (%)": st.column_config.NumberColumn(format="%.2f"),
            "Weighted RMSE": st.column_config.NumberColumn(format="%.5g"),
        },
    )

    # Compact all-parameter comparison on a normalised x-axis -----------------------
    if len(result.profiles) > 1:
        st.markdown("### Normalised comparison of profile shapes")
        fig2 = go.Figure()
        for profile_item in result.profiles:
            vals = np.asarray([p.fixed_value for p in profile_item.points], dtype=float)
            y = np.asarray([p.relative_increase_percent for p in profile_item.points], dtype=float)
            if profile_item.fitted_value > 0 and np.all(vals > 0):
                xvals = vals / profile_item.fitted_value
            else:
                span = max(profile_item.upper_bound - profile_item.lower_bound, 1e-15)
                xvals = (vals - profile_item.fitted_value) / span + 1.0
            fig2.add_trace(go.Scatter(x=xvals, y=y, mode="lines+markers", name=profile_item.parameter_id))
        fig2.add_hline(y=0.0, line_dash="dash", line_color="#ffffff")
        if all(p.fitted_value > 0 and all(pt.fixed_value > 0 for pt in p.points) for p in result.profiles):
            fig2.update_xaxes(type="log")
            xlab = "Fixed parameter / fitted parameter"
        else:
            xlab = "Normalised displacement from fitted parameter"
        fig2.update_layout(
            title="Profiled-objective comparison",
            xaxis_title=xlab,
            yaxis_title="Objective increase relative to completed optimum (%)",
        )
        st.plotly_chart(_dark(fig2), use_container_width=True)
        st.caption(
            "This overlay compares practical profile steepness on a normalised parameter axis. It is descriptive only: parameters may have different physical units, bounds and nonlinear geometry."
        )

    _, stored_selected, stored_zero, stored_grid, stored_span, stored_nfev = stored_config
    return {
        "result": result,
        "selected_parameters": tuple(stored_selected),
        "zero_parameters": tuple(stored_zero),
        "grid_points": int(stored_grid),
        "span_factor": float(stored_span),
        "max_nfev": int(stored_nfev),
        "controls_match": stored_config == config,
    }


def render() -> None:
    workspace_header(
        "Advanced Model Diagnostics",
        "Upload a completed KineticFittingPot kinetic-fitting workbook and challenge the data/model after fitting: rate-free stoichiometric consistency, residual behaviour, local parameter geometry and nonlinear profiled-objective identifiability.",
        section="Model Diagnostics",
        accent=ACCENT,
    )
    chips([
        ("Completed fit upload", "blue"),
        ("Stoichiometric invariants", ""),
        ("Integer conserved totals", "blue"),
        ("Measurement uncertainty", "warn"),
        ("Data reconciliation", ""),
        ("Residual diagnostics", "blue"),
        ("Local Jacobian", ""),
        ("Parameter correlation", "warn"),
        ("Profiled objective", "blue"),
        ("k = 0 tests", "warn"),
    ])

    st.markdown("## Load completed kinetic-fitting workbook")
    uploaded = st.file_uploader(
        "Upload KineticFittingPot kinetic-fitting results workbook (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=False,
        help="Use the workbook downloaded after a successful KineticFittingPot kinetic fit. It must contain the original model/data sheets plus Fit_Parameters, Fit_Predictions, Fit_Residuals and Fit_Summary.",
    )
    if uploaded is None:
        st.caption("Start with the completed workbook downloaded from Kinetic Parameter Fitting.")
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Model Diagnostics Fundamentals"):
                navigate("Model Diagnostics Fundamentals")
        with c2:
            if st.button("Open Kinetic Parameter Fitting →"):
                navigate("Kinetic Parameter Fitting")
        return

    raw = uploaded.getvalue()
    try:
        info = parse_completed_fit_workbook(raw)
        diag = stoichiometric_diagnostics(info)
    except (ModelDiagnosticsValidationError, FittingValidationError, ModelValidationError, RuntimeError) as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Unexpected post-fit workbook validation error: {exc}")
        return

    st.success(f"Completed fit recognised: {info.summary.get('Model', info.problem.model.model_name)}")
    _summary_cards(info, diag)

    st.markdown("## Stoichiometric structure recovered from the workbook")
    st.markdown(
        "The balance diagnostics are generated from the fitted workbook's **stoichiometric matrix S**. "
        "The rate expressions and fitted parameter values are not needed to derive these constraints."
    )
    _stoichiometric_matrix(info)

    st.markdown("## Independent closed-batch mole-balance constraints")
    st.markdown(
        r"KineticFittingPot finds the complete left-null space: every displayed vector $\mathbf l$ satisfies "
        r"$\mathbf l^T\mathbf S=0$, so $\mathbf l^T\mathbf n$ is invariant for the assumed closed reaction network."
    )
    _constraint_table(info, diag)
    integer_artifact = _simple_integer_constraint_table(info)
    _measured_constraint_table(info, diag)
    context = _consistency_monitor(info, diag)
    reconciliation_artifact = _data_reconciliation(info, context) if context is not None else None
    residual_artifact = _dynamic_residual_diagnostics(info, raw, context)
    local_artifact = _local_parameter_jacobian_diagnostics(info)
    profile_artifact = _profiled_objective_diagnostics(info, raw)

    st.divider()
    st.markdown("## Save model diagnostics")
    st.markdown(
        "Download the **completed fitting workbook plus the full diagnostic record calculated above**. "
        "The original model/data and `Fit_*` sheets are preserved and KineticFittingPot appends `Diag_*` sheets containing the stoichiometric checks, uncertainty assumptions, reconciliation, residual summaries, local Jacobian geometry and — when run — profiled-objective results."
    )
    try:
        diagnostic_workbook = build_model_diagnostics_workbook(
            raw,
            info,
            diag,
            integer_artifact=integer_artifact,
            balance_artifact=context,
            reconciliation_artifact=reconciliation_artifact,
            residual_artifact=residual_artifact,
            local_artifact=local_artifact,
            profile_artifact=profile_artifact,
            reactionpot_version="KineticFittingPot v1.57",
        )
        source_name = getattr(uploaded, "name", "completed_fit.xlsx")
        stem = source_name[:-5] if source_name.lower().endswith(".xlsx") else source_name
        st.download_button(
            "Download completed model-diagnostics workbook",
            data=diagnostic_workbook,
            file_name=f"{stem}_model_diagnostics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_model_diagnostics_workbook",
        )
        if profile_artifact is None:
            st.caption(
                "Parameter-profile sheets are marked as not included because profiles have not been run for this uploaded workbook. Run the profiles first and then download again to capture the profile points, zero-boundary tests and re-optimised parameter values."
            )
        else:
            st.caption(
                "The export includes the stored parameter-profile run, its exact profile settings, every constrained objective point, zero-boundary tests and the re-optimised values of the remaining fitted parameters."
            )
    except Exception as exc:
        st.warning(f"KineticFittingPot could not create the model-diagnostics workbook: {exc}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Model Diagnostics Fundamentals", key="postfit_to_fund"):
            navigate("Model Diagnostics Fundamentals")
    with c2:
        if st.button("Open Kinetic Parameter Fitting →", key="postfit_to_fit"):
            navigate("Kinetic Parameter Fitting")
