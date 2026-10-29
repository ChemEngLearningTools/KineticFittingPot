from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
try:
    from scipy.integrate import solve_ivp
except ImportError:  # allows the app shell to start before dependencies are installed
    solve_ivp = None


R_KJ_PER_KMOL_K = 8.314
SPECIES = ("x0", "x1", "x2", "x3", "x4")
SPECIES_NAMES = ("solvent", "reactant", "by-product", "desired product", "waste product")

# Rows: x0 ... x4. Columns: reactions 1 ... 3.
STOICHIOMETRIC_MATRIX = np.array(
    [
        [0.0, 0.0, 0.0],
        [-2.0, -1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, -1.0],
        [0.0, 0.0, 1.0],
    ],
    dtype=float,
)


@dataclass(frozen=True)
class BatchReferenceParameters:
    """Reference Van de Vusse parameters checked against the supplied MATLAB parameter source."""

    pre_exponential: np.ndarray
    activation_energy_kj_per_kmol: np.ndarray
    molecular_weight_kg_per_kmol: np.ndarray
    density_kg_per_m3: np.ndarray


def reference_parameters() -> BatchReferenceParameters:
    return BatchReferenceParameters(
        pre_exponential=np.array([8088.0, 4.7e8, 8.73e5], dtype=float),
        activation_energy_kj_per_kmol=np.array([50434.0, 74650.0, 60889.0], dtype=float),
        molecular_weight_kg_per_kmol=np.array([18.0, 100.0, 200.0, 100.0, 100.0], dtype=float),
        density_kg_per_m3=np.array([1000.0, 800.0, 900.0, 1000.0, 1000.0], dtype=float),
    )


def arrhenius_rate_constants_kelvin(
    temperature_k: float,
    pre_exponential: np.ndarray,
    activation_energy_kj_per_kmol: np.ndarray,
) -> np.ndarray:
    temperature_k = float(temperature_k)
    if temperature_k <= 0:
        raise ValueError("Temperature must be above absolute zero.")
    return np.asarray(pre_exponential, dtype=float) * np.exp(
        -np.asarray(activation_energy_kj_per_kmol, dtype=float) / (R_KJ_PER_KMOL_K * temperature_k)
    )


def arrhenius_rate_constants(
    temperature_c: float,
    pre_exponential: np.ndarray,
    activation_energy_kj_per_kmol: np.ndarray,
) -> np.ndarray:
    return arrhenius_rate_constants_kelvin(
        float(temperature_c) + 273.15,
        pre_exponential,
        activation_energy_kj_per_kmol,
    )


def initial_moles_from_component_volumes(
    component_volumes_m3: np.ndarray,
    molecular_weight_kg_per_kmol: np.ndarray,
    density_kg_per_m3: np.ndarray,
) -> np.ndarray:
    volumes = np.asarray(component_volumes_m3, dtype=float)
    if np.any(volumes < 0):
        raise ValueError("Initial component volumes cannot be negative.")
    return volumes * np.asarray(density_kg_per_m3, dtype=float) / np.asarray(
        molecular_weight_kg_per_kmol, dtype=float
    )


def additive_liquid_volume(
    n_kmol: np.ndarray,
    molecular_weight_kg_per_kmol: np.ndarray,
    density_kg_per_m3: np.ndarray,
) -> float:
    n = np.maximum(np.asarray(n_kmol, dtype=float), 0.0)
    volume = float(np.sum(n * molecular_weight_kg_per_kmol / density_kg_per_m3))
    if not np.isfinite(volume) or volume <= 0:
        raise ValueError("Calculated liquid volume is not positive and finite.")
    return volume


def reaction_rates(c_kmol_per_m3: np.ndarray, k: np.ndarray) -> np.ndarray:
    c = np.maximum(np.asarray(c_kmol_per_m3, dtype=float), 0.0)
    k = np.asarray(k, dtype=float)
    return np.array(
        [
            k[0] * c[1] ** 2,
            k[1] * c[1],
            k[2] * c[3],
        ],
        dtype=float,
    )


