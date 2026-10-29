from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.general_batch_model import (
    ModelValidationError,
    build_results_workbook,
    generated_species_equations,
    parse_model_workbook,
    simulate_general_isothermal_batch,
    species_peak,
)
from utils.deployment import (
    PUBLIC_CUSTOM_MODEL_LIMITS,
    is_public_cloud,
    public_cloud_model_violations,
    public_cloud_workbook_violations,
    public_custom_limits_markdown,
)
from utils.ui import metric_card, workspace_header, show_dataframe
from utils.trajectory_plots import plot_values


ACCENT = "#38bdf8"
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "data" / "templates" / "KineticFittingPot_Isothermal_Batch_Model_Template.xlsx"
SERIES_COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]


def _dark(fig: go.Figure, height: int = 460) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=25, r=25, t=65, b=35),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#e5edf5", zerolinecolor="#b6c9d9")
    fig.update_yaxes(gridcolor="#e5edf5", zerolinecolor="#b6c9d9")
    return fig


def _safe_filename(name: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return text[:80] or "KineticFittingPot_Model"


def _intro() -> None:
    """Optional model-building guidance, kept close to the upload workflow."""
    with st.expander("How to complete the workbook", expanded=False):
        st.markdown(
            "The **Model** sheet specifies operating conditions, **Species** defines the initial charge, "
            "**Parameters** contains kinetic constants, and **Reactions** contains rate expressions and stoichiometry. "
            "Start with the supplied example, then change one part at a time. "
            "Use literal values in the required cells; Excel formulas are not accepted in model-definition fields."
        )
        st.markdown("**Unit basis:** amounts in kmol, volume in m³, time in s, and rates in kmol m⁻³ s⁻¹. "
                    "Parameter units must be consistent with the rate expressions; the software cannot verify dimensions.")
        st.markdown("The initial workbook is a worked Van de Vusse example that can be tested before modifying the reaction network.")
    with st.expander("Mathematical model and supported expressions", expanded=False):
        st.latex(r"\frac{d\mathbf n}{dt}=V\mathbf S\mathbf r(\mathbf c,\boldsymbol\theta),\qquad \mathbf c=\frac{\mathbf n}{V}")
        st.markdown("The reactor is well-mixed and isothermal. Liquid volume can be constant or "
                    "composition-dependent, with $V=\\sum_j n_j M_j/\\rho_j$.")
        st.markdown("Rate expressions use `c_x1`-style concentrations, defined parameter names, "
                    "arithmetic `+ - * / **`, parentheses, and `exp()`, `log()`, `sqrt()`, `abs()`. "
                    "Expressions are parsed with restricted syntax, not executed as arbitrary Python commands.")
        st.warning("Workbook validation cannot establish chemical plausibility, unit consistency, "
                   "or whether a rate expression remains defined throughout the full trajectory.")


def _template_download() -> None:
    st.markdown("## 1. Prepare the model")
    st.markdown(
        "The supplied template is the **same Van de Vusse isothermal problem** used by the built-in KineticFittingPot simulator. "
        "The example also provides a numerical consistency check: the Excel-defined model should reproduce the built-in simulator in **both constant-volume and composition-dependent-volume modes** before you edit it into a different reaction network."
    )
    if TEMPLATE_PATH.exists():
        st.download_button(
            "Download Van de Vusse Excel model template",
            data=TEMPLATE_PATH.read_bytes(),
            file_name=TEMPLATE_PATH.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=False,
        )
    else:
        st.error("The bundled Excel template is missing from this KineticFittingPot installation.")


def _model_preview(model) -> None:
    st.success("Workbook validated. Review the model below before running the solver.")
    cols = st.columns(5)
    summary = [
        ("Species", len(model.species_ids), "state variables"),
        ("Reactions", len(model.reaction_ids), "rate expressions"),
        ("Parameters", len(model.parameter_ids), "kinetic/model constants"),
        ("Volume model", model.volume_model.replace("_", " "), f"V₀ = {model.initial_volume_m3:.4g} m³"),
        ("Batch time", f"{model.batch_duration_s/60:.4g} min", f"{model.output_points} output points"),
    ]
    for col, (label, value, note) in zip(cols, summary):
        with col:
            metric_card(label, value, note, compact=True)

    st.markdown("### Species and initial conditions")
    species_df = pd.DataFrame({
        "Species_ID": model.species_ids,
        "Display name": model.display_names,
        "Initial concentration (kmol m⁻³)": model.initial_concentration_kmol_m3,
        "Initial amount (kmol)": model.initial_moles_kmol,
        "Molecular weight (kg kmol⁻¹)": model.molecular_weight_kg_per_kmol,
        "Density (kg m⁻³)": model.density_kg_per_m3,
        "Plot default": ["Yes" if x else "No" for x in model.plot_default],
    })
    show_dataframe(species_df, use_container_width=True, hide_index=True)

    st.markdown("### Parameters")
    parameter_df = pd.DataFrame({
        "Parameter_ID": model.parameter_ids,
        "Value": model.parameter_values,
        "Units": model.parameter_units,
        "Fit later?": ["Yes" if x else "No" for x in model.fit_later],
        "Lower bound": model.lower_bounds,
        "Upper bound": model.upper_bounds,
    })
    show_dataframe(parameter_df, use_container_width=True, hide_index=True)

    st.markdown("### Reaction rates and stoichiometry")
    reaction_df = pd.DataFrame(model.stoichiometric_matrix.T, columns=model.species_ids)
    reaction_df.insert(0, "Rate expression", model.rate_expressions)
    reaction_df.insert(0, "Description", model.reaction_descriptions)
    reaction_df.insert(0, "Reaction_ID", model.reaction_ids)
    show_dataframe(reaction_df, use_container_width=True, hide_index=True)

    with st.expander("Interpreted mathematical model (generated equations)", expanded=False):
        st.caption("Rate symbols correspond to the workbook reaction rows; rates are combined with the stoichiometric matrix.")
        for equation in generated_species_equations(model):
            st.code(equation, language=None)


@st.fragment
def _plots(model, result, visible_species: list[str]) -> None:
    time_min = result["time_s"] / 60.0
    variable = st.selectbox("Additional species plot", ["Existing amount and concentration plots", "Mole fraction", "Mass fraction", "Net conversion", "Overall selectivity"], help="Plot-only transformations; the solved model is not changed.")
    reactant = 0
    product = 1 if len(model.species_ids) > 1 else 0
    ratio = 1.0
    if variable in ("Net conversion", "Overall selectivity"):
        reactant = st.selectbox("Reference reactant", range(len(model.species_ids)), format_func=lambda i: f"{model.species_ids[i]} — {model.display_names[i]}")
    if variable == "Overall selectivity":
        product = st.selectbox("Desired product", range(len(model.species_ids)), index=product, format_func=lambda i: f"{model.species_ids[i]} — {model.display_names[i]}")
        ratio = st.number_input("Theoretical product/reactant molar ratio (stoichiometric basis)", min_value=0.000001, value=1.0)
        st.caption("Overall selectivity = net product formed / net reactant consumed, divided by the specified theoretical molar ratio. Undefined until the reference reactant has positive net disappearance. This does not attribute production to a particular reaction pathway.")
    elif variable == "Net conversion":
        st.caption("Net conversion is calculated from the selected reference species' initial and current amounts; regeneration can affect its interpretation.")
    if variable != "Existing amount and concentration plots":
        try:
            values = plot_values(result["amounts_kmol"], model.molecular_weight_kg_per_kmol, variable, reactant=reactant, product=product, stoich_ratio=ratio)
            fig_extra = go.Figure()
            if values.ndim == 2:
                for i, sid in enumerate(model.species_ids):
                    if sid in visible_species:
                        fig_extra.add_trace(go.Scatter(x=time_min, y=values[:, i], mode="lines", name=f"{sid} — {model.display_names[i]}", line=dict(color=SERIES_COLORS[i % len(SERIES_COLORS)])))
            else:
                fig_extra.add_trace(go.Scatter(x=time_min, y=values, mode="lines", name=variable))
            fig_extra.update_layout(title=variable, xaxis_title="Time (min)", yaxis_title=variable + " (−)")
            st.plotly_chart(_dark(fig_extra), use_container_width=True)
            if values.ndim == 1 and not np.any(np.isfinite(values)):
                st.info("This quantity is undefined over the selected time range.")
        except ValueError as exc:
            st.info(str(exc))


    fig_n = go.Figure()
    for idx, sid in enumerate(model.species_ids):
        if sid not in visible_species:
            continue
        fig_n.add_trace(go.Scatter(
            x=time_min,
            y=result["amounts_kmol"][:, idx],
            mode="lines",
            name=f"{sid} — {model.display_names[idx]}",
            line=dict(color=SERIES_COLORS[idx % len(SERIES_COLORS)], width=2.2),
        ))
    fig_n.update_layout(title="Species amounts", xaxis_title="Time (min)", yaxis_title="Amount (kmol)")
    st.plotly_chart(_dark(fig_n), use_container_width=True)

    fig_c = go.Figure()
    for idx, sid in enumerate(model.species_ids):
        if sid not in visible_species:
            continue
        fig_c.add_trace(go.Scatter(
            x=time_min,
            y=result["concentrations_kmol_m3"][:, idx],
            mode="lines",
            name=f"{sid} — {model.display_names[idx]}",
            line=dict(color=SERIES_COLORS[idx % len(SERIES_COLORS)], width=2.2),
        ))
    fig_c.update_layout(title="Species concentrations", xaxis_title="Time (min)", yaxis_title="Concentration (kmol m⁻³)")
    st.plotly_chart(_dark(fig_c), use_container_width=True)

    if model.volume_model == "composition_dependent":
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(
            x=time_min,
            y=result["volume_m3"],
            mode="lines",
            name="Liquid volume",
            line=dict(color="#19D3F3", width=2.4),
        ))
        fig_v.update_layout(title="Composition-dependent liquid volume", xaxis_title="Time (min)", yaxis_title="Volume (m³)")
        st.plotly_chart(_dark(fig_v), use_container_width=True)

    fig_r = go.Figure()
    for idx, rid in enumerate(model.reaction_ids):
        fig_r.add_trace(go.Scatter(
            x=time_min,
            y=result["reaction_rates_kmol_m3_s"][:, idx],
            mode="lines",
            name=f"{rid}: {model.reaction_descriptions[idx]}",
            line=dict(color=SERIES_COLORS[idx % len(SERIES_COLORS)], width=2.0),
        ))
    fig_r.update_layout(title="Reaction rates", xaxis_title="Time (min)", yaxis_title="Rate (kmol m⁻³ s⁻¹)")
    st.plotly_chart(_dark(fig_r), use_container_width=True)


