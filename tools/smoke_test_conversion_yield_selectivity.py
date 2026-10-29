from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    # Parallel network: nu1 A -> D, nu2 A -> U.
    nu1, nu2 = 2.0, 1.0
    r1, r2 = 3.0, 5.0
    RA = -(nu1 * r1 + nu2 * r2)
    RD, RU = r1, r2
    y_d = RD / (-RA)
    y_u = RU / (-RA)
    np.testing.assert_allclose(nu1 * y_d + nu2 * y_u, 1.0)
    np.testing.assert_allclose(RD / RU, r1 / r2)

    # Series network: A -> D -> U. Net desired-product yield may become negative.
    r1_series, r2_series = 2.0, 3.0
    y_d_series = (r1_series - r2_series) / r1_series
    y_u_series = r2_series / r1_series
    assert y_d_series < 0.0
    np.testing.assert_allclose(y_d_series + y_u_series, 1.0)

    # Van de Vusse reacting-species stoichiometric matrix.
    S = np.array(
        [
            [-2.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, -1.0],
            [0.0, 0.0, 1.0],
        ]
    )
    assert np.linalg.matrix_rank(S) == 3

    # Key species x2, x3, x4; dependent species x1.
    S_K = S[[1, 2, 3], :]
    S_dep = S[[0], :]
    S_K_inv = np.linalg.inv(S_K)
    Phi = S_dep @ S_K_inv
    np.testing.assert_allclose(
        S_K_inv,
        [[1.0, 0.0, 0.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]],
    )
    np.testing.assert_allclose(Phi, [[-2.0, -1.0, -1.0]])

    # Any extent-generated composition change must satisfy the dependency.
    dxi = np.array([0.3, 0.7, 0.2])
    dn = S @ dxi
    np.testing.assert_allclose(dn[0], -2.0 * dn[1] - dn[2] - dn[3])
    invariant = np.array([1.0, 2.0, 1.0, 1.0])
    np.testing.assert_allclose(invariant @ dn, 0.0, atol=1e-12)

    # Unweighted stoichiometric reconciliation projects noisy data into col(S).
    noisy_dn = dn + np.array([0.02, -0.01, 0.015, -0.008])
    xi_hat = np.linalg.pinv(S) @ noisy_dn
    reconciled = S @ xi_hat
    residual = noisy_dn - reconciled
    np.testing.assert_allclose(S.T @ residual, np.zeros(3), atol=1e-12)
    np.testing.assert_allclose(invariant @ reconciled, 0.0, atol=1e-12)

    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    home_source = (ROOT / "modules" / "home.py").read_text(encoding="utf-8")
    page_source = (ROOT / "modules" / "conversion_yield_selectivity.py").read_text(encoding="utf-8")

    assert '"Conversion, Yield and Selectivity": conversion_yield_selectivity.render' in app_source
    fundamentals_block = home_source.split('"Fundamentals": [', 1)[1].split('],', 1)[0]
    assert fundamentals_block.count('Reaction Stoichiometry Fundamentals') == 1
    assert fundamentals_block.count('Conversion, Yield and Selectivity') == 1

    required_markers = [
        "Conversion: how much reactant has disappeared?",
        "Instantaneous yield and selectivity",
        "Overall yield and selectivity",
        "Parallel reactions: desired versus undesired pathways",
        "Series reactions: when the desired product starts disappearing",
        "Stoichiometric dependencies: what can be learned without kinetics?",
        "Van de Vusse worked dependency",
        "Reconstruct an unmeasured species",
        "Reduce the ODE set",
        "Validate measured data against stoichiometry — without rates",
        "Reconcile noisy data to the stoichiometric subspace",
        r"\boxed{X_A(t)=\frac{n_{A0}-n_A(t)}{n_{A0}}}",
        r"\boxed{d\mathbf n=\mathbf S\,d\boldsymbol\xi}",
        r"\begin{bmatrix}-2&-1&-1\end{bmatrix}",
        r"\varepsilon_{\mathrm{stoich}}(t)",
        r"\widehat{\boldsymbol\xi}=\mathbf S^{+}\Delta\mathbf n_{\mathrm{meas}}",
    ]
    for marker in required_markers:
        assert marker in page_source, marker

    print("Conversion, yield and selectivity smoke test passed.")
    print("Parallel weighted-yield closure:", nu1 * y_d + nu2 * y_u)
    print("Series desired instantaneous yield:", y_d_series)
    print("Van de Vusse rank:", np.linalg.matrix_rank(S))
    print("Van de Vusse Phi:", Phi.tolist())
    print("Rate-free invariant residual:", float(invariant @ dn))
    print("Reconciled invariant residual:", float(invariant @ reconciled))


if __name__ == "__main__":
    main()
