"""Bootstrap confidence intervals."""

from __future__ import annotations

from typing import Callable

import numpy as np


def bootstrap_ci(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float] | None = None,
    n_boot: int = 5000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> tuple[float, float, np.ndarray]:
    """Percentile-bootstrap confidence interval for ``statistic``.

    Default statistic is the mean. Returns ``(lo, hi, draws)`` where ``draws``
    is the bootstrap distribution of the statistic.
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(data)
    n = len(arr)
    if statistic is None:
        statistic = np.mean
    draws = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        draws[i] = float(statistic(arr[idx]))
    lo = float(np.quantile(draws, alpha / 2))
    hi = float(np.quantile(draws, 1 - alpha / 2))
    return lo, hi, draws
