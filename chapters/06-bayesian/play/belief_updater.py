"""Watch the belief curve update toss by toss.

Pick a starting belief (the prior parameters) and a true bias.
Toss the coin a chosen number of times and watch how the belief
curve narrows around the true bias as data accumulates.

Try different priors:
  PRIOR_A = 1, PRIOR_B = 1   : flat (no opinion)
  PRIOR_A = 50, PRIOR_B = 50 : skeptical (probably fair)
  PRIOR_A = 8, PRIOR_B = 2   : expects heads
  PRIOR_A = 0.5, PRIOR_B = 0.5 : Jeffreys prior

To play, run:

    python chapters/06-bayesian/play/belief_updater.py
"""

PRIOR_A = 1
PRIOR_B = 1
TRUE_BIAS = 0.55
N_TOSSES = 1000

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)
    seq = rng.binomial(1, TRUE_BIAS, size=N_TOSSES)
    print(f"\nStarting belief: Beta({PRIOR_A}, {PRIOR_B})")
    print(f"  prior mean: {PRIOR_A / (PRIOR_A + PRIOR_B):.4f}")
    print(f"True bias: {TRUE_BIAS}")
    print(f"\nBelief at checkpoints:\n")
    for n in [1, 10, 100, 1000, N_TOSSES]:
        if n > N_TOSSES:
            continue
        k = int(seq[:n].sum())
        a, b = PRIOR_A + k, PRIOR_B + n - k
        mean = a / (a + b)
        lo = stats.beta.ppf(0.025, a, b)
        hi = stats.beta.ppf(0.975, a, b)
        print(f"  after {n:5d} tosses ({k} heads): mean = {mean:.4f}, 95% band [{lo:.4f}, {hi:.4f}], width = {hi - lo:.4f}")


if __name__ == "__main__":
    main()
