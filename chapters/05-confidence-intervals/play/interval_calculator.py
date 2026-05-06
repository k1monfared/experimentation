"""Several interval procedures applied to one observation.

Pick a number of heads and a total number of tosses. The script
computes four different 95-percent intervals around the observed
fraction and prints them side by side.

Try observations like 0/10 (boundary, where Wald collapses), 60/100
(borderline, where they all roughly agree), 600/1000 (clear signal,
where they almost coincide).

To play, run:

    python chapters/05-confidence-intervals/play/interval_calculator.py
"""

# Parameters
HEADS = 60
N_TOSSES = 100
LEVEL = 0.95

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    k, n = HEADS, N_TOSSES
    if k < 0 or k > n:
        raise ValueError("HEADS must be between 0 and N_TOSSES")
    z = stats.norm.ppf((1 + LEVEL) / 2)
    alpha = 1 - LEVEL

    # Wald
    p = k / n if n > 0 else 0.5
    se = np.sqrt(p * (1 - p) / n) if n > 0 else 0.5
    wald = (max(0, p - z * se), min(1, p + z * se))

    # Wilson
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    wilson = (max(0, centre - half), min(1, centre + half))

    # Clopper-Pearson
    cp_lo = stats.beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    cp_hi = stats.beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0

    # Bayesian (flat prior)
    bayes_lo = stats.beta.ppf(alpha / 2, 1 + k, 1 + n - k)
    bayes_hi = stats.beta.ppf(1 - alpha / 2, 1 + k, 1 + n - k)

    print(f"\nObservation: {k} heads in {n} tosses (fraction {k / n:.3f}).")
    print(f"Asking for {LEVEL * 100:.0f}% intervals.\n")
    print(f"  simple bell-curve interval     : [{wald[0]:.3f}, {wald[1]:.3f}]  width {wald[1] - wald[0]:.3f}")
    print(f"  shrunken-centre interval       : [{wilson[0]:.3f}, {wilson[1]:.3f}]  width {wilson[1] - wilson[0]:.3f}")
    print(f"  guaranteed-coverage interval   : [{cp_lo:.3f}, {cp_hi:.3f}]  width {cp_hi - cp_lo:.3f}")
    print(f"  belief-curve interval          : [{bayes_lo:.3f}, {bayes_hi:.3f}]  width {bayes_hi - bayes_lo:.3f}\n")
    if k == 0 or k == n:
        print(f"Notice: simple bell-curve interval collapses to a point at boundary observations.")
        print(f"It tells me I can rule out everything, which is the worst possible answer with no data on the other side.")


if __name__ == "__main__":
    main()
