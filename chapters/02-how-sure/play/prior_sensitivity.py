"""How much does my starting belief change the ending belief?

The chapter notes that a flat prior is only one choice. If I walk in
expecting the coin is probably fair, or expecting it is rigged low, the
same data pulls my belief to a different place. This script lets me
pick any starting prior (as Beta shape parameters) and any observation
and see the ending belief curve.

Try PRIOR_A = 50, PRIOR_B = 50 (strong fair-leaning) with OBSERVED = 60
and N = 100. Then keep the same prior and try OBSERVED = 600, N = 1000.
With enough data the prior stops mattering.

To play: change the parameters, then run with

    python chapters/02-how-sure/play/prior_sensitivity.py
"""

# Parameters you can change
PRIOR_A = 1            # pseudo-heads in the prior (1 = flat, 50 = expects fair)
PRIOR_B = 1            # pseudo-tails in the prior
OBSERVED_HEADS = 60    # how many heads I actually saw
N_TOSSES = 100         # how many times I tossed

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from expkit.plot.story import PALETTE, apply_story_style


def main():
    apply_story_style()
    if OBSERVED_HEADS < 0 or OBSERVED_HEADS > N_TOSSES:
        raise ValueError("OBSERVED_HEADS must be between 0 and N_TOSSES")
    if PRIOR_A <= 0 or PRIOR_B <= 0:
        raise ValueError("PRIOR_A and PRIOR_B must be positive")

    a = PRIOR_A + OBSERVED_HEADS
    b = PRIOR_B + (N_TOSSES - OBSERVED_HEADS)
    ps = np.linspace(0.001, 0.999, 1000)
    prior = stats.beta.pdf(ps, PRIOR_A, PRIOR_B)
    posterior = stats.beta.pdf(ps, a, b)

    prior_mean = PRIOR_A / (PRIOR_A + PRIOR_B)
    post_mean = a / (a + b)
    lo = stats.beta.ppf(0.025, a, b)
    hi = stats.beta.ppf(0.975, a, b)
    prob_above_half = 1.0 - stats.beta.cdf(0.5, a, b)

    print(f"\nPrior: Beta({PRIOR_A}, {PRIOR_B}), mean {prior_mean:.3f}.")
    print(f"Observation: {OBSERVED_HEADS} heads in {N_TOSSES} tosses.")
    print(f"Posterior: Beta({a}, {b}), mean {post_mean:.3f}.")
    print(f"95% range of plausible bias: [{lo:.3f}, {hi:.3f}].")
    print(f"P(bias > 0.5) under this prior and data: {prob_above_half:.3f}.\n")

    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.plot(ps, prior, color=PALETTE["muted"], linewidth=1.6, alpha=0.8,
            label=f"prior Beta({PRIOR_A}, {PRIOR_B})")
    ax.fill_between(ps, 0, posterior, color=PALETTE["focus"], alpha=0.35)
    ax.plot(ps, posterior, color=PALETTE["focus"], linewidth=2.0,
            label=f"posterior after {OBSERVED_HEADS}/{N_TOSSES}")
    ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1.0)
    ax.set_xlim(0, 1)
    ax.set_xlabel("possible fairness of the coin")
    ax.set_ylabel("how strongly I believe each value")
    ax.set_title("prior meets data")
    ax.legend(loc="upper left")
    plt.show()


if __name__ == "__main__":
    main()
