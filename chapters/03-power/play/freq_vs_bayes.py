"""When do the two ways of thinking actually disagree?

The frequentist way (does the data fall in the surprise zone) and the
belief-curve way (does the 95 percent band of plausible biases exclude
0.5) are different procedures answering related questions. This script
simulates many experiments under a chosen truth and counts how often
the two methods agree, and how often they disagree.

The pattern: at large sample sizes they agree almost always. Near the
threshold of detectability they sometimes diverge. The disagreement is
real but it is small.

To play, run:

    python chapters/03-power/play/freq_vs_bayes.py
"""

# Parameters
TRUE_BIAS = 0.55
N_TOSSES = 200
N_EXPERIMENTS = 2000
THRESHOLD = 0.05         # both methods use 5% (i.e. 95% credibility for Bayesian)

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(7)
    head_counts = rng.binomial(N_TOSSES, TRUE_BIAS, size=N_EXPERIMENTS)

    both_biased = both_fair = only_freq = only_bayes = 0
    for k in head_counts:
        # Frequentist: surprise zone
        pval = stats.binomtest(int(k), N_TOSSES, p=0.5, alternative="two-sided").pvalue
        freq_says_biased = pval < THRESHOLD
        # Bayesian: 95% credible interval excludes 0.5
        lo = stats.beta.ppf(THRESHOLD / 2, 1 + k, 1 + N_TOSSES - k)
        hi = stats.beta.ppf(1 - THRESHOLD / 2, 1 + k, 1 + N_TOSSES - k)
        bayes_says_biased = (lo > 0.5) or (hi < 0.5)
        if freq_says_biased and bayes_says_biased: both_biased += 1
        elif freq_says_biased: only_freq += 1
        elif bayes_says_biased: only_bayes += 1
        else: both_fair += 1

    agree = both_biased + both_fair
    disagree = only_freq + only_bayes

    print(f"\nTrue bias: {TRUE_BIAS}")
    print(f"Sample size: {N_TOSSES}")
    print(f"Both methods at the same threshold: {(1 - THRESHOLD) * 100:.0f}% confidence.")
    print(f"Number of simulated experiments: {N_EXPERIMENTS}\n")

    print(f"  Both methods called the coin biased:  {both_biased:5d}  ({both_biased / N_EXPERIMENTS * 100:.1f}%)")
    print(f"  Both methods called the coin fair:    {both_fair:5d}  ({both_fair / N_EXPERIMENTS * 100:.1f}%)")
    print(f"  Only the surprise rule called biased: {only_freq:5d}  ({only_freq / N_EXPERIMENTS * 100:.1f}%)")
    print(f"  Only the belief curve called biased:  {only_bayes:5d}  ({only_bayes / N_EXPERIMENTS * 100:.1f}%)\n")

    print(f"Total agreement: {agree / N_EXPERIMENTS * 100:.1f}%")
    print(f"Total disagreement: {disagree / N_EXPERIMENTS * 100:.1f}%")
    print(f"\nTry larger N_TOSSES: the disagreement shrinks.")
    print(f"Try TRUE_BIAS = 0.5 (fair coin): they almost always agree (both stay quiet).")
    print(f"Try TRUE_BIAS = 0.6 with N_TOSSES = 50: borderline territory, more divergence.")


if __name__ == "__main__":
    main()
