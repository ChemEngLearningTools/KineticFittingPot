from __future__ import annotations

import streamlit as st
from utils.deployment import PUBLIC_CONTACT_EMAIL, is_public_cloud
from utils.ui import workspace_header


def render() -> None:
    workspace_header(
        "About KineticFittingPot",
        "A chemical-engineering teaching application for dynamic kinetic modelling, parameter fitting and model diagnostics.",
        section="About", accent="#f59e0b",
    )
    st.markdown("""
KineticFittingPot is designed to make the complete kinetic-modelling workflow visible rather than treat parameter estimation as a black box.

The teaching sequence is:

**reaction fundamentals → isothermal batch modelling → user-defined forward model → kinetic fitting → post-fit diagnostics**.

The built-in Van de Vusse batch model provides a transparent reference problem. The general Excel-defined model then allows a reaction network, parameters, rate expressions and stoichiometry to be specified without writing Python code. The same model definition is reused for fitting and diagnostics.

### Availability and scope

The publicly deployed application provides batch simulation, kinetic parameter fitting and Basic Model Diagnostics, subject to computational safeguards that protect shared server resources. Advanced Model Diagnostics are available in the local version; they are not available in the public deployment.

### Developer and contact

KineticFittingPot is developed by **Mark Willis** as part of the **Chemical Engineering Learning Tools** collection of interactive teaching applications.
""")
    st.markdown(f"**Contact and feedback:** [{PUBLIC_CONTACT_EMAIL}](mailto:{PUBLIC_CONTACT_EMAIL})")
    st.markdown("**Project website:** [Chemical Engineering Learning Tools](https://chemenglearningtools.github.io/)")
    st.markdown("""
Questions, suggestions, bug reports and enquiries about educational use are welcome. When reporting a problem, please include the workspace, input or example case, and a brief description of what happened.

### Educational and research use

KineticFittingPot is an educational and research-support tool. Model structure, units, experimental design, numerical accuracy, parameter identifiability and physical interpretation remain the responsibility of the user. Numerical convergence alone does not establish that a fitted model is physically valid or that its parameters are uniquely identifiable.
""")
