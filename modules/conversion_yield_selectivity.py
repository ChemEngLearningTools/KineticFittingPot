from __future__ import annotations

import streamlit as st

from utils.ui import chips, navigate, teaching_table, workspace_header


ACCENT = "#38bdf8"


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


def _equation_caption(text: str) -> None:
    st.markdown(f"<div class='equation-caption'>{text}</div>", unsafe_allow_html=True)


def render() -> None:
    workspace_header(
        "Conversion, Yield and Selectivity",
        "Distinguish cumulative conversion from instantaneous and overall yield/selectivity, then use stoichiometric dependencies to extract rate-free information from batch data.",
        section="Fundamentals",
        accent=ACCENT,
    )

    chips([
        ("Learning", "blue"),
        ("Conversion", ""),
        ("Instantaneous metrics", "blue"),
        ("Overall metrics", "warn"),
        ("Parallel & series reactions", ""),
        ("Rate-free data checks", "warn"),
    ])

    st.markdown(
        """
        <div class='learning-objectives'>
            <div class='learning-objectives-title'>Learning path</div>
            <div class='learning-objectives-grid'>
                <div><b>1 · Convert</b><br><span>measure how much reactant has disappeared.</span></div>
                <div><b>2 · Distinguish</b><br><span>instantaneous rates from accumulated outcomes.</span></div>
                <div><b>3 · Compare</b><br><span>desired and undesired pathways.</span></div>
                <div><b>4 · Generalise</b><br><span>parallel and series reaction networks.</span></div>
                <div><b>5 · Exploit</b><br><span>stoichiometric dependencies without kinetics.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Conversion: how much reactant has disappeared?")
    st.markdown(
        "For a closed batch reactor, conversion is most generally defined from **mole amounts**. "
        "For reactant $A$, the conversion at time $t$ is"
    )
    _equation_caption("Reactant conversion")
    st.latex(r"\boxed{X_A(t)=\frac{n_{A0}-n_A(t)}{n_{A0}}}")
    st.markdown(
        "A conversion of 0 means none of the initial reactant has been consumed; a conversion of 1 means all of the initial reactant has disappeared. "
        "Conversion says nothing by itself about **which products were formed**."
    )
    _concept_card(
        "Why KineticFittingPot starts from moles",
        "For a constant-volume batch, the same expression may be written using concentrations. Using moles is more general because it remains valid when reactor volume changes; concentration changes can then reflect both reaction and changing volume.",
        "#2dd4bf",
    )
    st.latex(r"V=\mathrm{constant}\quad\Longrightarrow\quad X_A=\frac{C_{A0}-C_A}{C_{A0}}")

    st.markdown("## From reaction rates to species rates")
    st.markdown(
        r"The previous Fundamentals workspace introduced the stoichiometric matrix $\mathbf S$ and reaction-rate vector $\mathbf r$. "
        "Their product gives the net species formation rates per unit volume:"
    )
    st.latex(r"\boxed{\mathbf R=\mathbf S\mathbf r}")
    st.latex(r"\frac{d\mathbf n}{dt}=V\mathbf R=V\mathbf S\mathbf r")
    st.markdown(
        "This is the bridge to instantaneous performance. Stoichiometry tells us how each reaction contributes to each species; kinetics determines the current reaction rates, and therefore the current net formation or consumption rates."
    )

    st.markdown("## Instantaneous yield and selectivity")
    st.markdown(
        "Suppose $A$ is the reactant, $D$ is the desired product and $U$ is an undesired product. "
        "An **instantaneous yield** asks what the chemistry is doing **right now**."
    )
    _equation_caption("Instantaneous desired-product yield")
    st.latex(
        r"\boxed{Y_{D/A}^{\mathrm{inst}}="
        r"\frac{dn_D/dt}{-dn_A/dt}="
        r"\frac{R_D}{-R_A}}"
    )
    st.markdown(
        "When $A$ is being consumed, this is the current net formation of $D$ per mole of $A$ disappearing. "
        "The common reactor volume cancels from the ratio."
    )
    _equation_caption("Instantaneous desired/undesired selectivity")
    st.latex(
        r"\boxed{S_{D/U}^{\mathrm{inst}}="
        r"\frac{dn_D/dt}{dn_U/dt}="
        r"\frac{R_D}{R_U}}"
    )
    _concept_card(
        "Instantaneous means local in time",
        "Instantaneous yield and selectivity are built from current species rates. They can change continuously during a batch because the reaction-rate vector changes as composition and, in non-isothermal systems, temperature change.",
        "#f59e0b",
    )

    st.markdown("## Overall yield and selectivity")
    st.markdown(
        r"Overall metrics describe everything that has accumulated between the initial state and the current or final state. Define $\Delta n_i=n_i-n_{i0}$."
    )
    _equation_caption("Overall desired-product yield")
    st.latex(r"\boxed{\widetilde Y_{D/A}=\frac{\Delta n_D}{-\Delta n_A}}")
    _equation_caption("Overall desired/undesired selectivity")
    st.latex(r"\boxed{\widetilde S_{D/U}=\frac{\Delta n_D}{\Delta n_U}}")
    teaching_table(
        ["Metric", "Uses", "Question answered"],
        [
            ["Conversion", "Current inventory", "How much reactant has disappeared?"],
            ["Instantaneous yield/selectivity", "Current species rates", "What is the reaction doing now?"],
            ["Overall yield/selectivity", "Accumulated mole changes", "What has the batch achieved so far?"],
        ],
        alignments=["left", "center", "left"],
    )
    _concept_card(
        "Key distinction",
        "A batch can have a favourable overall yield because useful product accumulated earlier, while its instantaneous yield is poor — or even negative — because that product is currently being consumed by a later reaction.",
        "#a78bfa",
    )
    _concept_card(
        "KineticFittingPot definition convention",
        "Yield and selectivity terminology varies between textbooks and industries. On this page, yield is a <b>net molar product change per mole of reactant consumed</b>, and selectivity is a <b>molar desired/undesired ratio</b>. Any stoichiometric normalisation is shown explicitly rather than hidden in the definition. Instantaneous ratios are undefined when their denominator is zero and may become negative when a nominal product is being consumed.",
        "#38bdf8",
    )

    st.markdown("## Parallel reactions: desired versus undesired pathways")
    st.markdown("Consider two parallel reactions:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Reaction 1 — desired path**")
        st.latex(r"\nu_{A1}A\rightarrow D")
    with c2:
        st.markdown("**Reaction 2 — undesired path**")
        st.latex(r"\nu_{A2}A\rightarrow U")

    st.markdown("With species ordering $[A,D,U]^T$,")
    st.latex(
        r"\mathbf S="
        r"\begin{bmatrix}"
        r"-\nu_{A1}&-\nu_{A2}\\"
        r"1&0\\"
        r"0&1"
        r"\end{bmatrix}"
    )
    st.latex(
        r"R_A=-\nu_{A1}r_1-\nu_{A2}r_2,\qquad "
        r"R_D=r_1,\qquad R_U=r_2"
    )
    st.markdown("The instantaneous yields therefore become")
    st.latex(
        r"Y_{D/A}^{\mathrm{inst}}="
        r"\frac{r_1}{\nu_{A1}r_1+\nu_{A2}r_2},\qquad "
        r"Y_{U/A}^{\mathrm{inst}}="
        r"\frac{r_2}{\nu_{A1}r_1+\nu_{A2}r_2}"
    )
    st.latex(
        r"\boxed{\nu_{A1}Y_{D/A}^{\mathrm{inst}}+"
        r"\nu_{A2}Y_{U/A}^{\mathrm{inst}}=1}"
    )
    st.markdown("and the instantaneous desired/undesired selectivity is")
    st.latex(r"\boxed{S_{D/U}^{\mathrm{inst}}=\frac{r_1}{r_2}}")
    st.markdown(
        "This makes the kinetic meaning of selectivity explicit: for competing parallel pathways, changing temperature or composition can change $r_1/r_2$ and therefore change which product is favoured."
    )
    st.markdown("Integrating the same mole balance across the batch gives")
    st.latex(
        r"\boxed{\nu_{A1}\widetilde Y_{D/A}+"
        r"\nu_{A2}\widetilde Y_{U/A}=1}"
    )
    st.caption(
        "For the common unit-stoichiometry case A → D and A → U, the desired and undesired yields sum to one, both instantaneously and overall, provided these are the only routes consuming A."
    )

    st.markdown("## Series reactions: when the desired product starts disappearing")
    st.markdown("Now consider an intermediate desired product:")
    st.latex(r"A\xrightarrow{r_1}D\xrightarrow{r_2}U")
    st.latex(
        r"\mathbf S="
        r"\begin{bmatrix}"
        r"-1&0\\"
        r"1&-1\\"
        r"0&1"
        r"\end{bmatrix}"
    )
    st.latex(r"R_A=-r_1,\qquad R_D=r_1-r_2,\qquad R_U=r_2")
    st.markdown("The instantaneous yields relative to reactant consumption are")
    st.latex(
        r"\boxed{Y_{D/A}^{\mathrm{inst}}=1-\frac{r_2}{r_1}},\qquad "
        r"\boxed{Y_{U/A}^{\mathrm{inst}}=\frac{r_2}{r_1}}"
    )
    st.latex(r"Y_{D/A}^{\mathrm{inst}}+Y_{U/A}^{\mathrm{inst}}=1")
    _concept_card(
        "A useful diagnostic",
        "If <i>r</i><sub>2</sub> exceeds <i>r</i><sub>1</sub>, the desired intermediate D is disappearing faster than it is being formed. Its instantaneous net yield is then negative even though its overall yield can still be positive because D accumulated earlier in the batch.",
        "#fb7185",
    )

    st.markdown("## Stoichiometric dependencies: what can be learned without kinetics?")
    st.markdown(
        "The yield/selectivity definitions use rates, but the stoichiometric matrix contains an additional kind of information that does **not** require a kinetic model. "
        "For a closed batch reactor define the differential reaction-extent vector"
    )
    st.latex(r"d\boldsymbol\xi=V\mathbf r\,dt")
    st.markdown("Then the species balances reduce to the purely stoichiometric relationship")
    _equation_caption("Differential stoichiometric balance")
    st.latex(r"\boxed{d\mathbf n=\mathbf S\,d\boldsymbol\xi}")
    st.markdown(
        r"This equation contains no rate constants, reaction orders or Arrhenius parameters. It says that every physically possible composition change generated by the assumed reaction network must lie in the column space of $\mathbf S$."
    )

    st.markdown("### Partition the species")
    st.markdown(
        r"For a full-column-rank network, choose as many **key species** as there are independent reaction columns so that their square stoichiometric submatrix $\mathbf S_K$ is invertible. "
        r"Place the remaining species in a dependent block $\mathbf n_{\mathrm{dep}}$:"
    )
    st.latex(
        r"\begin{bmatrix}d\mathbf n_K\\d\mathbf n_{\mathrm{dep}}\end{bmatrix}="
        r"\begin{bmatrix}\mathbf S_K\\\mathbf S_{\mathrm{dep}}\end{bmatrix}d\boldsymbol\xi"
    )
    st.latex(r"d\boldsymbol\xi=\mathbf S_K^{-1}d\mathbf n_K")
    st.latex(
        r"\boxed{d\mathbf n_{\mathrm{dep}}="
        r"\underbrace{\mathbf S_{\mathrm{dep}}\mathbf S_K^{-1}}_{\boldsymbol\Phi}"
        r"d\mathbf n_K}"
    )
    _concept_card(
        "Stoichiometric dependency matrix",
        "KineticFittingPot denotes <b>Φ = S<sub>dep</sub>S<sub>K</sub><sup>−1</sup></b>. Φ is fixed by the chosen reaction network and species partition. It is <b>not</b> an instantaneous-yield matrix: it is a structural map showing how dependent species changes are constrained by a set of independent species changes.",
        "#2dd4bf",
    )
    st.markdown(r"Because $\mathbf S$ is fixed, the relationship integrates directly:")
    st.latex(r"\boxed{\Delta\mathbf n_{\mathrm{dep}}=\boldsymbol\Phi\,\Delta\mathbf n_K}")

    st.markdown("### Van de Vusse worked dependency")
    st.markdown("For the four reacting Van de Vusse species,")
    st.latex(
        r"\mathbf S="
        r"\begin{bmatrix}"
        r"-2&-1&0\\"
        r"1&0&0\\"
        r"0&1&-1\\"
        r"0&0&1"
        r"\end{bmatrix},\qquad \operatorname{rank}(\mathbf S)=3"
    )
    st.markdown(
        "Choose $x_2$, $x_3$ and $x_4$ as the key species. Their rows form"
    )
    st.latex(
        r"\mathbf S_K="
        r"\begin{bmatrix}"
        r"1&0&0\\"
        r"0&1&-1\\"
        r"0&0&1"
        r"\end{bmatrix},\qquad "
        r"\mathbf S_K^{-1}="
        r"\begin{bmatrix}"
        r"1&0&0\\"
        r"0&1&1\\"
        r"0&0&1"
        r"\end{bmatrix}"
    )
    st.markdown("The remaining species is $x_1$, with")
    st.latex(r"\mathbf S_{\mathrm{dep}}=\begin{bmatrix}-2&-1&0\end{bmatrix}")
    st.latex(
        r"\boxed{\boldsymbol\Phi=\mathbf S_{\mathrm{dep}}\mathbf S_K^{-1}="
        r"\begin{bmatrix}-2&-1&-1\end{bmatrix}}"
    )
    st.markdown("Therefore every valid Van de Vusse trajectory must satisfy")
    st.latex(r"\boxed{dn_1=-2\,dn_2-dn_3-dn_4}")
    st.markdown("or, after integration from the initial state,")
    st.latex(r"\boxed{\Delta n_1=-2\Delta n_2-\Delta n_3-\Delta n_4}")
    st.markdown("which can also be written as the invariant")
    st.latex(r"\boxed{n_1+2n_2+n_3+n_4=\mathrm{constant}}")
    _concept_card(
        "Why this matters",
        "This relationship is true for the Van de Vusse reaction network regardless of the values of <i>k</i><sub>1</sub>, <i>k</i><sub>2</sub> and <i>k</i><sub>3</sub>, regardless of the kinetic rate laws used to evaluate the reaction rates, and regardless of how quickly the batch moves along the trajectory.",
        "#38bdf8",
    )

    st.markdown("### 1 · Reconstruct an unmeasured species")
    st.markdown(
        "If $x_2$ is not measured but $x_1$, $x_3$ and $x_4$ are available, the invariant can be rearranged to give"
    )
    st.latex(
        r"\boxed{\Delta n_2=-\frac{1}{2}\left(\Delta n_1+\Delta n_3+\Delta n_4\right)}"
    )
    st.latex(
        r"n_2(t)=n_{2,0}-\frac12\left[(n_1-n_{1,0})+(n_3-n_{3,0})+(n_4-n_{4,0})\right]"
    )
    st.markdown(
        "This is a **stoichiometric reconstruction**, not a kinetic prediction. It can be useful when one species is unavailable, but measurement noise from all contributing signals is propagated into the reconstructed value."
    )

    st.markdown("### 2 · Reduce the ODE set")
    st.markdown(
        "The reacting Van de Vusse system has four species but only three independent reaction directions. One reacting-species balance can therefore be replaced by the algebraic dependency. "
        "For example, solve for $n_2$, $n_3$ and $n_4$ and reconstruct $n_1$:"
    )
    st.latex(
        r"\boxed{n_1=n_{1,0}-2(n_2-n_{2,0})-(n_3-n_{3,0})-(n_4-n_{4,0})}"
    )
    st.caption(
        "KineticFittingPot currently keeps the full species ODE set because it is transparent and computationally inexpensive for the teaching models. The reduction is nevertheless useful conceptually and can matter in larger models."
    )

    st.markdown("### 3 · Validate measured data against stoichiometry — without rates")
    st.markdown(
        "If all four reacting species are measured, define a stoichiometric consistency residual at each sampling time:"
    )
    st.latex(
        r"\boxed{\varepsilon_{\mathrm{stoich}}(t)="
        r"\Delta n_1+2\Delta n_2+\Delta n_3+\Delta n_4}"
    )
    st.latex(r"\text{stoichiometrically consistent data}\quad\Longrightarrow\quad \varepsilon_{\mathrm{stoich}}(t)=0")
    teaching_table(
        ["Needed", "Not needed"],
        [
            ["Measured species inventories", "Rate constants"],
            ["Initial composition", "Reaction orders"],
            ["Assumed stoichiometric network", "Arrhenius parameters"],
            ["Consistent mole basis", "ODE integration"],
        ],
        alignments=["center", "center"],
    )
    st.markdown(
        "A systematic non-zero residual can signal measurement bias/noise, an omitted species, an incorrect stoichiometric network, an unmodelled reaction, or a basis/sampling inconsistency. "
        "It therefore provides a useful **rate-free check before kinetic fitting**."
    )
    _concept_card(
        "Variable-volume caution",
        "For a variable-volume batch, carry out this check using mole amounts. Applying the same invariant directly to concentrations can create an apparent inconsistency simply because the volume changed.",
        "#f59e0b",
    )

    st.markdown("### 4 · Reconcile noisy data to the stoichiometric subspace")
    st.markdown(
        r"If the reaction network is trusted and measured composition changes are noisy, the measurements can be compared with the nearest change that lies in the column space of $\mathbf S$. "
        "For a simple unweighted least-squares reconciliation:"
    )
    st.latex(r"\widehat{\boldsymbol\xi}=\mathbf S^{+}\Delta\mathbf n_{\mathrm{meas}}")
    st.latex(r"\boxed{\Delta\widehat{\mathbf n}=\mathbf S\widehat{\boldsymbol\xi}}")
    st.latex(r"\boxed{\mathbf e=\Delta\mathbf n_{\mathrm{meas}}-\Delta\widehat{\mathbf n}}")
    st.markdown(
        r"The residual $\mathbf e$ shows the adjustment required to make the measurements stoichiometrically consistent. "
        "If measurement uncertainties are known, the same idea can be extended to weighted data reconciliation so that reliable measurements are adjusted less than uncertain ones."
    )
    _concept_card(
        "Do not hide model mismatch",
        "Data reconciliation is appropriate only when there is good reason to trust the stoichiometric structure. Raw inconsistency residuals should be inspected first; conditioning data should not be used to conceal evidence of a missing reaction or an incorrect model.",
        "#fb7185",
    )

    st.markdown("## KineticFittingPot workflow summary")
    st.markdown(
        """
        <div class='model-chain'>
            <div><b>Reaction network</b><span>stoichiometric matrix S</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Rate-free structure</b><span>dependencies & invariants</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Experimental data</b><span>validate / reconstruct / reconcile</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Kinetics</b><span>reaction-rate vector r</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Performance</b><span>conversion, yield & selectivity</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _concept_card(
        "Four questions to keep separate",
        "<b>Conversion:</b> how much reactant has disappeared?<br>"
        "<b>Instantaneous yield/selectivity:</b> what is the chemistry doing now?<br>"
        "<b>Overall yield/selectivity:</b> what has accumulated so far?<br>"
        "<b>Stoichiometric dependency:</b> what relationships must hold even before a kinetic model is specified?",
        ACCENT,
    )

    st.markdown("### Continue through KineticFittingPot")
    left, centre, right = st.columns(3)
    with left:
        if st.button("← Reaction Stoichiometry Fundamentals", key="cys_open_stoich"):
            navigate("Reaction Stoichiometry Fundamentals")
    with centre:
        if st.button("Open Batch Reactor Fundamentals →", key="cys_open_batch"):
            navigate("Batch Reactor Fundamentals")
    with right:
        if st.button("Open Kinetic Fitting Fundamentals →", key="cys_open_fit"):
            navigate("Kinetic Fitting Fundamentals")
