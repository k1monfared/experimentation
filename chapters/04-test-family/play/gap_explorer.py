"""How big is the gap between honest count and bell-curve approximation?

The bell-curve approximation gets the right answer in the middle (around
the typical fraction of heads) and lies near the boundaries (very few
or very many heads). The size of the lie shrinks as the sample size
grows.

This script computes both procedures across every possible number of
heads for a given sample size, and reports where the gap is largest.

To play, run:

    python chapters/04-test-family/play/gap_explorer.py
"""

# Parameters
N_TOSSES = 50

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    n = N_TOSSES
    gaps = []
    for k in range(n + 1):
        p_honest = stats.binomtest(k, n, p=0.5, alternative="two-sided").pvalue
        p_hat = k / n
        se = np.sqrt(0.25 / n)
        z = (p_hat - 0.5) / se if se > 0 else 0.0
        p_bell = float(2 * stats.norm.sf(abs(z)))
        gaps.append(abs(p_honest - p_bell))

    gaps = np.array(gaps)
    worst_k = int(np.argmax(gaps))
    p_honest_worst = stats.binomtest(worst_k, n, p=0.5, alternative="two-sided").pvalue
    p_hat = worst_k / n
    z = (p_hat - 0.5) / np.sqrt(0.25 / n) if n else 0.0
    p_bell_worst = float(2 * stats.norm.sf(abs(z)))

    print(f"\nSample size: {n} tosses\n")
    print(f"Largest gap between honest count and bell-curve approximation:")
    print(f"  At {worst_k} heads in {n} tosses:")
    print(f"    Honest count: {p_honest_worst:.4f}")
    print(f"    Bell-curve  : {p_bell_worst:.4f}")
    print(f"    Gap         : {gaps[worst_k]:.4f}\n")
    print(f"Median gap across all observations: {np.median(gaps):.4f}")
    print(f"Maximum gap: {gaps.max():.4f}")
    print(f"\nTry larger N to see the gap shrink. At N = 1000, the worst gap is around 0.025.")
    print(f"At N = 10000, the worst gap is below 0.01.")


if __name__ == "__main__":
    main()
