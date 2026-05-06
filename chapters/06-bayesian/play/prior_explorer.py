"""Same data, different starting beliefs, different ending beliefs.

Pick a number of heads and tosses, and try several priors. The
script reports the posterior under each prior and shows how much
the prior matters at different sample sizes.

Try the same number of heads at different sample sizes (6/10 vs
60/100 vs 600/1000). At small N the priors disagree wildly. At
large N they all converge to the same answer.

To play, run:

    python chapters/06-bayesian/play/prior_explorer.py
"""

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
    priors = [
        (1, 1, "flat (no opinion)"),
        (50, 50, "skeptical (probably fair)"),
        (2, 8, "expects tails"),
        (8, 2, "expects heads"),
        (0.5, 0.5, "Jeffreys (mildly U-shaped)"),
    ]
    print(f"\nObservation: {k} heads in {n} tosses (fraction {k / n:.3f}).\n")
    print(f"{'Prior':30s}  {'Mean':>8s}  {'95% lo':>8s}  {'95% hi':>8s}  {'P(p>0.5)':>10s}")
    print("-" * 76)
    for a, b, label in priors:
        post_a, post_b = a + k, b + n - k
        mean = post_a / (post_a + post_b)
        lo = stats.beta.ppf(0.025, post_a, post_b)
        hi = stats.beta.ppf(0.975, post_a, post_b)
        p_above = 1 - stats.beta.cdf(0.5, post_a, post_b)
        print(f"{label:30s}  {mean:8.4f}  {lo:8.4f}  {hi:8.4f}  {p_above:10.4f}")
    print("\nAt small N the priors disagree noticeably. At large N they all converge.")


if __name__ == "__main__":
    main()
