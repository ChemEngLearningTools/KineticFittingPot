from __future__ import annotations

import html
from urllib.parse import quote
import streamlit as st

# Activity-led home: all existing scientific workspaces remain in app.py.
MAIN_SIMULATION = [
    ("Isothermal Batch Reactor Simulation", "Guided simulation", "Explore an established Van de Vusse reaction network, kinetics and reactor response."),
    ("Simulate Your Own Model — Isothermal Batch Reactor", "Excel-defined model", "Define your own reaction network in a workbook and simulate it without writing Python."),
]
MAIN_FITTING = [
    ("Kinetic Parameter Fitting", "Parameter estimation", "Estimate shared kinetic parameters using experimental datasets and numerical optimisation."),
    ("Basic Model Diagnostics", "Post-fit assessment", "Inspect fitted results, residuals and stoichiometric consistency without repeating the optimisation."),
]
DIAGNOSTICS = [
    ("Advanced Model Diagnostics", "Local-only analysis", "Data reconciliation, local parameter analysis and profiled-objective diagnostics."),
]
CASE_STUDIES = [
    ("Kinetic Fitting Case Study — Biodiesel", "Worked case study", "Follow a complete biodiesel parameter-fitting case study."),
]
LEARNING = [
    ("Reaction Stoichiometry Fundamentals", "Fundamentals", "Reaction vectors, stoichiometric coefficients and species balances."),
    ("Conversion, Yield and Selectivity", "Fundamentals", "Performance measures for parallel and consecutive reactions."),
    ("Numerical Solution of Differential Equations", "Numerical methods", "Integration methods, numerical accuracy and discontinuities."),
    ("Batch Reactor Fundamentals", "Fundamentals", "Batch reactor balances and isothermal kinetic models."),
    ("Kinetic Fitting Fundamentals", "Fundamentals", "Formulating dynamic kinetic parameter estimation."),
    ("Model Diagnostics Fundamentals", "Fundamentals", "Interpreting residuals, consistency and parameter uncertainty."),
]

def _card(page: str, label: str, description: str) -> None:
    st.markdown(
        f"<a class='stack-card-link' href='?page={quote(page)}' target='_self'>"
        f"<div class='stack-card'><div class='stack-kicker'>{html.escape(label)}</div>"
        f"<div class='stack-title'>{html.escape(page)}</div>"
        f"<div class='stack-desc'>{html.escape(description)}</div>"
        f"<div class='stack-open'>Open workspace →</div></div></a>",
        unsafe_allow_html=True,
    )

def render() -> None:
    st.markdown(
        "<div class='workspace-title-card kfp-home-title'>"
        "<div class='workspace-title'>KineticFittingPot</div>"
        "<div class='workspace-desc'>Reaction model simulation, kinetic parameter estimation and model diagnostics</div>"
        "</div>", unsafe_allow_html=True,
    )
    st.markdown("<div class='home-active-section'>MAIN WORKSPACES</div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap='medium')
    with left:
        st.markdown("#### Simulation")
        for page, kind, desc in MAIN_SIMULATION:
            _card(page, kind, desc)
    with right:
        st.markdown("#### Kinetic fitting")
        for page, kind, desc in MAIN_FITTING:
            _card(page, kind, desc)

    st.markdown("<div class='home-active-section'>FURTHER ANALYSIS</div>", unsafe_allow_html=True)
    for page, kind, desc in DIAGNOSTICS:
        _card(page, kind, desc)

    st.markdown("<div class='home-active-section'>CASE STUDIES</div>", unsafe_allow_html=True)
    st.caption("Worked applications of simulation, parameter estimation and interpretation. Additional case studies can be added here.")
    for page, kind, desc in CASE_STUDIES:
        _card(page, kind, desc)

    st.markdown("<div class='home-active-section'>LEARNING & REFERENCE</div>", unsafe_allow_html=True)
    st.caption("Supporting theory and reference material, available without leaving the application.")
    c1, c2 = st.columns(2, gap='medium')
    for i, (page, kind, desc) in enumerate(LEARNING):
        with (c1 if i % 2 == 0 else c2):
            _card(page, kind, desc)
    st.divider()
    if st.button("About KineticFittingPot", key="home_about"):
        st.session_state["page"] = "About KineticFittingPot"
        try:
            st.query_params["page"] = "About KineticFittingPot"
        except Exception:
            pass
        st.rerun()
