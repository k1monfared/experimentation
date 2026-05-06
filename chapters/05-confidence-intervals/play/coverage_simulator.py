"""Do these 95% intervals actually contain the truth 95% of the time?

A 95% interval is a procedure with a promise. If I run the procedure
many times under conditions where I know the truth, the interval
should contain the truth in about 95% of those runs.

This script simulates many experiments at a chosen true bias and a
chosen sample size, computes each interval, and counts how often the
true bias was inside.

Try TRUE_BIAS = 0.5 with N_TOSSES = 5: the simple bell-curve interval
("Wald") badly under-covers. Try N_TOSSES = 100: all four procedures
are near 95%. Try TRUE_BIAS = 0.05 (rare event): Wald breaks again.

To play, run:

    python chapters/05-confidence-intervals/play/coverage_simulator.py
"""

# Parameters
TRUE_BIAS = 0.5
N_TOSSES = 30
N_TRIALS = 5000

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)
    n = N_TOSSES
    p_true = TRUE_BIAS
    z = stats.norm.ppf(0.975)

    ks = rng.binomial(n, p_true, size=N_TRIALS)
    cov = {"Wald": 0, "Wilson": 0, "Clopper-Pearson": 0, "Belief": 0}
    for k in ks:
        # Wald
        p = k / n
        se = np.sqrt(p * (1 - p) / n)
        wlo, whi = max(0, p - z * se), min(1, p + z * se)
        if wlo <= p_true <= whi: cov["Wald"] += 1
        # Wilson
        denom = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        wilo, wihi = max(0, centre - half), min(1, centre + half)
        if wilo <= p_true <= wihi: cov["Wilson"] += 1
        # Clopper-Pearson
        cplo = stats.beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
        cphi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
        if cplo <= p_true <= cphi: cov["Clopper-Pearson"] += 1
        # Belief
        blo = stats.beta.ppf(0.025, 1 + k, 1 + n - k)
        bhi = stats.beta.ppf(0.975, 1 + k, 1 + n - k)
        if blo <= p_true <= bhi: cov["Belief"] += 1

    print(f"\nTrue bias: {p_true}")
    print(f"Sample size: {n}")
    print(f"Number of simulated experiments: {N_TRIALS}")
    print(f"\nFraction of '95% intervals' that actually contained the true bias:\n")
    for name, count in cov.items():
        frac = count / N_TRIALS
        verdict = "OK" if abs(frac - 0.95) < 0.02 else ("under-covers (broken promise)" if frac < 0.93 else "over-covers (conservative)")
        print(f"  {name:18s}: {frac:.3f}  [{verdict}]")
    print(f"\nA procedure is honest about '95%' only if its coverage is near 95% across the parameter space.")
    print(f"Try TRUE_BIAS = 0.05 to see Wald break at the boundary.")


if __name__ == "__main__":
    main()
