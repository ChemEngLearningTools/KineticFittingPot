from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    # Forward stoichiometric columns for the biodiesel network.
    # Species: TG, DG, MG, MeOH, ME, Gly
    S = np.array([
        [-1.0,  0.0,  0.0],
        [ 1.0, -1.0,  0.0],
        [ 0.0,  1.0, -1.0],
        [-1.0, -1.0, -1.0],
        [ 1.0,  1.0,  1.0],
        [ 0.0,  0.0,  1.0],
    ])

    # Fully observed fatty-acyl invariant: 3 TG + 2 DG + MG + ME.
    l_observed = np.array([3.0, 2.0, 1.0, 0.0, 1.0, 0.0])
    assert np.allclose(l_observed @ S, 0.0)

    # Other valid but partially observed invariants used conceptually.
    l_glycerol_backbone = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 1.0])
    l_methanol_ester = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 0.0])
    assert np.allclose(l_glycerol_backbone @ S, 0.0)
    assert np.allclose(l_methanol_ester @ S, 0.0)

    # Linear weighted reconciliation example: one exact balance H x = h.
    y = np.array([1.10, 1.85, 3.10])
    H = np.array([[1.0, 1.0, 1.0]])
    h = np.array([6.0])
    Sigma = np.diag([0.04, 0.09, 0.16])
    correction = Sigma @ H.T @ np.linalg.solve(H @ Sigma @ H.T, H @ y - h)
    x_star = y - correction.ravel()
    assert np.allclose(H @ x_star, h, atol=1e-12)

    home_text = (ROOT / "modules" / "home.py").read_text(encoding="utf-8")
    app_text = (ROOT / "app.py").read_text(encoding="utf-8")
    module_text = (ROOT / "modules" / "model_diagnostics_fundamentals.py").read_text(encoding="utf-8")
    doc_text = (ROOT / "docs" / "MODEL_DIAGNOSTICS_FUNDAMENTALS.md").read_text(encoding="utf-8")

    assert '"Model Diagnostics Fundamentals"' in home_text
    assert '"Model Diagnostics Fundamentals"' in app_text
    assert "Stoichiometric-consistency monitoring" in module_text
    assert "Profile likelihood" in module_text
    assert "k_r=0" in module_text
    assert "Data reconciliation" in doc_text
    assert "does not prove" in module_text
    assert "Open Post-fit Model Diagnostics" in module_text
    assert "This Fundamentals page defines the diagnostic concepts only" not in module_text

    print("Model Diagnostics Fundamentals smoke test passed.")
    print(f"Observed invariant l^T S = {l_observed @ S}")
    print(f"Reconciled constraint Hx = {(H @ x_star)[0]:.12f}")


if __name__ == "__main__":
    main()
