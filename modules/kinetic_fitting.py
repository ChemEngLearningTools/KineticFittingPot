from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.kinetic_fitting_engine import (
    FittingValidationError,
    FittingBudget,
    FittingBudgetExceeded,
    build_fitting_results_workbook,
    fit_multistart,
    evaluate_validation,
    fitted_trajectory,
    parse_fitting_workbook,
    problem_with_fit_parameters,
    synthetic_truth,
)
from utils.general_batch_model import ModelValidationError
from utils.deployment import (is_public_cloud, PUBLIC_FITTING_LIMITS, public_cloud_workbook_violations,
                              public_fitting_violations, public_fitting_limits_markdown)
from utils.ui import chips, metric_card, navigate, workspace_header, teaching_table, show_dataframe
from utils.public_fit_worker import run_public_fit, PublicFitBusy, PublicFitTimeout, PublicFitStopped


ACCENT = "#f59e0b"
EXAMPLE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "templates"
    / "KineticFittingPot_Kinetic_Fitting_Catalytic_Saturation_Synthetic_Data.xlsx"
)
COLORS = ["#19D3F3", "#AB63FA", "#EF553B", "#00CC96", "#FFA15A", "#636EFA", "#FF6692"]


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


def _center_numeric(df: pd.DataFrame):
    """Align numeric columns without changing underlying values or table schemas."""
    return df  # show_dataframe handles numeric alignment without changing the data


def _preview(problem) -> None:
    st.markdown("### Model and fitting data recognised")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Fit datasets", str(len(problem.datasets)), f"{len(problem.validation_datasets)} held out for validation", compact=True)
    with c2: metric_card("Observations", str(len(problem.observations)), "actual measured rows", compact=True)
    with c3: metric_card("Species", str(len(problem.model.species_ids)), ", ".join(problem.model.species_ids), compact=True)
    with c4: metric_card("Fit candidates", str(len(problem.fit_parameter_ids)), ", ".join(problem.fit_parameter_ids), compact=True)

    ds_df = pd.DataFrame([
        {
            "Dataset": d.dataset_id,
            "Description": d.description,
            "Purpose": "Fit" if d.dataset_id in {x.dataset_id for x in problem.datasets} else "Validation",
            "Volume (m³)": d.volume_m3,
            "Volume model": d.volume_model,
            **{f"c0_{sid}": float(v) for sid, v in zip(problem.model.species_ids, d.initial_concentration_kmol_m3)},
        }
        for d in (*problem.datasets, *problem.validation_datasets)
    ])
    st.markdown("### Dataset-specific initial conditions")
    show_dataframe(_center_numeric(ds_df), use_container_width=True, hide_index=True)

    obs_df = pd.DataFrame([
        {"Dataset": o.dataset_id, "Time (s)": o.time_s, "Species": o.species_id, "Measured": o.measured_value}
        for o in (*problem.observations, *problem.validation_observations)
    ])
    summary = obs_df.groupby(["Dataset", "Species"], as_index=False).agg(
        observations=("Measured", "size"), first_time_s=("Time (s)", "min"), last_time_s=("Time (s)", "max")
    )
    st.markdown("### Observation coverage")
    teaching_table(
        ["Dataset", "Species", "Observations", "First time (s)", "Last time (s)"],
        [[r.Dataset, r.Species, str(int(r.observations)), f"{r.first_time_s:g}", f"{r.last_time_s:g}"]
         for r in summary.itertuples(index=False)],
        alignments=["center", "center", "center", "center", "center"],
    )
    st.caption("Fit datasets determine the estimated parameters. Validation datasets are held out of the objective and evaluated after fitting. Missing measurements are absent rows.")


def _parameter_table(problem, selected: list[str]) -> pd.DataFrame:
    rows = []
    for pid in problem.model.parameter_ids:
        idx = problem.model.parameter_ids.index(pid)
        rows.append({
            "Parameter": pid,
            "Workbook value / start": float(problem.model.parameter_values[idx]),
            "Fit now?": pid in selected,
            "Lower bound": problem.model.lower_bounds[idx],
            "Upper bound": problem.model.upper_bounds[idx],
            "Units": problem.model.parameter_units[idx],
        })
    return pd.DataFrame(rows)


