"""Three priors, one observation. Where do you land?

Pick a prior (Beta distribution shape parameters A and B), pick an
observation (HEADS out of N_TOSSES), and see the posterior: its centre,
its 95-percent credible interval, and how far the data moved you from
where you started.

Try A=1, B=1 (flat, no opinion), A=50, B=50 (sharp skeptical prior
centred on fair), A=2, B=8 (prior that expects tails) with HEADS=60,
N_TOSSES=100. Same data, three different ending beliefs. Then change
N_TOSSES to 10 and to 1000 and watch how quickly the prior loses the
argument as data grows.

To play, run:

    python chapters/05-confidence-intervals/play/prior_playground.py
"""

# Parameters
PRIOR_A = 1.0
PRIOR_B = 1.0
HEADS = 60
N_TOSSES = 100
LEVEL = 0.95

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scipy import stats


def main():
    a0, b0 = PRIOR_A, PRIOR_B
    k, n = HEADS, N_TOSSES
    if k < 0 or k > n:
        raise ValueError("HEADS must be between 0 and N_TOSSES")
    if a0 <= 0 or b0 <= 0:
        raise ValueError("PRIOR_A and PRIOR_B must both be positive")

    alpha = 1 - LEVEL
    prior_mean = a0 / (a0 + b0)
    post_a, post_b = a0 + k, b0 + (n - k)
    post_mean = post_a / (post_a + post_b)
    lo = stats.beta.ppf(alpha / 2, post_a, post_b)
    hi = stats.beta.ppf(1 - alpha / 2, post_a, post_b)

    # how much did the data actually move the belief
    p_hat = k / n
    pulled_toward_data = (post_mean - prior_mean) / (p_hat - prior_mean) if p_hat != prior_mean else float("nan")

    print(f"\nPrior:      Beta({a0:g}, {b0:g}),  prior mean = {prior_mean:.3f}")
    print(f"Observation: {k} heads in {n} tosses (fraction {p_hat:.3f}).")
    print(f"Posterior:  Beta({post_a:g}, {post_b:g}),  posterior mean = {post_mean:.3f}")
    print(f"{LEVEL * 100:.0f}% credible interval: [{lo:.3f}, {hi:.3f}]  width {hi - lo:.3f}")
    if p_hat != prior_mean:
        print(f"The data pulled the mean {pulled_toward_data * 100:.0f}% of the way from the prior toward the observed fraction.")
    print("\nTry a different prior strength: Beta(1,1) is flat, Beta(50,50) is sharp, Beta(2,8) leans tails.")
    print("Try a different sample size: small N keeps the prior in charge; large N lets the data win.")


if __name__ == "__main__":
    main()
