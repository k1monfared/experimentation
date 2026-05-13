"""Predictivity of a short-term metric for a long-term outcome.

Each of N_EXPERIMENTS experiments has a true latent effect drawn from a
zero-mean normal. A short-term metric adds SHORT_NOISE_SIGMA of
measurement noise on top. A long-term metric adds LONG_NOISE_SIGMA
(typically smaller, because it averages over more time). The script
prints how tightly the short-term metric anticipates the long-term one.

Watch the headline correlation move as you change the noise ratio. Try
N_EXPERIMENTS=50 and see the bootstrap CI widen: predictive validity is
itself a measurement, and small programs cannot pin it down.

To play, run:

    python chapters/13-metric-tree/play/predictivity_simulator.py
"""

N_EXPERIMENTS = 200
TRUE_EFFECT_SIGMA = 0.02
SHORT_NOISE_SIGMA = 0.03
LONG_NOISE_SIGMA = 0.01
SEED = 0

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy.stats import spearmanr


def main():
    rng = np.random.default_rng(SEED)
    truths = rng.normal(0, TRUE_EFFECT_SIGMA, size=N_EXPERIMENTS)
    short = truths * 0.6 + rng.normal(0, SHORT_NOISE_SIGMA, size=N_EXPERIMENTS)
    long = truths * 0.9 + rng.normal(0, LONG_NOISE_SIGMA, size=N_EXPERIMENTS)

    r = float(np.corrcoef(short, long)[0, 1])
    rho, _ = spearmanr(short, long)

    # Bootstrap CI on Pearson r
    rng_b = np.random.default_rng(SEED)
    n_boot = 1000
    rs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng_b.integers(0, N_EXPERIMENTS, size=N_EXPERIMENTS)
        c = np.cov(short[idx], long[idx], ddof=1)
        rs[i] = c[0, 1] / np.sqrt(c[0, 0] * c[1, 1])
    lo, hi = np.quantile(rs, [0.025, 0.975])

    # How often does short-term point the same way as long-term?
    agree = float(np.mean(np.sign(short) == np.sign(long)))
    # Of experiments the short metric calls positive, what fraction were really negative?
    shipped = short > 0
    ship_negatives = float(np.mean(long[shipped] < 0)) if shipped.any() else float("nan")

    print(f"\nN = {N_EXPERIMENTS}, short noise = {SHORT_NOISE_SIGMA}, long noise = {LONG_NOISE_SIGMA}")
    print(f"Pearson r  = {r:+.2f}   95% bootstrap CI [{lo:+.2f}, {hi:+.2f}]")
    print(f"Spearman rho = {rho:+.2f}   (close to Pearson when the link is linear)")
    print(f"R^2        = {r * r:.2f}   (fraction of long-term variance the short-term explains)")
    print(f"Sign agreement short vs long: {agree:.0%}")
    print(f"Of experiments the short metric calls positive, long says negative: {ship_negatives:.0%}")
    print()
    if r > 0.5:
        print("The short metric is a useful proxy. Headline still uncertain.")
    elif r > 0.2:
        print("Short metric is weakly predictive. Individual reads are noisy guesses.")
    else:
        print("Short metric barely predicts. Optimizing it may not move the truth.")


if __name__ == "__main__":
    main()