def _fit_parameter_results(problem, fit_result: dict, truth: dict[str, float]) -> pd.DataFrame:
    rows = []
    for j, pid in enumerate(problem.fit_parameter_ids):
        row = {
            "Parameter": pid,
            "Starting estimate": float(problem.starting_values[j]),
            "Fitted value": float(fit_result["best_values"][j]),
            "Lower bound": float(problem.lower_bounds[j]),
            "Upper bound": float(problem.upper_bounds[j]),
        }
        if pid in truth:
            row["Synthetic truth"] = truth[pid]
            row["Error vs truth (%)"] = 100.0 * (row["Fitted value"] - truth[pid]) / truth[pid]
        rows.append(row)
    return pd.DataFrame(rows)


def _starts_dataframe(problem, fit_result: dict) -> pd.DataFrame:
    rows = []
    for r in fit_result["records"]:
        row = {
            "Start": r["start"], "Success": r["success"], "SSE": r["sse"],
            "Weighted RMSE": r["weighted_rmse"], "Raw RMSE (kmol m⁻³)": r["raw_rmse_kmol_m3"], "nfev": r["nfev"],
        }
        for pid, value in zip(problem.fit_parameter_ids, r["parameter_values"]):
            row[pid] = value
        rows.append(row)
    return pd.DataFrame(rows).sort_values("SSE", kind="stable").reset_index(drop=True)


def _trajectory_plots(problem, fit_result: dict) -> None:
    st.markdown("### Fitted and independent validation trajectories")
    best = fit_result["best_values"]
    observations = pd.DataFrame([
        {"Dataset": o.dataset_id, "Time_s": o.time_s, "Species": o.species_id, "Measured": o.measured_value}
        for o in (*problem.observations, *problem.validation_observations)
    ])
    measured_species = [sid for sid in problem.model.species_ids if sid in set(observations["Species"])]
    color_map = {sid: COLORS[i % len(COLORS)] for i, sid in enumerate(problem.model.species_ids)}

    for dataset in (*problem.datasets, *problem.validation_datasets):
        is_validation = dataset.dataset_id in {d.dataset_id for d in problem.validation_datasets}
        traj = fitted_trajectory(problem, dataset, best, points=500)
        fig = go.Figure()
        for sid in measured_species:
            sidx = problem.model.species_ids.index(sid)
            fig.add_trace(go.Scatter(
                x=traj["time_s"] / 60.0, y=traj["concentrations_kmol_m3"][:, sidx],
                mode="lines", name=f"{sid} {'validation prediction' if is_validation else 'fitted'}",
                line=dict(color=color_map[sid], width=2.2, dash="dash" if is_validation else "solid"),
            ))
            subset = observations[(observations["Dataset"] == dataset.dataset_id) & (observations["Species"] == sid)]
            if not subset.empty:
                fig.add_trace(go.Scatter(
                    x=subset["Time_s"] / 60.0, y=subset["Measured"], mode="markers", name=f"{sid} {'validation data' if is_validation else 'fit data'}",
                    marker=dict(color=color_map[sid], size=8, symbol="diamond-open" if is_validation else "circle-open", line=dict(width=2)),
                ))
        if not is_validation:
            # Restore the original v1.19 fitting-figure layout exactly.
            # These figures already displayed correctly before the validation change.
            fig.update_layout(
                title=f"{dataset.dataset_id} — {dataset.description} (FITTING)",
                xaxis_title="Time (min)",
                yaxis_title="Concentration (kmol m⁻³)",
            )
            st.plotly_chart(_dark(fig), use_container_width=True)
        else:
            # Only validation figures need special treatment for long labels.
            # Render the dataset heading outside Plotly; compact margins keep
            # the actual trajectories at their former visual scale.
            st.markdown(
                f"**{dataset.dataset_id} — {dataset.description} "
                f"(VALIDATION — not fitted)**"
            )
            fig.update_layout(
                title=dict(text=""),
                xaxis_title="Time (min)",
                yaxis_title="Concentration (kmol m⁻³)",
            )
            _dark(fig)
            # A modest allowance for two rows of legend entries. Unlike v1.20/21,
            # do not reserve a 155px blank band above the data.
            fig.update_layout(margin=dict(l=25, r=25, t=90, b=35))
            st.plotly_chart(fig, use_container_width=True)