def simulate_van_de_vusse(
    *,
    initial_moles_kmol: np.ndarray,
    temperature_c: float,
    batch_time_s: float,
    output_points: int,
    volume_model: Literal["constant", "composition-dependent"],
    pre_exponential: np.ndarray,
    activation_energy_kj_per_kmol: np.ndarray,
    molecular_weight_kg_per_kmol: np.ndarray,
    density_kg_per_m3: np.ndarray,
    method: str = "RK45",
    rtol: float = 1e-6,
    atol: float = 1e-9,
) -> dict:
    if solve_ivp is None:
        raise RuntimeError("SciPy is required for Isothermal Batch Reactor Simulation. Run update_KineticFittingPot_dependencies.bat (or setup_KineticFittingPot.bat for a new installation).")

    n0 = np.asarray(initial_moles_kmol, dtype=float)
    if n0.shape != (5,):
        raise ValueError("The Van de Vusse state must contain five species amounts.")
    if np.any(n0 < 0):
        raise ValueError("Initial species amounts cannot be negative.")
    if n0[1] <= 0:
        raise ValueError("The initial reactant amount x1 must be greater than zero.")
    if batch_time_s <= 0:
        raise ValueError("Batch time must be greater than zero.")
    output_points = int(output_points)
    if output_points < 100:
        raise ValueError("Use at least 100 output points for a useful trajectory.")

    k = arrhenius_rate_constants(temperature_c, pre_exponential, activation_energy_kj_per_kmol)
    initial_volume = additive_liquid_volume(n0, molecular_weight_kg_per_kmol, density_kg_per_m3)

    def volume_from_state(n: np.ndarray) -> float:
        if volume_model == "constant":
            return initial_volume
        if volume_model == "composition-dependent":
            return additive_liquid_volume(n, molecular_weight_kg_per_kmol, density_kg_per_m3)
        raise ValueError(f"Unknown volume model: {volume_model}")

    def rhs(_t: float, n: np.ndarray) -> np.ndarray:
        n_for_rates = np.maximum(n, 0.0)
        volume = volume_from_state(n_for_rates)
        concentrations = n_for_rates / volume
        rates = reaction_rates(concentrations, k)
        return volume * (STOICHIOMETRIC_MATRIX @ rates)

    t_eval = np.linspace(0.0, float(batch_time_s), output_points)
    solution = solve_ivp(
        rhs,
        t_span=(0.0, float(batch_time_s)),
        y0=n0,
        method=method,
        t_eval=t_eval,
        rtol=float(rtol),
        atol=float(atol),
        dense_output=True,
    )

    if not solution.success:
        raise RuntimeError(f"ODE solver failed: {solution.message}")

    # Small negative values can arise from numerical tolerances near depletion.
    n = np.maximum(solution.y.T, 0.0)
    times = solution.t

    volumes = np.array([volume_from_state(row) for row in n], dtype=float)
    concentrations = n / volumes[:, None]
    rates = np.array([reaction_rates(row, k) for row in concentrations], dtype=float)

    # Use a denser evaluation of the continuous solution to locate the x3 maximum
    # without exposing solver-internal steps to the user.
    dense_count = max(5000, output_points * 3)
    t_dense = np.linspace(0.0, float(batch_time_s), dense_count)
    n_dense = np.maximum(solution.sol(t_dense).T, 0.0)
    optimum_idx = int(np.argmax(n_dense[:, 3]))
    optimum_time_s = float(t_dense[optimum_idx])
    optimum_n = n_dense[optimum_idx]
    optimum_volume = volume_from_state(optimum_n)
    optimum_c = optimum_n / optimum_volume
    optimum_rates = reaction_rates(optimum_c, k)

    initial_mass_kg = float(np.sum(n0 * molecular_weight_kg_per_kmol))
    mass_kg = n @ molecular_weight_kg_per_kmol
    mass_error_fraction = float(np.max(np.abs(mass_kg - initial_mass_kg)) / max(initial_mass_kg, 1e-12))

    reacted_x1 = np.maximum(n0[1] - n[:, 1], 0.0)
    conversion = reacted_x1 / n0[1]
    desired_yield_initial = n[:, 3] / n0[1]
    product_selectivity = np.divide(
        n[:, 3],
        n[:, 2] + n[:, 4],
        out=np.full_like(n[:, 3], np.nan),
        where=(n[:, 2] + n[:, 4]) > 1e-14,
    )
    desired_fraction_converted = np.divide(
        n[:, 3],
        reacted_x1,
        out=np.full_like(n[:, 3], np.nan),
        where=reacted_x1 > 1e-14,
    )

    opt_reacted = max(float(n0[1] - optimum_n[1]), 0.0)
    opt_conversion = opt_reacted / float(n0[1])
    opt_yield = float(optimum_n[3] / n0[1])
    opt_selectivity = (
        float(optimum_n[3] / (optimum_n[2] + optimum_n[4]))
        if (optimum_n[2] + optimum_n[4]) > 1e-14
        else float("nan")
    )
    opt_fraction_converted = float(optimum_n[3] / opt_reacted) if opt_reacted > 1e-14 else float("nan")

    return {
        "time_s": times,
        "n_kmol": n,
        "volume_m3": volumes,
        "c_kmol_m3": concentrations,
        "rates_kmol_m3_s": rates,
        "k": k,
        "conversion_x1": conversion,
        "yield_x3_on_initial_x1": desired_yield_initial,
        "selectivity_x3_to_undesired_products": product_selectivity,
        "desired_fraction_of_converted_x1": desired_fraction_converted,
        "initial_volume_m3": initial_volume,
        "initial_mass_kg": initial_mass_kg,
        "max_mass_error_fraction": mass_error_fraction,
        "solver_success": bool(solution.success),
        "solver_message": str(solution.message),
        "nfev": int(solution.nfev),
        "method": method,
        "rtol": float(rtol),
        "atol": float(atol),
        "optimum": {
            "time_s": optimum_time_s,
            "n_kmol": optimum_n,
            "volume_m3": float(optimum_volume),
            "c_kmol_m3": optimum_c,
            "rates_kmol_m3_s": optimum_rates,
            "conversion_x1": opt_conversion,
            "yield_x3_on_initial_x1": opt_yield,
            "selectivity_x3_to_undesired_products": opt_selectivity,
            "desired_fraction_of_converted_x1": opt_fraction_converted,
        },
    }
