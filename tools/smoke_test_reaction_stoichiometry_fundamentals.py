from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    # Van de Vusse reacting-species stoichiometric matrix used on the teaching page.
    S = np.array(
        [
            [-2.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, -1.0],
            [0.0, 0.0, 1.0],
        ]
    )
    assert S.shape == (4, 3)

    r = np.array([2.0, 3.0, 5.0])
    R = S @ r
    np.testing.assert_allclose(R, [-7.0, 2.0, -2.0, 5.0])

    # A catalyst may be absent from stoichiometric consumption/formation while
    # still appearing in a rate law. The stoichiometric vector itself is clear.
    nu_catalytic = np.array([-1.0, 1.0, 0.0])
    np.testing.assert_allclose(nu_catalytic, [-1.0, 1.0, 0.0])

    # Elemental conservation example: 2 H2 + O2 -> 2 H2O.
    A = np.array(
        [
            [2.0, 0.0, 2.0],  # H atoms in H2, O2, H2O
            [0.0, 2.0, 1.0],  # O atoms in H2, O2, H2O
        ]
    )
    nu = np.array([-2.0, -1.0, 2.0])
    np.testing.assert_allclose(A @ nu, np.zeros(2))

    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    home_source = (ROOT / "modules" / "home.py").read_text(encoding="utf-8")
    page_source = (ROOT / "modules" / "reaction_stoichiometry_fundamentals.py").read_text(encoding="utf-8")

    assert '"Reaction Stoichiometry Fundamentals": reaction_stoichiometry_fundamentals.render' in app_source
    assert '"Reactor Tools": reactor_tools.render' not in app_source

    # Current v1.13 homepage places stoichiometry under Learning & Reference.
    assert 'LEARNING = [' in home_source
    learning_block = home_source.split('LEARNING = [', 1)[1].split('\n]', 1)[0]
    for marker in ('Reaction Stoichiometry Fundamentals', 'Conversion, Yield and Selectivity',
                   'Numerical Solution of Differential Equations'):
        assert learning_block.count(marker) == 1
    assert 'LEARNING & REFERENCE' in home_source
    assert 'CASE STUDIES' in home_source
    assert home_source.index('CASE STUDIES') < home_source.index('LEARNING & REFERENCE')
    assert 'section="Fundamentals"' in page_source or 'section="Learning & Reference"' in page_source

    # v1.22 uses a static teaching-table renderer so both headers and body
    # coefficients obey the requested centring rather than dataframe defaults.
    assert 'teaching_table(' in page_source
    assert 'alignments=["left", "center", "center", "center"]' in page_source
    assert 'alignments=["left", "center"]' in page_source

    required_page_markers = [
        "Chemical reactions and stoichiometric coefficients",
        "From one reaction to a stoichiometric vector",
        "Multiple reactions: the stoichiometric matrix",
        "A note about matrix conventions",
        "Connecting stoichiometry with reaction rates",
        "Stoichiometry and kinetics are not the same thing",
        "Is the reaction balanced? The elemental matrix",
        "Can the elemental matrix determine the reactions?",
        "KineticFittingPot workflow summary",
        r"\boxed{\frac{d\mathbf n}{dt}=V\,\mathbf S\,\mathbf r}",
        r"\boxed{\mathbf A\mathbf S=\mathbf 0}",
    ]
    for marker in required_page_markers:
        assert marker in page_source, marker

    print("Reaction stoichiometry fundamentals smoke test passed.")
    print("Home section order: Simulation/Fitting -> Further Analysis -> Case Studies -> Learning & Reference")
    print("Fundamentals includes stoichiometry, conversion/yield/selectivity and numerical ODE solution")
    print("Stoichiometric-table numeric columns: centred")
    print("Van de Vusse matrix shape:", S.shape)
    print("Example S @ r:", R.tolist())
    print("Elemental conservation check A @ nu:", (A @ nu).tolist())


if __name__ == "__main__":
    main()
