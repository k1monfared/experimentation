"""Chi-square tests: goodness-of-fit and 2xK contingency."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Chi2Result:
    statistic: float
    p_value: float
    dof: int
    expected: np.ndarray


def goodness_of_fit(observed: np.ndarray, expected_p: np.ndarray | None = None) -> Chi2Result:
    """Chi-square goodness-of-fit test.

    ``expected_p`` is the null probability vector (sums to 1). If None, the
    null is uniform across categories.
    """
    obs = np.asarray(observed, dtype=float)
    n = obs.sum()
    if expected_p is None:
        expected_p = np.full_like(obs, 1.0 / len(obs))
    exp = np.asarray(expected_p, dtype=float) * n
    res = stats.chisquare(obs, f_exp=exp)
    return Chi2Result(statistic=float(res.statistic), p_value=float(res.pvalue), dof=len(obs) - 1, expected=exp)


def contingency(table: np.ndarray) -> Chi2Result:
    """Chi-square test of independence on a contingency table."""
    arr = np.asarray(table, dtype=float)
    chi2, pval, dof, exp = stats.chi2_contingency(arr)
    return Chi2Result(statistic=float(chi2), p_value=float(pval), dof=int(dof), expected=exp)
