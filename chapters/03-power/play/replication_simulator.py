"""If I run the same experiment many times, how often does the rule fire?

The "80 percent detection at this sample size" target sounds reassuring,
but it averages over many runs. Any one run can still miss the bias.
This script makes the variability visible: it runs the same experiment
ten times, repeats that group of ten many times, and shows how often
each catch-count happens.

Try changing N_REPLICATIONS to 1 to see how varied a single experiment
is. Or change BIAS to 0.52 (smaller effect, even with the recommended
N most experiments will miss the bias) to see why small studies are
unreliable witnesses.

To play, run:

    python chapters/03-power/play/replication_simulator.py
"""

# Parameters
TRUE_BIAS = 0.55             # the actual bias of the coin
N_TOSSES = 780               # the recommended sample size for 80 percent detection at bias 0.55
N_REPLICATIONS = 10          # how many times I run the experiment in each group
N_GROUPS = 1000              # how many groups to simulate (for the histogram)
THRESHOLD = 0.05             # the surprise threshold

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(424)
    catches_per_group = np.zeros(N_GROUPS, dtype=int)
    for g in range(N_GROUPS):
        for _ in range(N_REPLICATIONS):
            head_count = rng.binomial(N_TOSSES, TRUE_BIAS)
            pval = stats.binomtest(int(head_count), N_TOSSES, p=0.5, alternative="two-sided").pvalue
            if pval < THRESHOLD:
                catches_per_group[g] += 1

    counts = np.bincount(catches_per_group, minlength=N_REPLICATIONS + 1)
    expected_catches_per_group = N_REPLICATIONS * 0.8  # if true detection rate is 80%

    print(f"\nSimulated {N_GROUPS} groups, each running {N_REPLICATIONS} experiments.")
    print(f"Each experiment: {N_TOSSES} tosses of a coin biased to {TRUE_BIAS}.")
    print(f"\nDistribution of how many of {N_REPLICATIONS} experiments caught the bias:")
    for k, c in enumerate(counts):
        bar = "#" * (int(c / counts.max() * 60) if counts.max() > 0 else 0)
        print(f"  {k:2d} catches: {c:4d} groups  {bar}")
    print(f"\nMean catches per group: {catches_per_group.mean():.2f} (expected ~{expected_catches_per_group:.1f})")
    print(f"Worst 1% of groups caught {np.percentile(catches_per_group, 1):.0f} or fewer.")
    print(f"Best 1% caught {np.percentile(catches_per_group, 99):.0f} or more.")
    print(f"\nThe spread is real: 'eighty percent detection' does not mean every group lands at eight catches.")
    print(f"Some groups by sheer luck see only four or five. Some see ten.")


if __name__ == "__main__":
    main()
