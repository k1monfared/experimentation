"""Same observation, three different procedures, three different answers.

Pick a number of heads and a total number of tosses. The script runs
three different procedures that all answer "is this coin fair?" and
compares their p-values.

The three procedures are described in Chapter 4. In one phrase each:
  - honest count: count every fair-coin outcome at least as extreme.
  - bell-curve approximation: pretend the result is normally distributed.
  - proxy-crowd procedure: pair my data with an idealized fair sample,
    run a 2x2 test (this is Fisher's exact, force-fitted to one sample).

Try observations that are clearly fair (50 in 100), clearly biased
(70 in 100), or borderline (60 in 100, 6 in 10) to see how the three
procedures agree and disagree.

To play, run:

    python chapters/04-test-family/play/multi_test_calculator.py
"""

# Parameters
HEADS = 60
N_TOSSES = 100

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

    # Honest count
    p_honest = stats.binomtest(k, n, p=0.5, alternative="two-sided").pvalue

    # Bell-curve approximation
    if n == 0:
        p_bell = 1.0
    else:
        p_hat = k / n
        se = np.sqrt(0.5 * 0.5 / n)
        z = (p_hat - 0.5) / se if se > 0 else 0.0
        p_bell = float(2 * stats.norm.sf(abs(z)))

    # Proxy-crowd procedure
    half = n / 2
    table = [[k, n - k], [int(round(half)), int(round(half))]]
    p_proxy = float(stats.fisher_exact(table)[1])

    print(f"\nObservation: {k} heads in {n} tosses ({k / n * 100:.1f}% heads).\n")
    print(f"Three procedures, three p-values for testing 'is the coin fair (p = 0.5)':")
    print(f"  Honest count                : p = {p_honest:.4f}")
    print(f"  Bell-curve approximation    : p = {p_bell:.4f}")
    print(f"  Proxy-crowd procedure       : p = {p_proxy:.4f}\n")
    print(f"At alpha = 0.05:")
    for name, p in [("Honest count", p_honest), ("Bell-curve", p_bell), ("Proxy-crowd", p_proxy)]:
        verdict = "REJECT (the coin is suspicious)" if p < 0.05 else "DO NOT REJECT (data is consistent with fair)"
        print(f"  {name:25s}: {verdict}")
    print(f"\nIf the three procedures disagreed, you have hit the borderline territory.")
    print(f"At a clear signal (say 70 in 100), all three agree on 'reject'.")
    print(f"At a clearly fair-looking result (say 50 in 100), all three agree on 'do not reject'.")


if __name__ == "__main__":
    main()