def render() -> None:
    workspace_header(
        "Simulate Your Own Model — Isothermal Batch Reactor",
        "Define a general isothermal batch-reaction network in Excel, validate the model KineticFittingPot has understood, simulate it, and download the workbook with numerical results added.",
        section="Forward Modelling",
        accent=ACCENT,
    )
    if is_public_cloud():
        st.warning(
            "**Public-server protection is active for this workspace.** You can still upload, validate, run and download "
            "a general isothermal batch model, but model size and numerical work are deliberately capped so one public "
            "session cannot monopolise the shared server. The local KineticFittingPot build remains unrestricted by these cloud caps."
        )
        with st.expander("Public-server model limits", expanded=False):
            st.markdown(public_custom_limits_markdown())
    _template_download()
    _intro()

    st.markdown("## 2. Upload and validate")
    uploader_kwargs = {
        "label": "Upload KineticFittingPot Excel model (.xlsx)",
        "type": ["xlsx"],
        "accept_multiple_files": False,
        "help": "Use the supplied template structure. Required sheets: Model, Species, Parameters and Reactions.",
    }
    if is_public_cloud():
        # Streamlit 1.63 supports a per-widget upload limit. Keep this argument
        # cloud-only so an older existing local venv can still run unchanged.
        uploaded = st.file_uploader(
            **uploader_kwargs,
            max_upload_size=PUBLIC_CUSTOM_MODEL_LIMITS["max_upload_bytes"] // (1024 * 1024),
        )
    else:
        uploaded = st.file_uploader(**uploader_kwargs)
    if uploaded is None:
        st.caption("No workbook loaded yet. Download the example above, inspect it, then upload it unchanged for the first consistency test.")
        return

    raw = uploaded.getvalue()
    if is_public_cloud():
        package_problems = public_cloud_workbook_violations(raw)
        if package_problems:
            for problem in package_problems:
                st.error(problem)
            st.info("The public limits protect a shared teaching server. The full local KineticFittingPot build does not apply these cloud-specific caps.")
            st.stop()
    try:
        model = parse_model_workbook(raw)
    except (ModelValidationError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        if is_public_cloud():
            st.error("KineticFittingPot could not validate this workbook on the public server. Check the template structure and try again.")
        else:
            st.error(f"Unexpected workbook-validation error: {exc}")
        st.stop()

    if is_public_cloud():
        model_problems = public_cloud_model_violations(model)
        if model_problems:
            st.error("This workbook is valid, but it exceeds one or more public-server limits:")
            for problem in model_problems:
                st.markdown(f"- {problem}")
            st.info("Reduce the model for the public server or run the full local KineticFittingPot build.")
            st.stop()

    st.markdown("### Validation summary")
    st.success(f"Workbook structure and expressions are valid: {len(model.species_ids)} species, "
               f"{len(model.reaction_ids)} reactions, {len(model.parameter_ids)} parameters.")
    try:
        from utils.general_batch_model import evaluate_rates, model_volume_m3
        initial_volume = model_volume_m3(model, model.initial_moles_kmol)
        initial_concentrations = model.initial_moles_kmol / initial_volume
        initial_rates = evaluate_rates(model, initial_concentrations)
        if not np.all(np.isfinite(initial_rates)):
            raise ValueError("An initial rate was not finite.")
    except (ValueError, ArithmeticError, OverflowError, FloatingPointError) as exc:
        st.error("Initial rate evaluation failed. The workbook could be parsed, but at least one "
                 "rate expression cannot be evaluated at the specified initial charge.")
        st.error(str(exc))
        st.info("Check concentration-dependent denominators, log/sqrt arguments, "
                "parameter values and the reaction identified above.")
        st.stop()
    st.success("Initial rate evaluation passed: all reaction rates are finite at the initial state. "
               "This does not guarantee successful integration at later times.")
    with st.expander("Review interpreted model", expanded=False):
        _model_preview(model)

    st.markdown("## 3. Simulate")
    target_species = st.selectbox(
        "Target species for peak/summary diagnostics",
        list(model.species_ids),
        index=(list(model.species_ids).index("x3") if "x3" in model.species_ids else 0),
        format_func=lambda sid: f"{sid} — {model.display_names[model.species_ids.index(sid)]}",
    )
    default_visible = [sid for sid, flag in zip(model.species_ids, model.plot_default) if flag]
    if not default_visible:
        default_visible = list(model.species_ids)
    visible_species = st.multiselect(
        "Visible species (amount and concentration plots)",
        list(model.species_ids),
        default=default_visible,
        format_func=lambda sid: f"{sid} — {model.display_names[model.species_ids.index(sid)]}",
    )

    if not st.button("Run Excel-defined model", type="primary"):
        st.caption("The solver does not run until you press the button, so you can inspect the parsed model first.")
        return

    try:
        if is_public_cloud():
            result = simulate_general_isothermal_batch(
                model,
                max_function_evaluations=int(PUBLIC_CUSTOM_MODEL_LIMITS["max_function_evaluations"]),
                max_wall_time_s=float(PUBLIC_CUSTOM_MODEL_LIMITS["max_wall_time_s"]),
            )
        else:
            result = simulate_general_isothermal_batch(model)
        peak = species_peak(model, result, target_species)
    except Exception as exc:
        message = str(exc)
        if "function-evaluation limit" in message or "wall-time limit" in message:
            st.error("The numerical work limit was reached before the solution finished.")
        elif "rate expression" in message.lower() or "could not evaluate" in message.lower():
            st.error("A reaction-rate expression became invalid during integration. "
                     "Check denominators, logarithms, square roots and the reaction-rate domain.")
        elif "volume" in message.lower():
            st.error("The model encountered an invalid liquid volume during integration. "
                     "Check species inventories, densities and the volume model.")
        elif "solver" in message.lower():
            st.error("The ODE solver could not complete the requested time interval. "
                     "Check the model kinetics and consider a shorter batch duration.")
        else:
            st.error("The simulation could not be completed with the supplied model.")
        with st.expander("Technical error details", expanded=False):
            st.code(message)
        st.stop()

    st.markdown("## 4. Results")
    idx = model.species_ids.index(target_species)
    cards = st.columns(5)
    card_data = [
        ("Target peak time", f"{peak['time_min']:.3f} min", f"{peak['time_s']:.2f} s"),
        ("Target peak amount", f"{peak['amount_kmol']:.5g} kmol", target_species),
        ("Target final amount", f"{result['amounts_kmol'][-1, idx]:.5g} kmol", target_species),
        ("Function evaluations", str(result["nfev"]), "RK45 / solve_ivp"),
        ("Final volume", f"{result['final_volume_m3']:.4g} m³", f"{model.volume_model.replace('_', ' ')}; V₀={result['initial_volume_m3']:.4g} m³"),
    ]
    for col, (label, value, note) in zip(cards, card_data):
        with col:
            metric_card(label, value, note, compact=True)

    if peak["at_end"]:
        st.warning("The selected target species peaks at or very near the end of the simulated interval. Increase Batch_Duration_s before interpreting this as a true interior optimum.")
    if result["min_amount_kmol"] < -1e-7:
        st.warning(
            f"At least one species amount became negative (minimum {result['min_amount_kmol']:.3e} kmol). "
            "Check the kinetic expression, stoichiometry and time window; this is more than ordinary solver round-off."
        )

    _plots(model, result, visible_species)

    st.markdown("### Initial and final state")
    state_df = pd.DataFrame({
        "Species": model.species_ids,
        "Display name": model.display_names,
        "Initial amount (kmol)": result["amounts_kmol"][0, :],
        "Final amount (kmol)": result["amounts_kmol"][-1, :],
        "Initial concentration (kmol m⁻³)": result["concentrations_kmol_m3"][0, :],
        "Final concentration (kmol m⁻³)": result["concentrations_kmol_m3"][-1, :],
    })
    show_dataframe(state_df, use_container_width=True, hide_index=True)
    if model.volume_model == "composition_dependent":
        st.caption(
            f"Liquid volume changed from **{result['initial_volume_m3']:.6g} m³** to **{result['final_volume_m3']:.6g} m³** because the species have different molecular weights and densities."
        )

    with st.expander("Solver diagnostics", expanded=False):
        st.markdown(f"- Solver success: **{result['solver_success']}**")
        st.markdown(f"- Message: `{result['solver_message']}`")
        st.markdown(f"- Method: **{result['method']}**")
        st.markdown(f"- rtol: `{result['rtol']}`")
        st.markdown(f"- atol: `{result['atol']}`")
        st.markdown(f"- Function evaluations: **{result['nfev']}**")
        if is_public_cloud():
            st.markdown(f"- Solver wall time: **{result.get('solver_wall_time_s', float('nan')):.3f} s**")
            st.markdown(f"- Public ODE evaluation cap: **{PUBLIC_CUSTOM_MODEL_LIMITS['max_function_evaluations']:,}**")

    try:
        completed = build_results_workbook(raw, model, result, target_species)
    except Exception as exc:
        st.error(f"The simulation completed, but KineticFittingPot could not create the result workbook: {exc}")
        return

    filename = f"{_safe_filename(model.model_name)}_KineticFittingPot_results.xlsx"
    st.download_button(
        "Download completed Excel workbook",
        data=completed,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
    st.caption(
        "The downloaded workbook retains the model-definition sheets and replaces **Results_TimeSeries** and **Results_Summary** with this simulation. "
        "The model-definition worksheets can also be used with kinetic parameter fitting."
    )
