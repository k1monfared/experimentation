"""Metric quality diagnostics: noise, stability, predictivity."""

from __future__ import annotations

import numpy as np


def relative_noise(values: np.ndarray) -> float:
    """Coefficient of variation: std / |mean|. Higher = noisier per unit signal.

    Only meaningful for strictly-positive metrics where the mean is far from
    zero. For zero-centered or signed effects (e.g. treatment-vs-control
    differences whose true value can be 0), the CV explodes near the origin
    and is not a useful summary; consider :func:`signal_to_noise` instead.
    """
    arr = np.asarray(values, dtype=float)
    m = float(np.mean(arr))
    if m == 0:
        return float("nan")
    return float(np.std(arr, ddof=1) / abs(m))


def signal_to_noise(values: np.ndarray, reference_scale: float | None = None) -> float:
    """A reference-scale-aware noise summary for zero-centered effects.

    For an array of measured effects (where the *true* value can be 0 or
    negative), CV is degenerate. Instead, report ``std / reference_scale``
    where ``reference_scale`` is something meaningful in the same units --
    e.g. the minimum detectable effect, an A/A spread, or 1 percentage point.

    If ``reference_scale`` is None, returns just the std.
    """
    arr = np.asarray(values, dtype=float)
    s = float(np.std(arr, ddof=1))
    if reference_scale is None:
        return s
    return s / float(reference_scale)


def stability_aa(aa_effects: np.ndarray, alpha: float = 0.05) -> dict:
    """Summary of A/A test effect distribution.

    ``aa_effects`` is the array of measured "treatment - control" values from
    A/A simulations (where the truth is no effect).

    Note: ``frac_extreme`` here divides by the *empirical* std of the same
    array, so it tests symmetry rather than calibration. For a calibration
    check (the empirical false-positive rate against alpha), pass an array
    of A/A p-values to :func:`aa_calibration` instead.
    """
    arr = np.asarray(aa_effects, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)),
        "frac_extreme": float(np.mean(np.abs(arr) > 1.96 * arr.std(ddof=1))),
    }


def aa_calibration(p_values: np.ndarray, alpha: float = 0.05) -> dict:
    """Empirical false-positive rate of an A/A pipeline.

    Pass an array of p-values from many A/A tests (truth: no effect). A
    calibrated test rejects in ``alpha`` fraction of trials. Returns the
    empirical rate, the nominal alpha, and a 95% binomial CI on the rate.
    """
    p = np.asarray(p_values, dtype=float)
    n = int(p.size)
    rejects = int((p < alpha).sum())
    rate = rejects / n if n else float("nan")
    if n:
        from statsmodels.stats.proportion import proportion_confint

        lo, hi = proportion_confint(rejects, n, alpha=0.05, method="wilson")
    else:
        lo, hi = float("nan"), float("nan")
    return {
        "n_trials": n,
        "alpha": float(alpha),
        "empirical_rate": float(rate),
        "ci_95_low": float(lo),
        "ci_95_high": float(hi),
    }


def predictivity(
    short_term: np.ndarray,
    long_term: np.ndarray,
    *,
    n_boot: int = 0,
    seed: int | None = None,
    alpha: float = 0.05,
) -> dict:
    """Correlation between short-term and long-term per-experiment effects.

    Returns Pearson r and the in-sample R^2 from the linear fit. When
    ``n_boot > 0`` the result also includes a non-parametric bootstrap CI
    for ``r``: ``ci_95_low`` and ``ci_95_high`` (each row is resampled
    jointly from the (short, long) pairs).
    """
    s = np.asarray(short_term, dtype=float)
    l = np.asarray(long_term, dtype=float)
    if len(s) != len(l):
        raise ValueError("short_term and long_term must have the same length")
    cov = np.cov(s, l, ddof=1)
    r = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    out: dict = {"pearson_r": float(r), "r_squared": float(r ** 2)}
    if n_boot > 0:
        rng = np.random.default_rng(seed)
        n = len(s)
        rs = np.empty(n_boot, dtype=float)
        for i in range(n_boot):
            idx = rng.integers(0, n, size=n)
            ss, ll = s[idx], l[idx]
            c = np.cov(ss, ll, ddof=1)
            rs[i] = c[0, 1] / np.sqrt(c[0, 0] * c[1, 1])
        out["ci_95_low"] = float(np.quantile(rs, alpha / 2))
        out["ci_95_high"] = float(np.quantile(rs, 1 - alpha / 2))
        out["n_boot"] = int(n_boot)
    return out
