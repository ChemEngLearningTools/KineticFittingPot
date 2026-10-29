from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.ui import chips, navigate, workspace_header


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PDF = ROOT / "data" / "reference" / "Batch reactor model(2C-short)_2021.pdf"


def _concept_card(title: str, body: str, accent: str = "#2dd4bf") -> None:
    st.markdown(
        f"""
        <div class='teaching-card' style='--teach-accent:{accent};'>
            <div class='teaching-card-title'>{title}</div>
            <div class='teaching-card-body'>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _equation_caption(text: str) -> None:
    st.markdown(f"<div class='equation-caption'>{text}</div>", unsafe_allow_html=True)


def render() -> None:
    workspace_header(
        "Batch Reactor Fundamentals",
        "From industrial multipurpose batch operation to the closed, well-mixed dynamic model used for reactor simulation.",
        section="Forward Modelling",
        accent="#2dd4bf",
    )

    chips([
        ("Multipurpose vessel", "blue"),
        ("Dynamic operation", ""),
        ("Liquid phase", ""),
        ("Well mixed", "warn"),
        ("Pure batch starting point", "warn"),
    ])

    st.markdown(
        """
        <div class='learning-objectives'>
            <div class='learning-objectives-title'>Learning path</div>
            <div class='learning-objectives-grid'>
                <div><b>1 · Contextualise</b><br><span>how industrial batch reactors are actually used.</span></div>
                <div><b>2 · Simplify</b><br><span>define the pure-batch, well-mixed model used first.</span></div>
                <div><b>3 · Balance</b><br><span>total mass and individual chemical species.</span></div>
                <div><b>4 · Represent</b><br><span>multiple reactions and kinetic rate laws.</span></div>
                <div><b>5 · Assemble</b><br><span>the ODE system required for simulation.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## What is a batch reactor?")
    st.markdown(
        "A batch reactor is essentially a single, generally **well-mixed vessel** in which a sequence of operations is carried out to manufacture a chemical product. "
        "Unlike a continuous reactor, material does not flow continuously through the vessel during a pure reaction period. The reactor contents therefore evolve with time: "
        "species amounts, concentrations and, when heat effects are included, temperature are inherently **dynamic**."
    )
    st.markdown(
        "Industrial batch reactors are commonly **multipurpose vessels**. The same item of equipment may be used for many different products and may perform much more than the reaction itself. "
        "A batch operation can include charging solvents and reactants, catalyst addition, controlled reagent addition, heating, cooling, reaction, holding, sampling, transfer and discharge. "
        "Separation or purification may occur in the same vessel or elsewhere in the plant."
    )
    st.markdown(
        "Reactor engineering for a batch process therefore involves both **how much material is processed in each batch** and **how the reactor is operated with time**. "
        "The detailed sequence of charging, heating, reaction, cooling, transfer and other steps is commonly described by an **operations list**."
    )
    _concept_card(
        "Why batch processing is useful",
        "Batch and semi-batch processing are particularly important where production must be flexible, product values are high, production volumes are moderate, or the same plant must manufacture many different products. "
        "Continuous processing remains especially important for large-volume commodity production.",
        "#38bdf8",
    )

    st.markdown("## Pure batch and semi-batch operation")
    st.markdown(
        "In a **pure batch reaction**, all reacting material is charged before the reaction period begins and there is no intentional material flow into or out of the reactor while reaction proceeds."
    )
    st.markdown(
        "In **semi-batch operation**, some material is charged initially while one or more additional reactants are added progressively during the reaction. "
        "Controlled addition can be used to influence reaction rate, selectivity, temperature and the amount of reactive material accumulated in the vessel."
    )
    st.markdown(
        "Industrially, both modes are normally regarded as batch processes. KineticFittingPot begins with pure batch operation because it provides the cleanest route to the closed species balances; "
        "in fed-batch operation the feed term is retained, allowing controlled addition to become an operating variable."
    )

    st.markdown("## What does a real batch reactor look like?")
    st.markdown(
        "Commercial batch reactors are commonly fabricated from steel or stainless steel and, where additional chemical resistance is required, may use a **glass-lined internal surface**. "
        "A typical vessel includes charging and instrumentation connections, agitation, a bottom discharge, and an external jacket or other heat-transfer surface for heating and cooling."
    )
    st.markdown(
        "Heating or cooling fluid is circulated through the jacket so that heat can be transferred between the reactor contents and the utility system. "
        "Agitation promotes mixing within the vessel and strongly affects process-side heat and mass transfer. Commercial equipment spans a wide range of scales, from laboratory and pilot vessels to large production reactors."
    )
    st.caption("Heat-transfer limitations, jackets and utility-system design are outside the scope of this isothermal batch model.")
    st.link_button("Industrial reactor examples — Pfaudler", "https://www.pfaudler.com/")

    st.markdown("## From industrial operation to the isothermal batch model")
    st.markdown(
        """
**Industrial batch process** — many operations may occur: charge, controlled addition, heating/cooling, reaction, hold, sampling, transfer and discharge.

↓

**Model considered here** — a closed, well-mixed, liquid-phase, isothermal **pure batch** during the reaction period.

↓

**Scope of the present model** — isothermal closed-batch operation. Non-isothermal and fed-batch systems require additional energy and material-balance terms.
        """
    )
    _concept_card(
        "Why start with the simplified model?",
        "The pure-batch model isolates the relationship between <b>stoichiometry, kinetics, species inventory, concentration and time</b>. "
        "Once those ideas are clear, energy balances, cooling-system dynamics, feedback control and semi-batch feeds can be added without hiding the underlying reactor model.",
        "#a78bfa",
    )
    _concept_card(
        "Why model a batch reactor?",
        "The design problem is not only how much product is eventually formed. We often want to know <b>how fast</b> reactants disappear, "
        "when a desired product reaches its maximum, how long a batch should run, and whether heat released or absorbed by reaction can be handled safely.",
        "#2dd4bf",
    )
    st.markdown(
        "From this point, the treatment assumes a **liquid-phase reacting system**, a **perfectly mixed vessel** and a **pure-batch reaction period**. "
        "The formulation remains general: several species may participate in several simultaneous reactions."
    )

    st.markdown("## Overall mass balance")
    st.markdown(
        "For any dynamic system, accumulation equals inflow minus outflow. For the **pure-batch reaction period** considered in this workspace, "
        "there is no material flow into or out of the vessel after the initial charge. Total mass is therefore conserved."
    )
    _equation_caption("Overall batch-reactor mass balance")
    st.latex(r"\frac{d(\rho V)}{dt}=0")
    st.markdown(
        "Here, $V$ is the liquid volume and $\\rho$ is the liquid density. If density remains constant, the liquid volume is also constant:"
    )
    st.latex(r"\rho\frac{dV}{dt}=0 \qquad \Rightarrow \qquad \frac{dV}{dt}=0")
    st.markdown("More generally, when density changes as reaction proceeds:")
    st.latex(r"\rho\frac{dV}{dt}+V\frac{d\rho}{dt}=0")
    _concept_card(
        "Modelling choice",
        "A constant-volume model is often useful, but it is an <b>assumption</b>. The simulator offers a composition-dependent volume option so that this assumption can be examined explicitly.",
        "#f59e0b",
    )

    st.markdown("### Volume of liquid in the vessel")
    st.markdown("If component volumes are assumed to be additive, the reacting-liquid volume can be calculated from the current species inventory:")
    st.latex(r"V=\sum_{j=1}^{N_S}\frac{m_j}{\rho_j}=\sum_{j=1}^{N_S}\frac{n_jM_j}{\rho_j}")
    st.markdown(
        "where $n_j$ is the amount of species $j$, $M_j$ its molecular weight, $\\rho_j$ its density and $N_S$ the total number of chemical species. "
        "Because the $n_j$ values evolve during reaction, this expression can produce a changing liquid volume even though total mass remains constant."
    )

    st.markdown("## Species component balances")
    st.markdown(
        "Total mass is conserved, but individual chemical species are not. A reactant can be consumed and a product can be formed. "
        "For species $j$, the general balance is accumulation = inflow − outflow + net generation. In the pure-batch reaction period the flow terms vanish; a fed-batch model includes the inlet term explicitly."
    )
    _equation_caption("Core species balance")
    st.latex(r"\boxed{\frac{dn_j}{dt}=V R_j}")
    st.markdown(
        "$R_j$ is the **net rate of production** of species $j$ per unit reactor volume. It can be positive for net production, negative for net consumption, or zero."
    )
    _concept_card(
        "Why moles are useful",
        "The state of the dynamic batch model can be represented by the vector of species amounts. Concentrations then follow from the current amounts and volume, which is convenient when density or volume changes with composition.",
        "#a78bfa",
    )

    st.markdown("## Species participation in multiple reactions")
    st.markdown(
        "For several simultaneous reactions, it is helpful to separate **which species exist** from **how each species participates in each reaction**. "
        "Let $\\mathbf{B}=(x_1,\\ldots,x_{N_S})$ denote the species set. Reactant and product stoichiometric matrices, $\\mathbf{S}_R$ and $\\mathbf{S}_P$, then describe the reaction network."
    )
    st.markdown("Consider the three reactions:")
    st.latex(r"2x_1\rightarrow x_2")
    st.latex(r"x_1\rightarrow x_3")
    st.latex(r"x_3\rightarrow x_4")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Reactant stoichiometric matrix**")
        st.latex(r"\mathbf{S}_R=\begin{bmatrix}2&1&0\\0&0&0\\0&0&1\\0&0&0\end{bmatrix}")
    with col2:
        st.markdown("**Product stoichiometric matrix**")
        st.latex(r"\mathbf{S}_P=\begin{bmatrix}0&0&0\\1&0&0\\0&1&0\\0&0&1\end{bmatrix}")
    st.markdown(
        "Each **column** corresponds to a reaction and each **row** to a species. This representation becomes particularly useful when reaction networks are too large to manage safely as separate handwritten balance equations."
    )

    st.markdown("## Chemical reaction rates")
    st.markdown(
        "Reaction rates are generally nonlinear functions of composition. For an ideal, well-mixed liquid system, the notes introduce **mass-action kinetics**, "
        "where the rate of reaction $i$ is proportional to the product of reactant concentrations raised to their reactant stoichiometric powers."
    )
    _equation_caption("Mass-action reaction rate")
    st.latex(r"r_i=k_i\prod_{j=1}^{N_S}c_j^{\,s_{R,j,i}}")
    st.markdown(
        "The units of the rate constant $k_i$ depend on the overall reaction order. By contrast, a volumetric reaction rate retains concentration-per-time units, "
        "for example $\\mathrm{kmol\\,m^{-3}\\,s^{-1}}$."
    )

    st.markdown("### Temperature dependence of the rate constant")
    st.markdown("The rate constant normally changes strongly with temperature and is commonly represented using the Arrhenius relationship:")
    st.latex(r"\boxed{k_i=A_i\exp\!\left(-\frac{E_i}{RT}\right)}")
    cols = st.columns(4)
    labels = [
        ("A<sub>i</sub>", "frequency / pre-exponential factor"),
        ("E<sub>i</sub>", "activation energy"),
        ("<i>R</i>", "gas constant"),
        ("<i>T</i>", "absolute temperature"),
    ]
    for col, (symbol, meaning) in zip(cols, labels):
        with col:
            st.markdown(f"<div class='symbol-card'><div class='symbol-main'>{symbol}</div><div class='symbol-desc'>{meaning}</div></div>", unsafe_allow_html=True)
    _concept_card(
        "Link to kinetic fitting",
        "Forward simulation assumes kinetic parameters are known. Kinetic fitting reverses the problem: experimental concentration–time or rate data are used to estimate <i>k</i>, and multi-temperature measurements can then be used to estimate Arrhenius parameters.",
        "#2dd4bf",
    )

    st.markdown("## Rate of production and consumption of species")
    st.markdown("Define the **net stoichiometric matrix** as the product matrix minus the reactant matrix:")
    st.latex(r"\boxed{\mathbf{S}=\mathbf{S}_P-\mathbf{S}_R}")
    st.markdown(
        "By convention, a negative coefficient identifies net consumption of a species in a reaction, a positive coefficient identifies net production, "
        "and zero means the species has no net change in that reaction."
    )
    st.markdown("The net production rate of species $j$ is therefore:")
    st.latex(r"R_j=\sum_{i=1}^{N_R}s_{j,i}r_i")
    st.markdown("Substituting this into the species balance gives the general dynamic batch-reactor model:")
    _equation_caption("Simulation-ready batch-reactor ODE")
    st.latex(r"\boxed{\frac{dn_j}{dt}=V\sum_{i=1}^{N_R}s_{j,i}r_i}")
    st.markdown("For all species together this can be written compactly as:")
    st.latex(r"\boxed{\frac{d\mathbf{n}}{dt}=V\,\mathbf{S}\,\mathbf{r}}")

    st.markdown("### From model state to time derivative")
    st.latex(
        r"\mathbf n(t)\;\longrightarrow\;V,\mathbf c\;\longrightarrow\;"
        r"\mathbf r(\mathbf c,T)\;\longrightarrow\;\mathbf S\mathbf r\;\longrightarrow\;"
        r"\frac{d\mathbf n}{dt}"
    )
    flow_cols = st.columns(5)
    flow_text = [
        ("Species amounts", "current reactor state"),
        ("Volume & concentrations", "calculate composition"),
        ("Reaction rates", "evaluate kinetics"),
        ("Production rates", "apply stoichiometry"),
        ("ODE derivative", "return to integrator"),
    ]
    for col, (title, caption) in zip(flow_cols, flow_text):
        with col:
            st.markdown(f"**{title}**")
            st.caption(caption)

    st.markdown("## From fundamentals to simulation")
    st.markdown(
        "The material above provides the basis for the built-in batch simulator: define the species and reaction network, "
        "construct the stoichiometric matrix, calculate concentrations, evaluate reaction rates and integrate the resulting ODEs through batch time."
    )
    st.markdown(
        "The built-in simulator uses the **Van de Vusse reaction network** from the next section of the notes as a built-in example, while keeping the underlying implementation general enough for multiple species and multiple reactions."
    )
    if st.button("Open Isothermal Batch Reactor Simulation →", key="open_batch_sim_method"):
        navigate("Isothermal Batch Reactor Simulation")

    st.divider()
    st.markdown("### Source notes")
    st.caption(
        "The mathematical development on this page is adapted from the supplied 2021 Batch reactor models notes through the general species production/consumption formulation. "
        "The opening industrial context has been added to connect that model to practical multipurpose batch operation. The original document is preserved separately; source figures are intentionally omitted from this web presentation."
    )
    if SOURCE_PDF.exists():
        st.download_button(
            "Download original batch-reactor notes (PDF)",
            data=SOURCE_PDF.read_bytes(),
            file_name=SOURCE_PDF.name,
            mime="application/pdf",
            key="download_batch_notes",
        )
