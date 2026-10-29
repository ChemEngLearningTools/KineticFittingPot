from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils.batch_model import (
    SPECIES,
    SPECIES_NAMES,
    STOICHIOMETRIC_MATRIX,
    arrhenius_rate_constants,
    initial_moles_from_component_volumes,
    reference_parameters,
    simulate_van_de_vusse,
)
from utils.ui import chips, metric_card, navigate, teaching_table, workspace_header
from utils.trajectory_plots import plot_values


ACCENT = "#f59e0b"
SPECIES_COLORS = {
    "x0": "#636EFA",
    "x1": "#EF553B",
    "x2": "#00CC96",
    "x3": "#AB63FA",
    "x4": "#FFA15A",
}


def _concept_card(title: str, body: str, accent: str = ACCENT) -> None:
    st.markdown(
        f"""
        <div class='teaching-card' style='--teach-accent:{accent};'>
            <div class='teaching-card-title'>{title}</div>
            <div class='teaching-card-body'>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _dark(fig: go.Figure, height: int = 470) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=25, r=25, t=65, b=35),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        legend_title_text="",
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#e5edf5", zerolinecolor="#b6c9d9")
    fig.update_yaxes(gridcolor="#e5edf5", zerolinecolor="#b6c9d9")
    return fig


def _fmt(value: float, digits: int = 4) -> str:
    if not np.isfinite(value):
        return "—"
    if value == 0:
        return "0"
    if abs(value) < 1e-3 or abs(value) >= 1e4:
        return f"{value:.3e}"
    return f"{value:.{digits}g}"


def _species_list() -> None:
    st.markdown("### Species in the model")
    teaching_table(
        ["Species", "Role"],
        [(f"x{idx}", name) for idx, name in enumerate(SPECIES_NAMES)],
        alignments=["center", "left"],
        monospace_columns={0},
    )


def _problem_and_method() -> None:
    st.markdown("## Reaction system")
    st.markdown(
        "The built-in simulator uses the **Van de Vusse reaction network**. "
        "Several reactions occur simultaneously, and the desired species is an intermediate. "
        "An important engineering question is **when to stop the batch**, rather than simply how much reactant eventually disappears."
    )

    reaction_cols = st.columns(3)
    with reaction_cols[0]:
        st.markdown("**Reaction 1 — by-product path**")
        st.latex(r"2x_1\rightarrow x_2")
        st.latex(r"r_1=k_1c_1^2")
    with reaction_cols[1]:
        st.markdown("**Reaction 2 — desired-product formation**")
        st.latex(r"x_1\rightarrow x_3")
        st.latex(r"r_2=k_2c_1")
    with reaction_cols[2]:
        st.markdown("**Reaction 3 — desired-product loss**")
        st.latex(r"x_3\rightarrow x_4")
        st.latex(r"r_3=k_3c_3")

    _species_list()
    _concept_card(
        "Engineering objective",
        "The desired product <b>x<sub>3</sub></b> is formed from the reactant and then consumed to form waste. "
        "The simulator identifies the time at which <b>x<sub>3</sub> reaches its maximum</b> "
        "within the simulated window and reports the reactor state at that stopping point.",
        "#38bdf8",
    )

    with st.expander("Mathematical model and numerical method", expanded=False):
        st.markdown("**Stoichiometric model**")
        st.markdown("For $x_0$ to $x_4$ and the three reactions above, the net stoichiometric matrix is:")
        st.latex(
            r"\mathbf S="
            r"\begin{bmatrix}"
            r"0&0&0\\"
            r"-2&-1&0\\"
            r"1&0&0\\"
            r"0&1&-1\\"
            r"0&0&1"
            r"\end{bmatrix}"
        )
        st.markdown("**State vector**")
        st.latex(r"\mathbf n=\begin{bmatrix}n_0&n_1&n_2&n_3&n_4\end{bmatrix}^{T}")
        st.markdown("**Reaction-rate vector**")
        st.latex(r"\mathbf r=\begin{bmatrix}r_1&r_2&r_3\end{bmatrix}^{T}")
        st.markdown("Concentrations follow from species amounts and liquid volume:")
        st.latex(r"c_j=\frac{n_j}{V}")
        st.markdown("For the composition-dependent-volume option:")
        st.latex(r"V=\sum_{j=1}^{N_S}\frac{n_jM_j}{\rho_j}")
        st.markdown("The species balances are:")
        st.latex(r"\boxed{\frac{d\mathbf n}{dt}=V\mathbf S\mathbf r(\mathbf c,T)}")
        st.markdown("**Numerical integration**")
        st.markdown(
            "The simulator uses **`scipy.integrate.solve_ivp`** with adaptive **RK45** integration. "
            "At each evaluation, the current amounts determine liquid volume and concentrations; "
            "Arrhenius rate constants and reaction rates are then evaluated to return $V\\mathbf S\\mathbf r$."
        )
        st.latex(
            r"\mathbf n(t)\;\longrightarrow\;V,\mathbf c\;\longrightarrow\;"
            r"\mathbf k(T)\;\longrightarrow\;\mathbf r\;\longrightarrow\;V\mathbf S\mathbf r"
        )
        st.markdown(
            "The default tolerances are $\\mathrm{rtol}=10^{-6}$ and $\\mathrm{atol}=10^{-9}$. "
            "The regular points on the figures are requested output points; RK45 selects its own internal time steps."
        )
        st.markdown("**Model assumptions and adjustments**")
        st.markdown(
            "**Adjustable inputs:** reactor temperature, batch duration, vessel and working-volume context, "
            "initial charge, liquid-volume model, Arrhenius parameters and optional initial products. "
            "**Assumptions:** a well-mixed liquid phase, a batch without inlet or outlet streams during reaction, "
            "and a specified, constant reactor temperature. Feed and energy balances are outside this model's scope."
        )


def _suggested_experiments() -> None:
    st.markdown("## Suggested experiments with this simulation")
    st.markdown(
        "The default case is a **reference batch**, not a single answer to memorise. "
        "Use the experiments below to change one feature at a time and connect the model inputs to the resulting "
        "amount, concentration, reaction-rate, conversion, yield and selectivity behaviour."
    )

    experiments = [
        (
            "1. Find the optimum stopping time for x3",
            "**Try this:** Run the default case first and locate the reported maximum in the desired-product $x_3$ trajectory. "
            "Then extend or shorten the batch duration so that the maximum is clearly inside the simulated time window.\n\n"
            "**Look for:** Compare the time of maximum $x_3$ with the $x_1$, $x_3$ and reaction-rate profiles.\n\n"
            "**Think about:** Why does continuing the batch after the maximum reduce the amount of desired product? "
            "Which reaction forms $x_3$, and which reaction subsequently consumes it?",
        ),
        (
            "2. Change the reaction temperature",
            "**Try this:** Compare the default 60 °C case with a lower and a higher temperature, for example 50 °C and 70 °C. "
            "Keep the initial charge and volume model unchanged.\n\n"
            "**Look for:** Compare reaction rates, the time to maximum $x_3$, the maximum amount of $x_3$, conversion and yield.\n\n"
            "**Think about:** Increasing temperature accelerates Arrhenius kinetics, but the three reactions do not necessarily accelerate by the same factor. "
            "Does a faster batch automatically give the best desired-product outcome?",
        ),
        (
            "3. Change the initial x0:x1 charge ratio",
            "**Try this:** Keep the total initial liquid charge near 0.70 m³ but change the split between solvent $x_0$ and reactant $x_1$; "
            "for example compare 0.45/0.25 m³ with 0.25/0.45 m³.\n\n"
            "**Look for:** Compare the initial $x_1$ concentration, reaction rates, conversion, maximum $x_3$ and optimum stopping time.\n\n"
            "**Think about:** Reaction 1 depends on $c_1^2$ whereas Reaction 2 depends on $c_1$. "
            "How does changing the initial formulation alter the competition between desired-product formation and the by-product path?",
        ),
        (
            "4. Compare the two liquid-volume models",
            "**Try this:** Run an otherwise identical batch using **Constant volume** and **Composition-dependent volume**.\n\n"
            "**Look for:** Compare the liquid-volume trajectory, concentrations, reaction rates and the optimum $x_3$ result.\n\n"
            "**Think about:** Is the constant-volume approximation important for this particular case? "
            "A modelling assumption can be useful even when it is not exact, provided its effect on the quantities of interest is understood.",
        ),
        (
            "5. Change batch size while preserving composition",
            "**Try this:** Reduce or increase both initial component volumes by the same proportion so that the $x_0:x_1$ ratio is unchanged. "
            "For example compare 0.35/0.35 m³ with 0.25/0.25 m³.\n\n"
            "**Look for:** Compare concentration profiles with species amounts and the maximum amount of $x_3$.\n\n"
            "**Think about:** Why can the concentration-time behaviour remain almost unchanged while the total amount of product changes? "
            "This is a useful distinction between **intensive** quantities such as concentration and **extensive** quantities such as moles.",
        ),
        (
            "6. Explore the kinetic assumptions",
            "**Try this:** Open **Kinetic parameters and advanced settings** and change one Arrhenius parameter at a time. "
            "Reset it before changing another parameter so the comparison remains interpretable.\n\n"
            "**Look for:** Compare reaction rates, maximum $x_3$, optimum stopping time, conversion and selectivity.\n\n"
            "**Think about:** Which engineering conclusions are robust, and which depend strongly on the assumed kinetic parameters? "
            "This is also a reminder that a simulator is only as reliable as the kinetic model supplied to it.",
        ),
    ]

    for title, body in experiments:
        with st.expander(title, expanded=False):
            st.markdown(body)


def _controls() -> dict:
    ref = reference_parameters()
    st.markdown("## Simulation controls")
    st.caption(
        "The default recipe uses a 50:50 solvent/reactant initial-volume ratio, with an initial "
        "liquid charge of 0.70 m³ in a 1.00 m³ reactor vessel."
    )

    st.markdown("**Reactor and operating basis**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        temperature_c = st.number_input("Temperature (°C)", value=60.0, step=1.0, min_value=-50.0, max_value=300.0)
    with c2:
        batch_minutes = st.number_input("Batch duration (min)", value=120.0, step=10.0, min_value=0.1, max_value=1440.0)
    with c3:
        reactor_capacity_m3 = st.number_input(
            "Reactor vessel volume (m³)",
            value=1.00,
            step=0.10,
            min_value=0.01,
            max_value=100.0,
            help="Geometric internal vessel capacity. This provides the physical fill-volume context; it does not change the kinetic equations.",
        )
    with c4:
        nominal_working_volume_m3 = st.number_input(
            "Nominal working volume (m³)",
            value=0.70,
            step=0.05,
            min_value=0.001,
            max_value=100.0,
            help="Normal intended liquid operating volume. The actual initial liquid volume is calculated from the charge below.",
        )

    st.markdown("**Initial liquid charge**")
    q1, q2, _q3, _q4 = st.columns(4)
    with q1:
        solvent_volume = st.number_input("Initial solvent x0 (m³)", value=0.35, step=0.05, min_value=0.0, max_value=20.0)
    with q2:
        reactant_volume = st.number_input("Initial reactant x1 (m³)", value=0.35, step=0.05, min_value=0.001, max_value=20.0)

    volume_label = st.radio(
        "Liquid-volume model",
        ["Constant volume", "Composition-dependent volume"],
        index=0,
        horizontal=True,
        help="Constant volume is the simpler teaching assumption. Composition-dependent volume recalculates V = Σ n_j M_j / ρ_j as reaction proceeds.",
    )

    A = ref.pre_exponential.copy()
    E = ref.activation_energy_kj_per_kmol.copy()
    product_initial = np.zeros(3, dtype=float)
    output_points = 1200

    with st.expander("Kinetic parameters and advanced settings", expanded=False):
        st.markdown("**Arrhenius parameters**")
        ac = st.columns(3)
        with ac[0]:
            A[0] = st.number_input("A1 (m³ kmol⁻¹ s⁻¹)", value=float(A[0]), format="%.6g")
            E[0] = st.number_input("E1 (kJ kmol⁻¹)", value=float(E[0]), format="%.6g")
        with ac[1]:
            A[1] = st.number_input("A2 (s⁻¹)", value=float(A[1]), format="%.6g")
            E[1] = st.number_input("E2 (kJ kmol⁻¹)", value=float(E[1]), format="%.6g")
        with ac[2]:
            A[2] = st.number_input("A3 (s⁻¹)", value=float(A[2]), format="%.6g")
            E[2] = st.number_input("E3 (kJ kmol⁻¹)", value=float(E[2]), format="%.6g")

        st.markdown("**Optional initial products**")
        pc = st.columns(3)
        with pc[0]:
            product_initial[0] = st.number_input("Initial x2 (kmol)", value=0.0, min_value=0.0, format="%.6g")
        with pc[1]:
            product_initial[1] = st.number_input("Initial x3 (kmol)", value=0.0, min_value=0.0, format="%.6g")
        with pc[2]:
            product_initial[2] = st.number_input("Initial x4 (kmol)", value=0.0, min_value=0.0, format="%.6g")
        output_points = st.number_input("Plot/output points", value=1200, min_value=200, max_value=5000, step=100)

        teaching_table(
            ["Species", "Role", "M (kg kmol⁻¹)", "ρ (kg m⁻³)"],
            [
                (symbol, role, f"{mw:.6g}", f"{rho:.6g}")
                for symbol, role, mw, rho in zip(
                    SPECIES,
                    SPECIES_NAMES,
                    ref.molecular_weight_kg_per_kmol,
                    ref.density_kg_per_m3,
                )
            ],
            alignments=["left", "left", "center", "center"],
            monospace_columns={2, 3},
        )

    component_volumes = np.array([solvent_volume, reactant_volume, 0.0, 0.0, 0.0], dtype=float)
    n0 = initial_moles_from_component_volumes(
        component_volumes,
        ref.molecular_weight_kg_per_kmol,
        ref.density_kg_per_m3,
    )
    n0[2:] = product_initial
    initial_volume_m3 = float(np.sum(n0 * ref.molecular_weight_kg_per_kmol / ref.density_kg_per_m3))
    vessel_fill_pct = 100.0 * initial_volume_m3 / float(reactor_capacity_m3)
    working_fill_pct = 100.0 * initial_volume_m3 / float(nominal_working_volume_m3)
    nominal_working_pct = 100.0 * float(nominal_working_volume_m3) / float(reactor_capacity_m3)

    st.markdown(
        f"**Physical fill basis:** initial liquid volume = **{initial_volume_m3:.3f} m³** · "
        f"vessel fill = **{vessel_fill_pct:.1f}%** · "
        f"initial charge / nominal working volume = **{working_fill_pct:.1f}%** "
        f"(nominal working volume = {nominal_working_pct:.1f}% of vessel capacity)."
    )

    if nominal_working_volume_m3 > reactor_capacity_m3 * (1.0 + 1e-12):
        st.error(
            "The nominal working volume is greater than the geometric reactor vessel volume. "
            "The chemistry calculation can still run, but this reactor definition is not physically feasible."
        )
    if initial_volume_m3 > reactor_capacity_m3 * (1.0 + 1e-12):
        st.error(
            "The initial liquid charge exceeds the geometric reactor vessel volume. "
            "The numerical chemistry can still be evaluated, but this fill is not physically feasible."
        )
    elif initial_volume_m3 > nominal_working_volume_m3 * (1.0 + 1e-12):
        st.warning(
            "The initial liquid charge is above the nominal working volume. "
            "KineticFittingPot will run the calculation so that the consequence is visible, but the batch is outside the stated normal operating fill."
        )

    k = arrhenius_rate_constants(temperature_c, A, E)

    kc = st.columns(3)
    labels = [
        ("k1", k[0], "m³ kmol⁻¹ s⁻¹"),
        ("k2", k[1], "s⁻¹"),
        ("k3", k[2], "s⁻¹"),
    ]
    for col, (label, value, units) in zip(kc, labels):
        with col:
            metric_card(label, _fmt(float(value), 5), f"{units} at {temperature_c:.1f} °C")

    return {
        "initial_moles_kmol": n0,
        "temperature_c": float(temperature_c),
        "batch_time_s": float(batch_minutes) * 60.0,
        "output_points": int(output_points),
        "volume_model": "constant" if volume_label == "Constant volume" else "composition-dependent",
        "pre_exponential": A,
        "activation_energy_kj_per_kmol": E,
        "molecular_weight_kg_per_kmol": ref.molecular_weight_kg_per_kmol,
        "density_kg_per_m3": ref.density_kg_per_m3,
    }


def _result_cards(result: dict) -> None:
    opt = result["optimum"]
    cols = st.columns(5)
    values = [
        ("Optimum batch time", f"{opt['time_s']/60:.3g} min", f"{opt['time_s']:.1f} s"),
        ("Maximum x3", f"{opt['n_kmol'][3]:.4g} kmol", "desired-product amount"),
        ("x1 conversion", f"{100*opt['conversion_x1']:.2f}%", "at optimum stop time"),
        ("x3 yield", f"{100*opt['yield_x3_on_initial_x1']:.3f}%", "n3 / initial n1"),
        ("Final volume", f"{result['volume_m3'][-1]:.4g} m³", "at end of simulated batch"),
    ]
    for col, (label, value, note) in zip(cols, values):
        with col:
            metric_card(label, value, note, compact=True)


def _plots(result: dict, molecular_weights: np.ndarray) -> None:
    t_min = result["time_s"] / 60.0
    n = result["n_kmol"]
    c = result["c_kmol_m3"]
    rates = result["rates_kmol_m3_s"]
    opt_t_min = result["optimum"]["time_s"] / 60.0
    opt_n3 = result["optimum"]["n_kmol"][3]

    st.markdown("## Dynamic results")

    species_options = [f"{symbol} — {name}" for symbol, name in zip(SPECIES, SPECIES_NAMES)]
    selected_species = st.multiselect(
        "Visible species (amount and concentration plots)",
        options=species_options,
        default=species_options[1:],
        help=(
            "Choose which species are drawn on the two species-trajectory plots. "
            "The solvent x0 is hidden by default because its larger amount can compress the reaction-species curves. "
            "This changes only plot visibility; all species remain in the simulation and diagnostics."
        ),
    )
    selected_indices = [species_options.index(label) for label in selected_species]
    variable = st.selectbox(
        "Additional species plot", ["Existing amount and concentration plots", "Mole fraction", "Mass fraction", "Net conversion", "Overall selectivity"],
        help="Additional quantities are calculated from the solved molar inventories; the reactor model is unchanged.",
    )
    ref_idx = 1
    prod_idx = 3
    ratio = 1.0
    if variable in ("Net conversion", "Overall selectivity"):
        ref_idx = st.selectbox("Reference reactant", range(len(SPECIES)), index=1, format_func=lambda i: species_options[i])
    if variable == "Overall selectivity":
        prod_idx = st.selectbox("Desired product", range(len(SPECIES)), index=3, format_func=lambda i: species_options[i])
        ratio = st.number_input("Theoretical product/reactant molar ratio (stoichiometric basis)", min_value=0.000001, value=1.0)
        st.caption("Overall selectivity = (net product formed / net reactant consumed) / theoretical product/reactant molar ratio. Undefined where there is no positive net reactant disappearance; this is a net-species metric, not reaction-path selectivity.")
    elif variable == "Net conversion":
        st.caption("Net conversion = (initial − current reactant amount) / initial amount; for networks with reactant regeneration, this is net disappearance.")

    if selected_indices:
        fig_n = go.Figure()
        for idx in selected_indices:
            symbol, name = SPECIES[idx], SPECIES_NAMES[idx]
            fig_n.add_trace(go.Scatter(x=t_min, y=n[:, idx], mode="lines", name=f"{symbol} — {name}", line=dict(color=SPECIES_COLORS[symbol])))
        fig_n.add_vline(x=opt_t_min, line_dash="dash", annotation_text="max x3")
        fig_n.update_layout(title="Species amounts through the batch", xaxis_title="Time (min)", yaxis_title="Amount (kmol)")
        st.plotly_chart(_dark(fig_n, 520), use_container_width=True)

        fig_c = go.Figure()
        for idx in selected_indices:
            symbol, name = SPECIES[idx], SPECIES_NAMES[idx]
            fig_c.add_trace(go.Scatter(x=t_min, y=c[:, idx], mode="lines", name=f"{symbol} — {name}", line=dict(color=SPECIES_COLORS[symbol])))
        fig_c.add_vline(x=opt_t_min, line_dash="dash", annotation_text="max x3")
        fig_c.update_layout(title="Species concentrations through the batch", xaxis_title="Time (min)", yaxis_title="Concentration (kmol m⁻³)")
        st.plotly_chart(_dark(fig_c, 500), use_container_width=True)
    else:
        st.info("Select at least one species above to display the amount and concentration trajectory plots.")

    if variable != "Existing amount and concentration plots":
        try:
            values = plot_values(n, molecular_weights, variable, reactant=ref_idx, product=prod_idx, stoich_ratio=ratio)
            fig_extra = go.Figure()
            if values.ndim == 2:
                for idx in selected_indices:
                    fig_extra.add_trace(go.Scatter(x=t_min, y=values[:, idx], mode="lines", name=species_options[idx], line=dict(color=SPECIES_COLORS[SPECIES[idx]])))
            else:
                fig_extra.add_trace(go.Scatter(x=t_min, y=values, mode="lines", name=variable))
            fig_extra.add_vline(x=opt_t_min, line_dash="dash", annotation_text="max x3")
            fig_extra.update_layout(title=variable, xaxis_title="Time (min)", yaxis_title=variable + (" (−)" if variable != "Overall selectivity" else " (molar basis)"))
            st.plotly_chart(_dark(fig_extra, 500), use_container_width=True)
            if values.ndim == 1 and not np.any(np.isfinite(values)):
                st.info("This quantity is undefined over the selected time range.")
        except ValueError as exc:
            st.info(str(exc))

    fig_r = go.Figure()
    for idx, label in enumerate(["r1: 2x1 → x2", "r2: x1 → x3", "r3: x3 → x4"]):
        fig_r.add_trace(go.Scatter(x=t_min, y=rates[:, idx], mode="lines", name=label))
    fig_r.add_vline(x=opt_t_min, line_dash="dash", annotation_text="max x3")
    fig_r.update_layout(title="Reaction rates", xaxis_title="Time (min)", yaxis_title="Reaction rate (kmol m⁻³ s⁻¹)")
    st.plotly_chart(_dark(fig_r, 470), use_container_width=True)

    # A dedicated desired-product plot makes an early optimum visible even when the full batch is long.
    fig_obj = go.Figure()
    fig_obj.add_trace(go.Scatter(x=t_min, y=n[:, 3], mode="lines", name="x3 desired product", line=dict(color=SPECIES_COLORS["x3"])))
    fig_obj.add_trace(go.Scatter(x=[opt_t_min], y=[opt_n3], mode="markers", marker=dict(size=11, color=SPECIES_COLORS["x3"]), name="maximum x3"))
    fig_obj.add_vline(x=opt_t_min, line_dash="dash")
    zoom_end = min(float(t_min[-1]), max(opt_t_min * 6.0, float(t_min[-1]) * 0.08, 1.0))
    fig_obj.update_xaxes(range=[0.0, zoom_end])
    fig_obj.update_layout(
        title="Desired product x3 — stopping-time view",
        xaxis_title="Time (min)",
        yaxis_title="x3 amount (kmol)",
    )
    st.plotly_chart(_dark(fig_obj, 460), use_container_width=True)

    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=t_min, y=result["volume_m3"], mode="lines", name="liquid volume"))
    fig_v.update_layout(title="Liquid volume", xaxis_title="Time (min)", yaxis_title="Volume (m³)")
    st.plotly_chart(_dark(fig_v, 400), use_container_width=True)


def _diagnostics(result: dict, initial_moles: np.ndarray) -> None:
    st.markdown("## Stopping-point and solver diagnostics")
    opt = result["optimum"]
    rows = []
    for idx, (symbol, name) in enumerate(zip(SPECIES, SPECIES_NAMES)):
        rows.append(
            {
                "Species": symbol,
                "Role": name,
                "Initial n (kmol)": initial_moles[idx],
                "n at optimum (kmol)": opt["n_kmol"][idx],
                "Final n (kmol)": result["n_kmol"][-1, idx],
                "c at optimum (kmol m⁻³)": opt["c_kmol_m3"][idx],
            }
        )
    teaching_table(
        [
            "Species",
            "Role",
            "Initial n (kmol)",
            "n at optimum (kmol)",
            "Final n (kmol)",
            "c at optimum (kmol m⁻³)",
        ],
        [
            (
                row["Species"],
                row["Role"],
                f"{row['Initial n (kmol)']:.6g}",
                f"{row['n at optimum (kmol)']:.6g}",
                f"{row['Final n (kmol)']:.6g}",
                f"{row['c at optimum (kmol m⁻³)']:.6g}",
            )
            for row in rows
        ],
        alignments=["left", "left", "center", "center", "center", "center"],
        monospace_columns={2, 3, 4, 5},
    )

    dc = st.columns(4)
    diag = [
        ("Solver", result["method"], result["solver_message"]),
        ("Function evaluations", str(result["nfev"]), "adaptive RK45 evaluations"),
        ("Maximum mass-balance error", f"{100*result['max_mass_error_fraction']:.3e}%", "numerical conservation check"),
        ("Volume model", "Constant" if np.allclose(result["volume_m3"], result["volume_m3"][0]) else "Composition-dependent", f"initial V = {result['initial_volume_m3']:.4g} m³"),
    ]
    for col, (label, value, note) in zip(dc, diag):
        with col:
            metric_card(label, value, note)

    with st.expander("Definitions used for the diagnostic metrics", expanded=False):
        st.latex(r"X_1=\frac{n_{1,0}-n_1}{n_{1,0}}")
        st.latex(r"Y_{x_3}=\frac{n_3}{n_{1,0}}")
        st.latex(r"S_{x_3/(x_2+x_4)}=\frac{n_3}{n_2+n_4}")
        st.markdown(
            "The displayed **x3 yield** is the current amount of desired product divided by the initial reactant amount. The optional product selectivity is a simple molar ratio of desired product to the two undesired product pools; it is provided as a teaching diagnostic, not as a universal selectivity definition for every reaction network."
        )
        if np.isfinite(opt["selectivity_x3_to_undesired_products"]):
            st.markdown(f"At the optimum stop time, $S_{{x_3/(x_2+x_4)}}={opt['selectivity_x3_to_undesired_products']:.4g}$.")
        if np.isfinite(opt["desired_fraction_of_converted_x1"]):
            st.markdown(f"The fraction of reacted $x_1$ currently present as $x_3$ is {100*opt['desired_fraction_of_converted_x1']:.3f}%.")


def render() -> None:
    workspace_header(
        "Isothermal Batch Reactor Simulation",
        "Interactive Van de Vusse batch simulation at fixed reactor temperature using the general stoichiometric-matrix model and SciPy's adaptive solve_ivp integrator.",
        section="Forward Modelling",
        accent=ACCENT,
    )

    chips([
        ("Interactive", "blue"),
        ("Isothermal", "blue"),
        ("Van de Vusse", "blue"),
        ("Multiple reactions", ""),
        ("Arrhenius kinetics", ""),
        ("solve_ivp / RK45", "warn"),
        ("Optimum stopping time", "warn"),
    ])

    _problem_and_method()
    controls = _controls()

    st.markdown("## Simulation results")
    st.caption("The solver reruns whenever an input changes. No data are written to disk.")

    try:
        result = simulate_van_de_vusse(**controls)
    except Exception as exc:
        st.error(f"Simulation could not be completed: {exc}")
        return

    if math.isclose(result["optimum"]["time_s"], controls["batch_time_s"], rel_tol=0.0, abs_tol=max(1e-6, controls["batch_time_s"] / 5000)):
        st.warning("The maximum x3 occurs at the end of the simulated window. Increase the batch duration before interpreting this as a true optimum.")

    _result_cards(result)
    _plots(result, controls["molecular_weight_kg_per_kmol"])
    _diagnostics(result, controls["initial_moles_kmol"])

    st.success(
        "The isothermal model holds reactor temperature constant while integrating the species balances. The results show the influence of the volume assumption, kinetic parameters and batch duration, including the optimum stopping-time diagnostic."
    )

    _suggested_experiments()

    # The historical non-isothermal destination is not part of this standalone app.
    # No link is rendered until a corresponding workspace exists.