def _residual_plot(problem, fit_result: dict) -> None:
    st.markdown("### Fitting residual diagnostics")
    fig = go.Figure()
    color_map = {sid: COLORS[i % len(COLORS)] for i, sid in enumerate(problem.model.species_ids)}
    for sid in problem.model.species_ids:
        xs=[]; ys=[]; texts=[]
        for obs, resid in zip(problem.observations, fit_result["raw_residuals"]):
            if obs.species_id == sid:
                xs.append(obs.time_s/60.0); ys.append(float(resid)); texts.append(obs.dataset_id)
        if xs:
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", name=sid, text=texts, marker=dict(color=color_map[sid], size=8)))
    fig.add_hline(y=0.0, line_dash="dash", line_color="#7b8ca0")
    fig.update_layout(title="Residual = model − measured", xaxis_title="Observation time (min)", yaxis_title="Residual (kmol m⁻³)")
    st.plotly_chart(_dark(fig), use_container_width=True)
    st.caption("Fitting data only. Hover points to see the dataset ID. Validation residuals are reported separately below.")



def _validation_residual_plot(problem, fit_result: dict) -> None:
    validation = fit_result.get("validation") or {}
    if not problem.validation_datasets:
        return
    st.markdown("### Independent validation residuals")
    st.caption("Validation observations were excluded from parameter estimation. All predictions use the fitted parameters and each validation dataset's own initial conditions.")
    if not len(problem.validation_observations):
        st.info("No validation observations are available to compare with predictions.")
        return
    st.markdown(f"**Validation RMSE:** {validation['rmse_kmol_m3']:.5g} kmol m⁻³  |  **Validation raw SSE:** {validation['sse_kmol_m6']:.5g}")
    fig = go.Figure()
    cmap = {sid: COLORS[i % len(COLORS)] for i,sid in enumerate(problem.model.species_ids)}
    for sid in problem.model.species_ids:
        records = [(o,r) for o,r in zip(problem.validation_observations, validation["residuals"]) if o.species_id == sid]
        if records:
            fig.add_trace(go.Scatter(x=[o.time_s / 60 for o,r in records], y=[float(r) for o,r in records],
                mode="markers", name=sid, text=[o.dataset_id for o,r in records],
                marker=dict(color=cmap[sid], symbol="diamond", size=9)))
    fig.add_hline(y=0, line_dash="dash", line_color="#7b8ca0")
    fig.update_layout(title="Validation residual = prediction − measured", xaxis_title="Time (min)", yaxis_title="Residual (kmol m⁻³)")
    st.plotly_chart(_dark(fig), use_container_width=True)


def _multistart_plot(problem, fit_result: dict) -> None:
    st.markdown("### Multistart diagnostics")
    starts = _starts_dataframe(problem, fit_result)
    fig = go.Figure(go.Scatter(
        x=starts["Start"], y=starts["SSE"], mode="markers", marker=dict(size=9), text=starts["Success"].astype(str),
    ))
    fig.update_layout(title="Final objective from every starting point", xaxis_title="Start number", yaxis_title="Weighted SSE")
    fig.update_yaxes(type="log")
    st.plotly_chart(_dark(fig), use_container_width=True)
    show_dataframe(_center_numeric(starts.head(min(12, len(starts)))), use_container_width=True, hide_index=True)
    if len(starts) > 1:
        best = float(starts.iloc[0]["SSE"])
        near = starts[starts["SSE"] <= best * 1.01 + 1e-14]
        st.caption(f"**{len(near)} of {len(starts)}** starts finished within 1% of the best objective. Similar objective values with materially different parameters are an identifiability warning, not just an optimiser warning.")


