"""Plot-only transformations of solved closed-batch molar inventories.

These functions never affect integration or parameter estimation.
"""
from __future__ import annotations

import numpy as np


def plot_values(amounts, molecular_weights, variable, *, reactant=None, product=None, stoich_ratio=1.0):
    n = np.asarray(amounts, dtype=float)
    if n.ndim != 2:
        raise ValueError('Amounts must be a time-by-species matrix.')
    mw = np.asarray(molecular_weights, dtype=float)
    if variable == 'Mole fraction':
        total = np.sum(n, axis=1)
        out = np.full_like(n, np.nan)
        np.divide(n, total[:, None], out=out, where=(total > 0)[:, None])
        return out
    if variable == 'Mass fraction':
        if mw.shape != (n.shape[1],) or np.any(~np.isfinite(mw)) or np.any(mw <= 0):
            raise ValueError('Positive molecular weights are required for every species.')
        masses = n * mw[None, :]
        total = np.sum(masses, axis=1)
        out = np.full_like(n, np.nan)
        np.divide(masses, total[:, None], out=out, where=(total > 0)[:, None])
        return out
    if variable == 'Net conversion':
        if reactant is None or n[0, reactant] <= 0:
            raise ValueError('The reference reactant must have a positive initial amount.')
        return (n[0, reactant] - n[:, reactant]) / n[0, reactant]
    if variable == 'Overall selectivity':
        if product is None or reactant is None or product == reactant or stoich_ratio <= 0:
            raise ValueError('Choose different product and reactant species and a positive stoichiometric ratio.')
        denominator = n[0, reactant] - n[:, reactant]
        numerator = n[:, product] - n[0, product]
        values = np.full(n.shape[0], np.nan, dtype=float)
        tol = max(1e-12, abs(float(n[0, reactant])) * 1e-10)
        np.divide(numerator, stoich_ratio * denominator, out=values, where=denominator > tol)
        return values
    raise ValueError(f'Unknown plot variable: {variable}')
