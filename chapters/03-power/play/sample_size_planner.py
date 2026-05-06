"""How many tosses do I need to reliably catch a bias of size X?

Set the effect size you care about and the detection target you want
(80 percent is conventional, 95 percent if you cannot afford to miss).
The script finds the smallest sample size that hits the target.

To play: change the parameters, then run with

    python chapters/03-power/play/sample_size_planner.py
"""

# Parameters you can change
TRUE_BIAS = 0.55        # what the bias actually is, the effect I care about catching
TARGET_DETECTION = 0.80 # I want the rule to catch this bias at least this often
THRESHOLD = 0.05        # the surprise threshold

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def power_two_sided(p_alt, n, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    se_null = np.sqrt(0.5 * 0.5 / n)
    se_alt = np.sqrt(p_alt * (1 - p_alt) / n)
    upper = (0.5 + z * se_null - p_alt) / se_alt
    lower = (0.5 - z * se_null - p_alt) / se_alt
    return float(stats.norm.sf(upper) + stats.norm.cdf(lower))


def main():
    if abs(TRUE_BIAS - 0.5) < 1e-6:
        print(f"\nTrue bias is 0.5 (fair). There is nothing to catch.")
        return
    lo, hi = 4, 1_000_000_000
    if power_two_sided(TRUE_BIAS, hi, THRESHOLD) < TARGET_DETECTION:
        print(f"\nEven a billion tosses cannot give {TARGET_DETECTION * 100:.0f}% detection at this threshold.")
        return
    while lo < hi:
        mid = (lo + hi) // 2
        if power_two_sided(TRUE_BIAS, mid, THRESHOLD) >= TARGET_DETECTION:
            hi = mid
        else:
            lo = mid + 1
    n_required = lo

    print(f"\nTrue bias I want to catch: {TRUE_BIAS}")
    print(f"Effect size: {abs(TRUE_BIAS - 0.5) * 100:.2f} percentage points away from fair")
    print(f"Detection target: {TARGET_DETECTION * 100:.0f}%")
    print(f"Surprise threshold: {THRESHOLD * 100:.1f}%")
    print(f"\nMinimum tosses needed: {n_required:,}")
    print(f"\nFor a sense of scale, halving the effect (to bias {0.5 + (TRUE_BIAS - 0.5) / 2:.3f}) would require about {n_required * 4:,} tosses (the sample size scales like 1 / effect squared).")


if __name__ == "__main__":
    main()
