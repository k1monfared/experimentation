"""Demonstrate hierarchical shrinkage vs naive per-segment estimates.

Segments with small samples get pulled toward the population mean.
Segments with large samples dominate their own posterior.

To play, run:

    python chapters/A2-hierarchical/play/shrinkage_demo.py
"""

N_SEGMENTS = 10
POP_MEAN = 0.05
POP_STD = 0.04         # true between-segment variability
NOISE_PER_USER = 0.5   # within-user noise
BASE_P = 0.30
SEED = 42

import sys
import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(SEED)
    true_effects = rng.normal(POP_MEAN, POP_STD, size=N_SEGMENTS)
    sample_sizes = rng.integers(20, 1000, size=N_SEGMENTS)

    observed = [rng.binomial(n, max(0, min(1, BASE_P + eff))) / n - BASE_P
                for n, eff in zip(sample_sizes, true_effects)]
    noise = [np.sqrt(BASE_P*(1-BASE_P)/n) for n in sample_sizes]

    # Simple hierarchical approximation
    sigma_pop = POP_STD
    w_obs = 1 / np.array(noise)**2
    w_pop = 1 / sigma_pop**2
    hierarchical = (w_obs * np.array(observed) + w_pop * POP_MEAN) / (w_obs + w_pop)
    shrinkage = (np.array(observed) - hierarchical) / (np.array(observed) - POP_MEAN + 1e-9)

    print(f"\n{N_SEGMENTS} segments. Population mean = {POP_MEAN*100:.1f}pp, pop std = {POP_STD*100:.1f}pp")
    print(f"\n{'Seg':3s}  {'n':>5s}  {'true':>7s}  {'naive':>7s}  {'hierarch':>9s}  {'shrinkage':>9s}")
    print("-" * 55)
    for i, (n, true, obs, hier, shr) in enumerate(zip(sample_sizes, true_effects, observed, hierarchical, shrinkage)):
        print(f"  {i+1:2d}  {n:5d}  {true*100:+6.2f}pp  {obs*100:+6.2f}pp  {hier*100:+8.2f}pp  {min(1.0, max(-1.0, shr))*100:7.0f}%")
    print(f"\nShrinkage > 50% means the segment's data was too noisy to trust — hierarchical relies mostly on the population mean.")


if __name__ == "__main__":
    main()
