"""How often will my rule catch a real bias of size X with N tosses?

Pick a true bias and a sample size, run the simulator a few thousand
times, count how often the surprise rule fires. This is "power" in
the textbook word, the chance of catching a real effect.

To play: change the parameters, then run with

    python chapters/03-power/play/power_explorer.py
"""

# Parameters you can change
TRUE_BIAS = 0.55        # the actual bias of the coin
N_TOSSES = 200          # how many tosses per experiment
THRESHOLD = 0.05        # the surprise threshold
N_EXPERIMENTS = 2000    # how many fake experiments to run

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)
    head_counts = rng.binomial(N_TOSSES, TRUE_BIAS, size=N_EXPERIMENTS)
    rejections = 0
    for k in head_counts:
        pval = stats.binomtest(int(k), N_TOSSES, p=0.5, alternative="two-sided").pvalue
        if pval < THRESHOLD:
            rejections += 1
    rate = rejections / N_EXPERIMENTS

    print(f"\nTrue bias: {TRUE_BIAS}")
    print(f"Sample size: {N_TOSSES}")
    print(f"Threshold: {THRESHOLD * 100:.1f}%")
    print(f"Number of experiments: {N_EXPERIMENTS}")
    print(f"\nThe rule caught the bias in {rejections} of {N_EXPERIMENTS} experiments ({rate * 100:.1f}%).")
    if abs(TRUE_BIAS - 0.5) < 1e-6:
        print(f"(The coin is actually fair, so this is the false alarm rate. It should be near {THRESHOLD * 100:.1f}%.)")
    elif rate < 0.5:
        print(f"That is below half. With this sample size, the rule is missing the bias more than catching it.")
    elif rate > 0.9:
        print(f"That is above 90%. The sample is large enough that the rule reliably catches this bias.")
    else:
        print(f"Detection is moderate. Doubling the sample size would push it noticeably higher.")


if __name__ == "__main__":
    main()
