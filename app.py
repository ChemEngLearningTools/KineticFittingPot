from __future__ import annotations

import streamlit as st
from modules import (about, batch_reactors, batch_simulation, conversion_yield_selectivity, custom_model_simulation, home, kinetic_fitting, kinetic_fitting_case_study, kinetic_fitting_fundamentals, model_diagnostics, basic_model_diagnostics, model_diagnostics_fundamentals, numerical_ode_fundamentals, reaction_stoichiometry_fundamentals)
from utils.deployment import PUBLIC_CONTACT_EMAIL, is_public_cloud, render_public_cloud_lock
from utils.ui import apply_theme

st.set_page_config(page_title="KineticFittingPot", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

def _locked_fit():
    render_public_cloud_lock(title="Kinetic Parameter Fitting", description="Fit selected model parameters simultaneously across multiple experimental datasets using bounded multistart nonlinear least squares.", section="Kinetic Fitting", accent="#f59e0b", kind="fitting")

def _locked_diag():
    render_public_cloud_lock(title="Advanced Model Diagnostics", description="Challenge a completed kinetic fit using stoichiometric, residual, local parameter and profiled-objective diagnostics.", section="Model Diagnostics", accent="#22c55e", kind="diagnostics")

FIT = kinetic_fitting.render
DIAG = _locked_diag if is_public_cloud() else model_diagnostics.render

PAGES = {
    "Home": home.render,
    "Reaction Stoichiometry Fundamentals": reaction_stoichiometry_fundamentals.render,
    "Conversion, Yield and Selectivity": conversion_yield_selectivity.render,
    "Numerical Solution of Differential Equations": numerical_ode_fundamentals.render,
    "Batch Reactor Fundamentals": batch_reactors.render,
    "Isothermal Batch Reactor Simulation": batch_simulation.render,
    "Simulate Your Own Model — Isothermal Batch Reactor": custom_model_simulation.render,
    "Kinetic Fitting Fundamentals": kinetic_fitting_fundamentals.render,
    "Kinetic Fitting Case Study — Biodiesel": kinetic_fitting_case_study.render,
    "Kinetic Parameter Fitting": FIT,
    "Model Diagnostics Fundamentals": model_diagnostics_fundamentals.render,
    "Basic Model Diagnostics": basic_model_diagnostics.render,
    "Advanced Model Diagnostics": DIAG,
    "Post-fit Model Diagnostics": DIAG,  # backward-compatible navigation
    "About KineticFittingPot": about.render,
}

apply_theme()
if "page" not in st.session_state or st.session_state["page"] not in PAGES:
    st.session_state["page"] = "Home"
try:
    qp = st.query_params.get("page")
    if isinstance(qp, list): qp = qp[0] if qp else None
    if qp in PAGES: st.session_state["page"] = str(qp)
except Exception:
    pass

try:
    PAGES[st.session_state["page"]]()
except Exception as exc:
    st.error("KineticFittingPot encountered an error while rendering this workspace.")
    if is_public_cloud():
        st.info(f"Please try again. If the problem persists, contact [{PUBLIC_CONTACT_EMAIL}](mailto:{PUBLIC_CONTACT_EMAIL}) and include the workspace name and what you were doing when the error occurred.")
    else:
        with st.expander("Technical details"):
            st.exception(exc)
