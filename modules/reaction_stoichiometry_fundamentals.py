from __future__ import annotations

import streamlit as st

from utils.ui import chips, navigate, teaching_table, workspace_header


ACCENT = "#2dd4bf"


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
        "Reaction Stoichiometry Fundamentals",
        "From chemical equations to stoichiometric vectors, reaction networks and the matrix form used throughout KineticFittingPot.",
        section="Fundamentals",
        accent=ACCENT,
    )

    chips([
        ("Learning", "blue"),
        ("Stoichiometric coefficients", ""),
        ("Reaction networks", "blue"),
        ("Linear algebra", "warn"),
        ("Element conservation", ""),
        ("Model foundation", "warn"),
    ])

    st.markdown(
        """
        <div class='learning-objectives'>
            <div class='learning-objectives-title'>Learning path</div>
            <div class='learning-objectives-grid'>
                <div><b>1 · Interpret</b><br><span>signed stoichiometric coefficients.</span></div>
                <div><b>2 · Vectorise</b><br><span>one reaction using a fixed species order.</span></div>
                <div><b>3 · Assemble</b><br><span>several reactions into a matrix.</span></div>
                <div><b>4 · Connect</b><br><span>stoichiometry with reaction-rate kinetics.</span></div>
                <div><b>5 · Validate</b><br><span>element conservation using matrix algebra.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Chemical reactions and stoichiometric coefficients")
    st.markdown("Consider a general chemical reaction:")
    _equation_caption("General reaction")
    st.latex(r"aA+bB\rightarrow cC+dD")
    st.markdown(
        "The stoichiometric coefficients specify the relative amounts of each species consumed or formed by the reaction. "
        "KineticFittingPot uses a signed convention so that the chemical equation can be represented directly by numbers."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        _concept_card("Reactants", "<b>Negative</b> stoichiometric coefficient.", "#fb7185")
    with c2:
        _concept_card("Products", "<b>Positive</b> stoichiometric coefficient.", "#22c55e")
    with c3:
        _concept_card("No stoichiometric participation", "Coefficient is <b>zero</b> for that reaction.", "#38bdf8")

    st.markdown("The same reaction can therefore be written as:")
    st.latex(r"-aA-bB+cC+dD=0")
    st.markdown(
        "Writing the reaction in this form turns the chemical equation into a **linear algebraic relationship**."
    )
    _concept_card(
        "Important — keep one reaction basis",
        "The numerical value of a stoichiometric coefficient depends on the chosen reaction basis. Once a reaction equation has been selected, "
        "reaction rates, heats of reaction and other reaction-based quantities must use that same basis consistently.",
        "#f59e0b",
    )

    st.markdown("## From one reaction to a stoichiometric vector")
    st.markdown("Start with the simple reaction:")
    st.latex(r"A+B\rightarrow C")
    st.markdown("For the fixed species ordering")
    st.latex(r"[A,\;B,\;C]")
    st.markdown("KineticFittingPot can represent the reaction using the stoichiometric vector")
    st.latex(r"\boldsymbol{\nu}=\begin{bmatrix}-1\\-1\\+1\end{bmatrix}")
    _concept_card(
        "Species ordering matters",
        "The order of the species must be defined once and then retained consistently. The vector simply records how much of each species is formed or consumed when the reaction proceeds.",
        "#38bdf8",
    )

    st.markdown("## Multiple reactions: the stoichiometric matrix")
    st.markdown(
        "For a reaction network, place one stoichiometric vector beside another. The result is the **stoichiometric matrix**. "
        "KineticFittingPot uses the Van de Vusse network because the same example appears throughout the batch-reactor teaching and simulation workspaces."
    )
    reaction_cols = st.columns(3)
    reactions = [
        ("Reaction 1", r"2x_1\rightarrow x_2"),
        ("Reaction 2", r"x_1\rightarrow x_3"),
        ("Reaction 3", r"x_3\rightarrow x_4"),
    ]
    for col, (label, equation) in zip(reaction_cols, reactions):
        with col:
            st.markdown(f"**{label}**")
            st.latex(equation)

    st.markdown(
        "There are $N_S=4$ reacting species and $N_R=3$ reactions. KineticFittingPot defines"
    )
    st.latex(r"\mathbf S\in\mathbb R^{N_S\times N_R}")
    _concept_card(
        "KineticFittingPot convention",
        "<b>Rows = chemical species.</b><br><b>Columns = chemical reactions.</b>",
        ACCENT,
    )
    st.latex(
        r"\mathbf S="
        r"\begin{bmatrix}"
        r"-2&-1&0\\"
        r"+1&0&0\\"
        r"0&+1&-1\\"
        r"0&0&+1"
        r"\end{bmatrix}"
    )

    teaching_table(
        ["Species", "R1", "R2", "R3"],
        [
            ["x1", -2, -1, 0],
            ["x2", 1, 0, 0],
            ["x3", 0, 1, -1],
            ["x4", 0, 0, 1],
        ],
        alignments=["left", "center", "center", "center"],
        monospace_columns={1, 2, 3},
    )
    st.markdown(
        "Each **column** describes one reaction. Each **row** shows how one species participates across the complete reaction network. "
        "For example, $x_3$ is produced by reaction 2 and consumed by reaction 3, so its row contains both a positive and a negative coefficient."
    )
    st.caption(
        "The built-in Van de Vusse simulator also tracks solvent x0. It has stoichiometric row [0, 0, 0], so the 4 × 3 matrix above is the reacting-species block of the full simulator matrix."
    )

    st.markdown("## A note about matrix conventions")
    _concept_card(
        "Matrix orientation is a convention",
        "Some books and notes arrange the stoichiometric matrix with <b>reactions as rows and species as columns</b>. "
        "KineticFittingPot uses the transpose convention: <b>species as rows, reactions as columns</b>. Both contain exactly the same stoichiometric information. "
        "KineticFittingPot's convention is used because it leads directly to a convenient reactor-balance equation.",
        "#a78bfa",
    )

    st.markdown("## Connecting stoichiometry with reaction rates")
    st.markdown("The kinetic model supplies one rate for each reaction. For the Van de Vusse network:")
    st.latex(r"\mathbf r=\begin{bmatrix}r_1\\r_2\\r_3\end{bmatrix}")
    st.markdown("Multiplying the stoichiometric matrix by the reaction-rate vector gives the net formation-rate vector:")
    _equation_caption("Species formation rates per unit volume")
    st.latex(r"\boxed{\mathbf R=\mathbf S\mathbf r}")
    st.latex(r"\mathbf R=\begin{bmatrix}R_1\\R_2\\R_3\\R_4\end{bmatrix}")
    st.markdown("For this network the individual species rates are")
    st.latex(
        r"R_1=-2r_1-r_2\qquad "
        r"R_2=r_1\qquad "
        r"R_3=r_2-r_3\qquad "
        r"R_4=r_3"
    )
    _concept_card(
        "Why the matrix formulation is useful",
        "The kinetic model determines the individual reaction rates <i>r<sub>i</sub></i>. The stoichiometric matrix then automatically converts those reaction rates into the net formation or consumption rate of every chemical species.",
        "#38bdf8",
    )
    st.markdown("For a well-mixed batch reactor, the species balances therefore become")
    _equation_caption("KineticFittingPot batch-reactor form")
    st.latex(r"\boxed{\frac{d\mathbf n}{dt}=V\,\mathbf S\,\mathbf r}")
    st.markdown(
        "This is the equation used by KineticFittingPot's batch-reactor simulators and by the Excel-defined general model. "
        r"Kinetic fitting then reuses the same forward-model structure while estimating selected parameters inside $\mathbf r$."
    )

    st.markdown("## Stoichiometry and kinetics are not the same thing")
    st.markdown(
        "The stoichiometric matrix describes **what is consumed and formed**. The kinetic rate expression describes **how rapidly the reaction proceeds**. "
        "These are related, but they are not the same thing."
    )
    st.markdown("KineticFittingPot's catalytic saturation example provides a useful illustration:")
    st.latex(r"A\xrightarrow{\mathrm{Cat}}B")
    st.latex(r"r_1=\frac{k_1c_{\mathrm{Cat}}c_A}{1+K_Ac_A}")
    teaching_table(
        ["Species", "R1 stoichiometric coefficient"],
        [["A", -1], ["B", 1], ["Cat", 0]],
        alignments=["left", "center"],
        monospace_columns={1},
    )
    st.markdown(
        "The catalyst has a zero stoichiometric coefficient because it is not consumed by the overall reaction. "
        "However, its concentration appears in the kinetic expression and therefore influences the reaction rate."
    )
    _concept_card(
        "Key distinction",
        "<b>A zero stoichiometric coefficient does not necessarily mean that a species is kinetically irrelevant.</b>",
        "#f59e0b",
    )

    st.markdown("## Is the reaction balanced? The elemental matrix")
    st.markdown(
        "Stoichiometric coefficients cannot be arbitrary. A valid chemical reaction must conserve every chemical element, and this requirement can also be written as a matrix relationship."
    )
    st.markdown("Define the elemental matrix")
    st.latex(r"\mathbf A\in\mathbb R^{N_E\times N_S}")
    st.markdown(
        "where **rows are elements**, **columns are species**, and $a_{ij}$ is the number of atoms of element $i$ contained in species $j$. "
        r"Because KineticFittingPot uses species × reactions for $\mathbf S$, a balanced reaction network satisfies"
    )
    _equation_caption("Element-conservation check")
    st.latex(r"\boxed{\mathbf A\mathbf S=\mathbf 0}")
    _concept_card(
        "A compact model check",
        "If every column of <b>S</b> represents a balanced chemical reaction, multiplication by the elemental matrix must give zero. "
        "The matrix formulation therefore provides a direct mathematical check that every element is conserved in every reaction.",
        "#22c55e",
    )

    st.markdown("## Can the elemental matrix determine the reactions?")
    st.markdown(
        "For a simple system containing one independent reaction, elemental conservation can sometimes be used to determine a valid set of stoichiometric coefficients by finding the **null space** of the elemental matrix:"
    )
    st.latex(r"\mathbf A\boldsymbol\nu=\mathbf 0")
    st.markdown(
        "For systems containing several independent reactions, however, elemental conservation alone generally does **not** tell us which physical reactions are actually occurring. "
        "The elemental matrix tells us which stoichiometries are compatible with conservation of atoms. The chemistry and reaction mechanism are still needed to define the reaction network used for kinetic modelling."
    )
    with st.expander("Advanced: deriving stoichiometry from elemental composition"):
        st.markdown(
            r"The null space $\mathcal N(\mathbf A)$ contains every stoichiometric vector $\boldsymbol\nu$ that satisfies elemental conservation. "
            "A non-zero null vector can therefore provide a balanced stoichiometric relationship."
        )
        st.latex(r"\boldsymbol\nu\in\mathcal N(\mathbf A)\qquad\Longleftrightarrow\qquad\mathbf A\boldsymbol\nu=\mathbf 0")
        st.markdown(
            r"The scale of a null vector is not unique: if $\boldsymbol\nu$ is valid, then $\alpha\boldsymbol\nu$ is also valid for any non-zero scalar $\alpha$. "
            "That is the linear-algebra version of choosing a reaction basis. For a multi-reaction system, the null space can contain several independent directions, but conservation alone does not identify which basis corresponds to the physical reaction mechanism."
        )

    st.markdown("## KineticFittingPot workflow summary")
    st.markdown(
        """
        <div class='model-chain'>
            <div><b>Reaction equations</b><span>define the chemistry</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Stoichiometric matrix S</b><span>encode consumption & formation</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Reaction-rate vector r</b><span>evaluate the kinetics</span></div>
            <div class='model-arrow'>→</div>
            <div><b>S r</b><span>net species formation rates</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Species balances</b><span>build the reactor model</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "The same stoichiometric structure connects the batch-reactor examples, user-defined reaction networks and kinetic parameter estimation. It is also applicable to other reactor configurations."
    )
    _concept_card(
        "Key idea",
        "<b>Stoichiometry determines how reaction rates change species inventories. Kinetics determines how fast the individual reactions proceed.</b>",
        ACCENT,
    )

    st.markdown("### Continue through KineticFittingPot")
    left, centre, right = st.columns(3)
    with left:
        if st.button("Conversion, Yield and Selectivity →", key="stoich_open_cys"):
            navigate("Conversion, Yield and Selectivity")
    with centre:
        if st.button("Open Batch Reactor Fundamentals →", key="stoich_open_batch_fundamentals"):
            navigate("Batch Reactor Fundamentals")
    with right:
        if st.button("Open Simulate Your Own Model →", key="stoich_open_custom_model"):
            navigate("Simulate Your Own Model — Isothermal Batch Reactor")
