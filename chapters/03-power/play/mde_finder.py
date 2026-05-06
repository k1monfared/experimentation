"""Given my sample size, what is the smallest bias I could realistically detect?

The minimum detectable effect, or MDE: with N tosses available, what
is the smallest deviation from fair that the rule would catch
reliably?

To play: change the parameters, then run with

    python chapters/03-power/play/mde_finder.py
"""

# Parameters you can change
N_TOSSES = 1000          # the budget I have for tosses (or patients, or users)
TARGET_DETECTION = 0.80  # how often I need the rule to fire when an effect is real
THRESHOLD = 0.05         # the surprise threshold

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
    # Bisect to find the smallest p_alt > 0.5 with detection >= target
    lo, hi = 0.5001, 0.999
    if power_two_sided(hi, N_TOSSES, THRESHOLD) < TARGET_DETECTION:
        print(f"\nEven a coin biased to heads-99.9% does not hit the detection target with {N_TOSSES} tosses.")
        return
    for _ in range(60):
        mid = (lo + hi) / 2
        if power_two_sided(mid, N_TOSSES, THRESHOLD) >= TARGET_DETECTION:
            hi = mid
        else:
            lo = mid
    mde_bias = (lo + hi) / 2
    mde_pp = (mde_bias - 0.5) * 100

    print(f"\nSample size: {N_TOSSES:,} tosses")
    print(f"Detection target: {TARGET_DETECTION * 100:.0f}%")
    print(f"Surprise threshold: {THRESHOLD * 100:.1f}%")
    print(f"\nMinimum detectable bias: about {mde_bias:.4f} (about {mde_pp:.2f} percentage points above fair)")
    print(f"\nMeaning: with this many tosses, anything closer to 0.5 than {mde_bias:.4f} will probably slip through the rule.")
    print(f"To halve the detectable effect (catch {mde_pp / 2:.2f} pp), I would need about {N_TOSSES * 4:,} tosses.")


if __name__ == "__main__":
    main()
