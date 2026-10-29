from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow direct execution from the project root or from the tools directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.batch_model import (
    initial_moles_from_component_volumes,
    reference_parameters,
    simulate_van_de_vusse,
)


def run(volume_model: str, solvent_volume_m3: float = 0.5, reactant_volume_m3: float = 0.5) -> dict:
    ref = reference_parameters()
    n0 = initial_moles_from_component_volumes(
        np.array([solvent_volume_m3, reactant_volume_m3, 0.0, 0.0, 0.0]),
        ref.molecular_weight_kg_per_kmol,
        ref.density_kg_per_m3,
    )
    return simulate_van_de_vusse(
        initial_moles_kmol=n0,
        temperature_c=60.0,
        batch_time_s=7200.0,
        output_points=1200,
        volume_model=volume_model,
        pre_exponential=ref.pre_exponential,
        activation_energy_kj_per_kmol=ref.activation_energy_kj_per_kmol,
        molecular_weight_kg_per_kmol=ref.molecular_weight_kg_per_kmol,
        density_kg_per_m3=ref.density_kg_per_m3,
    )


def main() -> None:
    ref = reference_parameters()
    assert np.array_equal(ref.pre_exponential, np.array([8088.0, 4.7e8, 8.73e5]))
    assert np.array_equal(ref.activation_energy_kj_per_kmol, np.array([50434.0, 74650.0, 60889.0]))

    for mode in ("constant", "composition-dependent"):
        result = run(mode)
        assert result["solver_success"]
        assert result["max_mass_error_fraction"] < 1e-10
        assert result["optimum"]["time_s"] > 0
        assert result["optimum"]["time_s"] < 7200
        assert result["optimum"]["n_kmol"][3] > 0
        # MATLAB reference-data regression checks. These intentionally use
        # modest tolerances so they catch unit/transcription errors without
        # over-constraining harmless solver/platform differences.
        assert 1600.0 < result["optimum"]["time_s"] < 1800.0
        assert 1.75 < result["optimum"]["n_kmol"][3] < 1.90
        print(
            f"PASS {mode}: optimum={result['optimum']['time_s']:.3f} s, "
            f"max x3={result['optimum']['n_kmol'][3]:.6g} kmol, "
            f"final V={result['volume_m3'][-1]:.6g} m3, "
            f"mass error={result['max_mass_error_fraction']:.3e}"
        )

    # v1.44 Stage 1 UI default: preserve the 50:50 reference composition but
    # scale the charge to the 0.70 m3 nominal working volume of a 1.00 m3 vessel.
    default_result = run("constant", 0.35, 0.35)
    assert np.isclose(default_result["initial_volume_m3"], 0.70, atol=1e-12)
    assert 1600.0 < default_result["optimum"]["time_s"] < 1800.0
    assert 1.20 < default_result["optimum"]["n_kmol"][3] < 1.35
    # Proportional scaling leaves the concentration path unchanged while amounts scale by 0.7.
    historical_result = run("constant", 0.5, 0.5)
    np.testing.assert_allclose(
        default_result["c_kmol_m3"],
        historical_result["c_kmol_m3"],
        rtol=1e-6,
        atol=5e-7,
    )
    np.testing.assert_allclose(
        default_result["n_kmol"],
        0.7 * historical_result["n_kmol"],
        rtol=1e-6,
        atol=5e-7,
    )
    print(
        "PASS v1.44 default working-volume charge: "
        f"initial V={default_result['initial_volume_m3']:.3f} m3, "
        f"max x3={default_result['optimum']['n_kmol'][3]:.6g} kmol"
    )

    page_text = (PROJECT_ROOT / "modules" / "batch_simulation.py").read_text(encoding="utf-8")
    for item in [
        '"Reactor vessel volume (m³)"',
        '"Nominal working volume (m³)"',
        'value=0.35',
        'Physical fill basis:',
        'alignments=["left", "left", "center", "center"]',
        'alignments=["left", "left", "center", "center", "center", "center"]',
    ]:
        assert item in page_text, f"Missing v1.44 Stage 1 isothermal-batch UI content: {item}"
    assert page_text.count('value=0.35') >= 2
    print("PASS v1.44 isothermal-batch UI definition and centred numeric teaching tables")

    # Current v1.13 page layout: mathematical detail remains collapsed,
    # and experiments follow results rather than preceding the controls.
    for marker in ('with st.expander("Mathematical model and numerical method"',
                   '## Suggested experiments with this simulation',
                   '## Simulation controls'):
        assert marker in page_text, f"Current batch-simulator page missing {marker}"
    assert page_text.index('def _controls()') < page_text.index('def render()')
    body = page_text.split('def render()', 1)[1]
    assert body.index('controls = _controls()') < body.index('_suggested_experiments()')
    print('PASS current simulator guidance and experiments-after-results layout')


if __name__ == "__main__":
    main()
