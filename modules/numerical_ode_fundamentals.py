from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.ui import chips, teaching_table, workspace_header


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PDF = ROOT / "data" / "reference" / "ODE_Integration(2C).pdf"
ACCENT = "#a78bfa"


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
        "Numerical Solution of Differential Equations",
        "Understand why reactor models are solved numerically, what an adaptive ODE integrator is doing, and why known discontinuities and state-triggered events need special treatment.",
        section="Fundamentals",
        accent=ACCENT,
    )

    chips([
        ("Learning", "blue"),
        ("Initial-value problems", ""),
        ("Euler illustration", "blue"),
        ("Adaptive RK45", "warn"),
        ("Discontinuities", "warn"),
        ("Event detection", ""),
    ])

    st.markdown(
        """
        <div class='learning-objectives'>
            <div class='learning-objectives-title'>Learning path</div>
            <div class='learning-objectives-grid'>
                <div><b>1 · Recognise</b><br><span>when analytical and numerical solutions are appropriate.</span></div>
                <div><b>2 · Interpret</b><br><span>numerical integration as advancing a state from its initial condition.</span></div>
                <div><b>3 · Understand</b><br><span>adaptive internal steps and numerical tolerances.</span></div>
                <div><b>4 · Segment</b><br><span>integration at known discontinuities.</span></div>
                <div><b>5 · Detect</b><br><span>state-triggered events whose occurrence time is not known beforehand.</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Analytical or numerical?")
    st.markdown(
        "A differential equation can sometimes be solved analytically, giving a closed-form expression that satisfies both the differential equation and its initial condition. "
        "Simple linear models are important examples, and selected nonlinear problems also have analytical solutions."
    )
    st.markdown(
        "Chemical-engineering models, however, quickly become **coupled and nonlinear**. A reactor model may contain species inventories, temperature, jacket temperature, volume and controller states, all changing together. "
        "Numerical integration gives a general framework for solving these models without deriving a new analytical expression for every case."
    )
    _equation_caption("General initial-value problem")
    st.latex(r"\boxed{\frac{d\mathbf y}{dt}=\mathbf f(t,\mathbf y,\mathbf u),\qquad \mathbf y(t_0)=\mathbf y_0}")
    st.markdown(
        r"The state vector $\mathbf y$ contains the quantities that evolve with time. The inputs $\mathbf u$ may be constant or time-varying. "
        "For a reactor, the right-hand side is the mathematical model that returns the current derivatives."
    )
    _concept_card(
        "KineticFittingPot already works this way",
        "The batch, non-isothermal and jacket/control simulators all assemble a vector of state derivatives and pass it to a numerical ODE solver. The chemistry changes the derivative calculation; the numerical integration framework remains the same.",
        "#2dd4bf",
    )

    st.markdown("## What numerical integration is doing")
    st.markdown("For a single state,")
    st.latex(r"\frac{dy}{dt}=f(t,y,u),\qquad y(t_0)=y_0")
    st.markdown("the exact relationship can be written as")
    st.latex(r"y(t)=y_0+\int_{t_0}^{t}f(\tau,y(\tau),u(\tau))\,d\tau")
    st.markdown(
        "A numerical method approximates this evolution through a sequence of calculations. The simplest way to see the idea is Euler's method."
    )

    st.markdown("## A simple example")
    st.markdown("Consider the first-order model used in the accompanying notes:")
    st.latex(r"\frac{dy}{dt}=0.2(u-y)")
    st.markdown(r"For $t\geq0$, let $u=1$ and $y(0)=0.9$. The analytical solution is")
    st.latex(r"\boxed{y(t)=0.9+0.1\left(1-e^{-0.2t}\right)}")
    st.markdown("Euler's method uses a fixed step $h$ and the current derivative:")
    st.latex(r"\boxed{y_{k+1}=y_k+h\,f(t_k,y_k)}")
    st.markdown(r"With $h=0.2\ \mathrm{s}$, the first step is")
    st.latex(r"y(0.2)\approx0.9+0.2\,[0.2(1-0.9)]=0.904")
    st.markdown("Repeating the same calculation gives the next estimate. Comparing a few values makes the numerical approximation visible:")
    teaching_table(
        ["Time (s)", "Euler", "Analytical"],
        [
            ["0.0", "0.9000", "0.9000"],
            ["0.2", "0.9040", "0.9039"],
            ["0.4", "0.9078", "0.9077"],
        ],
        alignments=["center", "center", "center"],
        monospace_columns={0, 1, 2},
    )
    _concept_card(
        "Why show Euler if KineticFittingPot does not use it?",
        "Euler's method makes the numerical idea transparent: start from the initial condition, evaluate the derivative, move forward and repeat. KineticFittingPot uses a much more accurate adaptive Runge–Kutta solver, but the underlying initial-value viewpoint is the same.",
        "#38bdf8",
    )

    st.markdown("## Modern adaptive integration")
    st.markdown(
        "KineticFittingPot's current reactor models use SciPy's `solve_ivp` with the **RK45** method. Rather than committing to one fixed step size, the solver estimates its local numerical error and adapts its internal step size."
    )
    teaching_table(
        ["Idea", "Meaning"],
        [
            ["Small internal steps", "Used where the solution needs finer resolution to satisfy the error target."],
            ["Larger internal steps", "Used where the solution is smooth and the same accuracy can be achieved more efficiently."],
            ["Relative tolerance", "Controls error relative to the magnitude of the state."],
            ["Absolute tolerance", "Provides an absolute error scale, especially important when a state is near zero."],
        ],
        alignments=["left", "left"],
    )
    st.markdown("KineticFittingPot's established reactor simulations typically use")
    st.latex(r"\mathrm{rtol}=10^{-6},\qquad \mathrm{atol}=10^{-9}")
    st.markdown(
        "RK45 is a good general-purpose non-stiff solver. Some chemical-engineering models can become **stiff**, in which case other numerical methods may be more efficient or robust. "
        "The important point here is that solver choice and tolerances are part of the numerical model and should not be hidden."
    )

    st.markdown("## Internal solver steps are not the same as plotted points")
    st.markdown(
        "A simulator may display results on a regular grid — for example every 10 seconds — while the adaptive integrator has taken many different internal steps between those output times."
    )
    _concept_card(
        "Output time ≠ integration step",
        "Requesting a value at a particular time tells the solver where a reported solution is wanted. It does not necessarily force that time to become a boundary between two internal integration steps.",
        "#f59e0b",
    )
    st.markdown(
        "This distinction becomes particularly important when a model contains a **discontinuity**."
    )

    st.markdown("## Discontinuities need special treatment")
    st.markdown(
        "Suppose the same first-order system experiences known changes in its input:"
    )
    st.latex(
        r"u(t)=\begin{cases}"
        r"1.0,&0\leq t<25\\"
        r"0.9,&25\leq t<50\\"
        r"1.0,&t\geq50"
        r"\end{cases}"
    )
    st.markdown(
        r"The state $y$ remains continuous at 25 s and 50 s, but its derivative changes abruptly because the input has changed. "
        "The numerical solver should therefore treat these times deliberately rather than unknowingly stepping across them."
    )

    st.markdown("### Known-time discontinuity: stop, change, restart")
    _concept_card(
        "Preferred strategy when the switching time is known",
        "Integrate exactly to the known discontinuity, stop the solver, change the input or model condition, and restart from the final state of the previous segment.",
        "#2dd4bf",
    )
    st.markdown(
        "For the example above, solve three continuous segments:"
    )
    st.latex(r"[0,25]\qquad\rightarrow\qquad[25,50]\qquad\rightarrow\qquad[50,t_f]")
    st.markdown(
        "The terminal state of one segment becomes the initial condition of the next. The physical state remains continuous; the equation defining its derivative changes at the segment boundary."
    )
    _concept_card(
        "A common numerical mistake",
        "Putting 25 s into an output-time array is <b>not the same thing</b> as stopping the integration at 25 s. If a discontinuity time is known, make it an integration boundary rather than relying on an adaptive solver to discover a change that you already know exists.",
        "#fb7185",
    )

    st.markdown("### Unknown switching time: event detection")
    st.markdown(
        "Sometimes the condition is known but the time at which it occurs is not. For example: **stop the feed when the reactor temperature reaches 90 °C**."
    )
    st.markdown("Define an event function")
    st.latex(r"g(t,\mathbf y)=T-90")
    st.markdown("The event occurs when")
    st.latex(r"\boxed{g(t,\mathbf y)=0}")
    st.markdown(
        "An event-capable solver brackets the crossing and refines its location. The simulation can then stop at the event, change operating logic if required, and restart from the detected event state."
    )
    teaching_table(
        ["Situation", "Numerical treatment"],
        [
            ["Known time: feed starts at 600 s", "Integrate to 600 s, change the input, restart."],
            ["Known time: set-point changes at 1200 s", "Use 1200 s as an explicit segment boundary."],
            ["Unknown time: T reaches 90 °C", "Define an event function and locate its zero crossing."],
            ["Smooth input/profile", "No restart is required solely because the input is time-varying."],
        ],
        alignments=["left", "left"],
    )

    st.markdown("## Why this matters for fed-batch reactors")
    st.markdown(
        "Fed-batch operation naturally introduces time-dependent inputs and recipes. A simple material/volume model might contain"
    )
    st.latex(r"\frac{dn_A}{dt}=F_{\mathrm{in}}C_{A,\mathrm{in}}+V(\mathbf S\mathbf r)_A")
    st.latex(r"\frac{dV}{dt}=F_{\mathrm{in}}")
    st.markdown("with a feed schedule such as")
    st.latex(
        r"F_{\mathrm{in}}(t)=\begin{cases}"
        r"0,&t<600\\"
        r"F_0,&600\leq t<2400\\"
        r"0,&t\geq2400"
        r"\end{cases}"
    )
    st.markdown(
        "The appropriate simulation uses three continuous integrations separated at 600 s and 2400 s. The same event-handling framework applies to feed-rate changes, additions and other discontinuous operating schedules."
    )

    st.markdown("## KineticFittingPot numerical workflow")
    st.markdown(
        """
        <div class='model-chain'>
            <div><b>Model equations</b><span>define the state derivatives</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Initial state</b><span>specifies where integration begins</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Adaptive solver</b><span>controls internal steps and error</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Events / boundaries</b><span>handle discontinuous changes explicitly</span></div>
            <div class='model-arrow'>→</div>
            <div><b>Reported solution</b><span>states at useful output times</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _concept_card(
        "Key idea",
        "Numerical integration provides the general dynamic-simulation framework. Adaptive solvers handle smooth evolution efficiently; discontinuities must be represented explicitly through known integration boundaries or event detection.",
        ACCENT,
    )

    st.divider()
    st.markdown("### Source notes")
    st.caption(
        "This page is a concise KineticFittingPot adaptation of the supplied ODE-integration teaching notes. The original Simulink-focused document is retained for provenance, while the screen presentation emphasises the numerical ideas used by KineticFittingPot and the discontinuity handling needed for models with operating changes."
    )
    if SOURCE_PDF.exists():
        st.download_button(
            "Download original ODE integration notes (PDF)",
            data=SOURCE_PDF.read_bytes(),
            file_name=SOURCE_PDF.name,
            mime="application/pdf",
            key="download_ode_notes",
        )
