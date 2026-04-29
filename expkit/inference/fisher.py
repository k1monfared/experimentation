"""Fisher's exact test for 2x2 contingency tables."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class FisherResult:
    odds_ratio: float
    p_value: float


def fisher_exact_2x2(table: np.ndarray, alternative: str = "two-sided") -> FisherResult:
    """Fisher's exact test on a 2x2 table.

    ``table`` is a 2x2 array-like of nonnegative integers. Returns the odds
    ratio and the exact p-value.
    """
    arr = np.asarray(table, dtype=int)
    if arr.shape != (2, 2):
        raise ValueError("table must be 2x2")
    odds, pval = stats.fisher_exact(arr, alternative=alternative)
    return FisherResult(odds_ratio=float(odds), p_value=float(pval))