def render() -> None:
    workspace_header(
        "Kinetic Parameter Fitting",
        "Fit selected Excel-model parameters simultaneously across multiple experimental datasets using bounded multistart nonlinear least squares.",
        section="Kinetic Fitting",
        accent=ACCENT,
    )
    chips([
        ("Multiple datasets", "blue"), ("Bounded least squares", ""), ("Multistart", "warn"),
        ("Irregular sampling", "blue"), ("Missing data", ""), ("Residual diagnostics", ""),
    ])

    cloud = is_public_cloud()
    if cloud:
        st.info("Public kinetic fitting is enabled with restricted computational resources. Results stopped at a limit are not converged estimates.")
        with st.expander("Public fitting limits and numerical settings", expanded=False):
            st.markdown(public_fitting_limits_markdown())
    st.markdown("## 1. Prepare a fitting workbook")
    st.write("Use an Excel workbook containing the reaction model and the experimental measurements. Download the example below to see the exact worksheet structure.")
    if EXAMPLE_PATH.exists():
        st.download_button(
            "Download worked fitting workbook", data=EXAMPLE_PATH.read_bytes(),
            file_name=EXAMPLE_PATH.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with st.expander("How to enter datasets and initial conditions", expanded=False):
        st.markdown("""The **Datasets** sheet has **one row per experiment**. Use a unique `Dataset_ID` for each experiment. Set `Use_for_Fit` to `Yes` for experiments used to estimate parameters; set it to `No` for independent validation datasets that will be plotted and assessed after fitting. Supply a positive `Volume_m3` and the initial concentration `c0_<Species_ID>` for **every** species. All concentrations are in kmol/m³. Each dataset may have different initial conditions while sharing the fitted kinetic parameters.""")
        show_dataframe(pd.DataFrame([
            {"Dataset_ID":"E1","Use_for_Fit":"Yes","Volume_m3":1.0,"Volume_Model":"constant","c0_A":2.0,"c0_B":0.0},
            {"Dataset_ID":"E2","Use_for_Fit":"Yes","Volume_m3":1.0,"Volume_Model":"constant","c0_A":3.0,"c0_B":0.0},
        ]),hide_index=True,use_container_width=True)
        st.caption("Illustrative abbreviated example: the actual sheet requires c0 columns for all model species, including inert species.")

    with st.expander("How to enter experimental measurements and missing data", expanded=False):
        st.markdown("""In **Experimental_Data**, enter **one row per species measurement at one time**. `Dataset_ID` must match a selected experiment, `Time_s` is elapsed time in seconds, and `Species_ID` must match the Species sheet. Measurements are concentrations in kmol/m³. Irregular sampling is supported: measurements of different species need not occur at the same times. **Omit missing measurements**; do not enter zero unless the measured concentration really was zero.""")
        show_dataframe(pd.DataFrame([
            {"Dataset_ID":"E1","Time_s":0,"Species_ID":"A","Measured_Value_kmol_m3":2.00},
            {"Dataset_ID":"E1","Time_s":300,"Species_ID":"A","Measured_Value_kmol_m3":1.65},
            {"Dataset_ID":"E1","Time_s":300,"Species_ID":"B","Measured_Value_kmol_m3":0.30},
            {"Dataset_ID":"E2","Time_s":300,"Species_ID":"A","Measured_Value_kmol_m3":2.57},
        ]),hide_index=True,use_container_width=True)
        st.caption("Illustrative values, not a fitted or published dataset. An optional positive `Sigma_kmol_m3` may be stored with observations; the current interface's Species-scaled/Unweighted options do **not** use sigma as inverse-variance weights.")

    with st.expander("How to choose parameters, starting estimates and bounds", expanded=False):
        st.markdown("""The **Parameters** sheet contains parameter IDs and their `Value` (initial estimate). Mark eligible parameters with `Fit_Later = Yes` and enter **finite** `Lower_Bound` and `Upper_Bound` enclosing the starting value. Select which eligible parameters to fit after upload; unselected parameters retain their workbook values. Ensure the rate expressions in **Reactions** refer to declared parameter and species IDs. The four forward-model sheets are `Model`, `Species`, `Parameters`, `Reactions`.""")
        st.markdown("**Fitting method:** the workbook starting parameter vector is included as one optimisation start. Additional starts are distributed across the supplied parameter bounds. One shared parameter vector is fitted across all selected datasets.")

    with st.expander("Numerical method and results interpretation", expanded=False):
        st.markdown("""The optimiser uses bounded multistart nonlinear least squares. **Species-scaled** weighting divides residuals by a characteristic measured concentration for each species; **Unweighted** uses concentration residuals directly. The reported objective and residuals must be interpreted in the light of this choice. Good agreement does not, by itself, establish uniqueness or identifiability of parameter estimates. Model Diagnostics provides additional checks.""")

    st.markdown("## 2. Upload and validate")
    uploaded = st.file_uploader(
        "Upload KineticFittingPot fitting workbook (.xlsx)", type=["xlsx"], accept_multiple_files=False,
        help="Required model sheets: Model, Species, Parameters, Reactions. Fitting also requires Datasets and Experimental_Data.",
    )
    if uploaded is None:
        st.caption("For the first test, download the catalytic example above and upload it unchanged.")
        return
    raw = uploaded.getvalue()
    if cloud:
        package_problems = public_cloud_workbook_violations(raw)
        if package_problems:
            for msg in package_problems: st.error(msg)
            return
    try:
        base_problem = parse_fitting_workbook(raw)
    except (FittingValidationError, ModelValidationError, RuntimeError) as exc:
        st.error(str(exc)); return
    except Exception as exc:
        st.error(f"Unexpected fitting-workbook validation error: {exc}"); return

    if cloud:
        violations = public_fitting_violations(base_problem)
        if violations:
            for message in violations: st.error(message)
            return
    _preview(base_problem)

    st.markdown("## 3. Configure and run fitting")
    candidates = list(base_problem.fit_parameter_ids)
    selected = st.multiselect("Parameters to fit", candidates, default=candidates)
    if not selected:
        st.warning("Select at least one parameter to fit."); return
    try:
        problem = problem_with_fit_parameters(base_problem, selected)
    except FittingValidationError as exc:
        st.error(str(exc)); return
    if cloud and len(problem.fit_parameter_ids) > PUBLIC_FITTING_LIMITS["max_fitted_parameters"]:
        st.error("Too many fitted parameters for public fitting."); return
    show_dataframe(_center_numeric(_parameter_table(base_problem, selected)), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        weighting_label = st.selectbox(
            "Residual weighting", ["Species-scaled", "Unweighted"], index=0,
            help="Species-scaled divides each residual by the largest absolute measured concentration for that species. Unweighted uses concentration residuals directly.",
        )
    with c2:
        n_starts = st.slider("Multistart runs", min_value=1 if cloud else 5, max_value=PUBLIC_FITTING_LIMITS["max_starts"] if cloud else 50, value=PUBLIC_FITTING_LIMITS["max_starts"] if cloud else 20, step=1 if cloud else 5)
    with c3:
        seed = st.number_input("Multistart random seed", min_value=0, max_value=2_147_483_647, value=20260904, step=1)

    with st.expander("Advanced optimiser settings", expanded=False):
        max_nfev = st.number_input("Maximum function evaluations per start", min_value=25 if cloud else 50, max_value=PUBLIC_FITTING_LIMITS["max_nfev_per_start"] if cloud else 1000, value=PUBLIC_FITTING_LIMITS["max_nfev_per_start"] if cloud else 300, step=25 if cloud else 50)
        st.caption("KineticFittingPot internally scales each bounded parameter to a 0–1 search coordinate. Positive bounded parameters are mapped logarithmically; other bounded parameters are mapped linearly.")

    weighting = "species_scaled" if weighting_label == "Species-scaled" else "unweighted"
    if not st.button("Run bounded multistart fit", type="primary"):
        st.caption("The optimiser does not run until you press the button. Review the datasets, observations, fitted parameters and bounds first.")
        return

    budget_summary = None
    with st.spinner(f"Running {n_starts} bounded least-squares starts across {len(problem.datasets)} datasets..."):
        try:
            if cloud:
                outcome = run_public_fit(raw, selected, weighting=weighting, n_starts=int(n_starts),
                                         random_seed=int(seed), max_nfev=int(max_nfev))
                fit_result = outcome.fit_result
                budget_summary = outcome.budget_summary
            else:
                fit_result = fit_multistart(problem, weighting=weighting, n_starts=n_starts,
                                            random_seed=int(seed), max_nfev=int(max_nfev), budget=None)
                fit_result["validation"] = evaluate_validation(problem, fit_result)
        except PublicFitBusy:
            st.info("Kinetic fitting is currently busy. Another public fitting calculation is running. "
                    "Your uploaded workbook and selections remain available; please retry shortly.")
            return
        except PublicFitTimeout as exc:
            st.warning(str(exc))
            return
        except PublicFitStopped as exc:
            st.warning(f"Fitting stopped at a public computation limit: {exc} "
                       "No converged estimate is reported. Reduce the requested model or optimisation work.")
            st.caption(f"Work performed: {exc.summary}")
            return
        except Exception as exc:
            st.error(f"Kinetic fitting could not be completed: {exc}")
            return

    st.markdown("## 4. Assess the results")
    if not fit_result["best"]["success"]:
        st.warning("The lowest-objective result did not meet the optimiser convergence criteria. These estimates are preliminary, not a confirmed converged fit.")
    else:
        st.success("Optimisation convergence criteria satisfied for the best start. This does not establish parameter identifiability.")
    if budget_summary is not None:
        st.caption(f"Computation used: {budget_summary['integrations']:,} ODE integrations; {budget_summary['rhs_evaluations']:,} RHS evaluations; {budget_summary['objective_calls']:,} objective calls; {budget_summary['failed_forward_evaluations']:,} failed forward evaluations; {budget_summary['elapsed_s']:.1f} s elapsed.")
    st.markdown("### Best fit")
    best = fit_result["best"]
    successful = sum(bool(r["success"]) for r in fit_result["records"])
    cards = st.columns(5)
    values = [
        ("Best weighted SSE", f"{best['sse']:.4g}", weighting_label),
        ("Raw RMSE", f"{best['raw_rmse_kmol_m3']:.4g}", "kmol m⁻³"),
        ("Successful starts", f"{successful}/{len(fit_result['records'])}", "least_squares status"),
        ("Observations", str(len(problem.observations)), f"{len(problem.datasets)} datasets"),
        ("Fitted parameters", str(len(problem.fit_parameter_ids)), ", ".join(problem.fit_parameter_ids)),
    ]
    for col, item in zip(cards, values):
        with col: metric_card(*item, compact=True)

    truth = synthetic_truth(raw, problem.fit_parameter_ids)
    st.markdown("### Parameter estimates")
    show_dataframe(_center_numeric(_fit_parameter_results(problem, fit_result, truth)), use_container_width=True, hide_index=True)
    if truth:
        st.caption("Synthetic truth is read only **after** the fit for validation display. It is not passed to or read by the optimiser.")

    _trajectory_plots(problem, fit_result)
    _residual_plot(problem, fit_result)
    _validation_residual_plot(problem, fit_result)
    _multistart_plot(problem, fit_result)

    with st.expander("Fit method and caveats", expanded=False):
        st.markdown("- Solver: SciPy `solve_ivp` (RK45) for each dataset/trial parameter vector.")
        st.markdown("- Optimiser: bounded SciPy `least_squares` (`trf`).")
        st.markdown("- The workbook starting estimate is always one multistart location.")
        st.markdown("- Additional starts cover the user bounds; positive bounded parameters are sampled on a log scale.")
        st.markdown("- Multistart reduces dependence on one initial guess but does **not** mathematically prove a global optimum.")
        st.markdown("- Similar fit quality from materially different parameter vectors is an identifiability warning.")

    try:
        completed = build_fitting_results_workbook(raw, problem, fit_result)
        st.download_button(
            "Download completed kinetic-fitting workbook", data=completed,
            file_name="KineticFittingPot_kinetic_fit_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary",
        )
        st.caption("The download retains the original model/data sheets and adds Fit_Parameters, Fit_Starts, Fit_Predictions, Fit_Residuals and Fit_Summary; when applicable, separate Validation_* sheets are included.")
    except Exception as exc:
        st.error(f"The fit completed, but KineticFittingPot could not create the result workbook: {exc}")

    st.divider()
    if st.button("← Kinetic Fitting Fundamentals"):
        navigate("Kinetic Fitting Fundamentals")
