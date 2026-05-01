"""Cochran-Mantel-Haenszel test for stratified 2x2 tables.

Use this when comparing two groups on a binary outcome across K strata
(segments, sites, time blocks). The aggregate 2x2 can be misleading
(Simpson's-paradox style); CMH gives the stratum-adjusted test of conditional
independence.

The data convention here: each stratum has a 2x2 table

    [[a_k, b_k],
     [c_k, d_k]]

with rows = group (treatment, control) and columns = outcome (success,
failure). Pass an array of shape (K, 2, 2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class CMHResult:
    statistic: float            # continuity-corrected CMH chi-square
    p_value: float              # two-sided
    common_odds_ratio: float    # Mantel-Haenszel pooled OR
    log_or: float
    log_or_se: float
    n_strata: int


def cochran_mantel_haenszel(tables: np.ndarray, continuity: bool = True) -> CMHResult:
    """Cochran-Mantel-Haenszel test on stratified 2x2 tables.

    ``tables`` has shape (K, 2, 2) where each (2, 2) layer is a stratum's
    contingency table laid out as ``[[a, b], [c, d]]``.

    Returns the chi-square statistic, two-sided p-value, and the
    Mantel-Haenszel pooled odds ratio (with a Robins-Breslow-Greenland-style
    SE for log(OR)).
    """
    arr = np.asarray(tables, dtype=float)
    if arr.ndim != 3 or arr.shape[1:] != (2, 2):
        raise ValueError("tables must have shape (K, 2, 2)")
    if np.any(arr < 0):
        raise ValueError("table entries must be non-negative")
    a = arr[:, 0, 0]
    b = arr[:, 0, 1]
    c = arr[:, 1, 0]
    d = arr[:, 1, 1]
    n = a + b + c + d
    # Drop empty strata (n == 0); they contribute nothing.
    keep = n > 0
    a, b, c, d, n = a[keep], b[keep], c[keep], d[keep], n[keep]
    if n.size == 0:
        raise ValueError("no non-empty strata")

    row1 = a + b
    col1 = a + c
    expected = row1 * col1 / n
    # Variance of a_k under the conditional null (hypergeometric).
    # Var = (row1 * row2 * col1 * col2) / (n^2 * (n - 1))
    row2 = c + d
    col2 = b + d
    denom = n * n * (n - 1)
    # Avoid div-by-zero in degenerate strata where n == 1.
    var = np.where(denom > 0, row1 * row2 * col1 * col2 / np.where(denom > 0, denom, 1.0), 0.0)

    diff = a.sum() - expected.sum()
    if continuity:
        # Mantel-Haenszel continuity correction: subtract 0.5 from |diff|.
        diff = np.sign(diff) * max(0.0, abs(diff) - 0.5)
    var_total = var.sum()
    if var_total <= 0:
        return CMHResult(0.0, 1.0, float("nan"), float("nan"), float("nan"), int(n.size))

    stat = diff ** 2 / var_total
    p = float(stats.chi2.sf(stat, df=1))

    # Mantel-Haenszel common OR: sum(a*d/n) / sum(b*c/n).
    num_or = (a * d / n).sum()
    den_or = (b * c / n).sum()
    or_mh = float(num_or / den_or) if den_or > 0 else float("nan")
    # RBG SE for log(OR_MH).
    P = (a + d) / n
    Q = (b + c) / n
    R = a * d / n
    S = b * c / n
    sumR = R.sum()
    sumS = S.sum()
    if sumR > 0 and sumS > 0:
        var_log = (
            (P * R).sum() / (2 * sumR ** 2)
            + ((P * S + Q * R)).sum() / (2 * sumR * sumS)
            + (Q * S).sum() / (2 * sumS ** 2)
        )
        se_log = float(np.sqrt(var_log))
        log_or = float(np.log(or_mh)) if or_mh > 0 else float("nan")
    else:
        se_log = float("nan")
        log_or = float("nan")

    return CMHResult(
        statistic=float(stat),
        p_value=p,
        common_odds_ratio=or_mh,
        log_or=log_or,
        log_or_se=se_log,
        n_strata=int(n.size),
    )
