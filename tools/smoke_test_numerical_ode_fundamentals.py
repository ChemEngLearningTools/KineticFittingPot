from __future__ import annotations

from pathlib import Path
import math
import sys

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    # Euler illustration used on the page.
    h = 0.2
    y0 = 0.9
    f0 = 0.2 * (1.0 - y0)
    y1_euler = y0 + h * f0
    y2_euler = y1_euler + h * 0.2 * (1.0 - y1_euler)
    assert abs(y1_euler - 0.904) < 1e-12
    assert abs(y2_euler - 0.90784) < 1e-12

    def analytical(t: float, y_initial: float, u: float, t_initial: float) -> float:
        return u + (y_initial - u) * math.exp(-0.2 * (t - t_initial))

    # Smooth numerical integration agrees with the closed-form solution.
    sol = solve_ivp(
        lambda t, y: [0.2 * (1.0 - y[0])],
        (0.0, 30.0),
        [y0],
        method="RK45",
        rtol=1e-9,
        atol=1e-12,
        dense_output=True,
    )
    assert sol.success
    y30 = float(sol.sol(30.0)[0])
    assert abs(y30 - analytical(30.0, y0, 1.0, 0.0)) < 1e-8

    # Known discontinuities: explicitly segment at 25 s and 50 s.
    segments = [(0.0, 25.0, 1.0), (25.0, 50.0, 0.9), (50.0, 100.0, 1.0)]
    y_seg = y0
    for t_start, t_end, u in segments:
        seg = solve_ivp(
            lambda t, y, u=u: [0.2 * (u - y[0])],
            (t_start, t_end),
            [y_seg],
            method="RK45",
            rtol=1e-9,
            atol=1e-12,
        )
        assert seg.success
        expected = analytical(t_end, y_seg, u, t_start)
        y_seg = float(seg.y[0, -1])
        assert abs(y_seg - expected) < 1e-8

    # State-triggered event: y=t, event at y=0.75 -> t=0.75.
    def event(t, y):
        return y[0] - 0.75

    event.terminal = True
    event.direction = 1
    ev = solve_ivp(
        lambda t, y: [1.0],
        (0.0, 2.0),
        [0.0],
        events=event,
        rtol=1e-10,
        atol=1e-12,
    )
    assert ev.success
    assert len(ev.t_events[0]) == 1
    assert abs(float(ev.t_events[0][0]) - 0.75) < 1e-9

    source_pdf = ROOT / "data" / "reference" / "ODE_Integration(2C).pdf"
    assert source_pdf.exists() and source_pdf.stat().st_size > 0

    home_text = (ROOT / "modules" / "home.py").read_text(encoding="utf-8")
    app_text = (ROOT / "app.py").read_text(encoding="utf-8")
    module_text = (ROOT / "modules" / "numerical_ode_fundamentals.py").read_text(encoding="utf-8")
    assert '"Numerical Solution of Differential Equations"' in home_text
    assert '"Numerical Solution of Differential Equations"' in app_text
    assert "Known-time discontinuity" in module_text
    assert "event detection" in module_text.lower()
    assert "output-time array" in module_text

    print("Numerical ODE Fundamentals smoke test passed.")
    print(f"Euler y(0.2)={y1_euler:.6f}; y(0.4)={y2_euler:.6f}")
    print(f"RK45 y(30)={y30:.10f}")
    print(f"Segmented final y(100)={y_seg:.10f}")
    print(f"Event time={float(ev.t_events[0][0]):.9f} s")


if __name__ == "__main__":
    main()
