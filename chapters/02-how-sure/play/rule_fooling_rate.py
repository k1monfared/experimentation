"""How often does the surprise rule actually catch a real bias?

The chapter shows a chart of how often the rule rings the alarm under
various truths and sample sizes. This script lets me run the
experiment myself: pick a true bias and a sample size, run the
experiment 1000 times, and count how often the rule fires.

To play: change the parameters, then run with

    python chapters/02-how-sure/play/rule_fooling_rate.py
"""

# Parameters you can change
TRUE_BIAS = 0.55        # the actual bias of the coin (0.5 = fair, 0.55 = slightly heavy)
N_TOSSES = 100          # how many tosses per experiment
THRESHOLD = 0.05        # the surprise threshold
N_EXPERIMENTS = 1000    # how many experiments to run

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)

    # Run N_EXPERIMENTS experiments, each one tossing the coin N_TOSSES times.
    head_counts = rng.binomial(N_TOSSES, TRUE_BIAS, size=N_EXPERIMENTS)

    # For each experiment, run a two-sided exact binomial test against H0: p=0.5.
    # Count how many times the test's p-value falls below the threshold.
    rejections = 0
    for k in head_counts:
        pval = stats.binomtest(int(k), N_TOSSES, p=0.5, alternative="two-sided").pvalue
        if pval < THRESHOLD:
            rejections += 1

    rate = rejections / N_EXPERIMENTS

    print(f"\nTrue coin bias: {TRUE_BIAS}")
    print(f"Experiment size: {N_TOSSES} tosses")
    print(f"Surprise threshold: {THRESHOLD * 100:.1f}%")
    print(f"Number of experiments: {N_EXPERIMENTS}")
    print(f"\nThe rule rang the alarm in {rejections} of {N_EXPERIMENTS} experiments ({rate * 100:.1f}%).\n")

    if abs(TRUE_BIAS - 0.5) < 1e-6:
        print(f"Coin is fair, so the rule should ring the alarm at most {THRESHOLD * 100:.1f}% of the time.")
        print(f"It rang {rate * 100:.1f}%, which is {'within' if rate <= THRESHOLD * 1.5 else 'higher than'} budget.")
    else:
        print(f"Coin is biased. The rule's job is to catch this.")
        print(f"It caught the bias {rate * 100:.1f}% of the time at this sample size.")
        if rate < 0.5:
            print(f"That is below half. Most of the time, the rule misses the real bias.")
        elif rate > 0.9:
            print(f"That is well above 90%. The rule reliably catches this bias at this sample size.")


if __name__ == "__main__":
    main()
