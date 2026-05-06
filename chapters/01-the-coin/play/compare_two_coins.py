"""Two coins with different biases, side by side over many tosses.

The chapter compares a fair coin against one that is 0.55 heavy on
heads, over 10000 tosses. This script lets me set both biases and
watch them drift apart at any sample size. Try BIAS_A = 0.5 and
BIAS_B = 0.501. They are practically indistinguishable even at
10000 tosses, which is the point.

To play: change the parameters, then run with

    python chapters/01-the-coin/play/compare_two_coins.py
"""

# Parameters you can change
N_TOSSES = 10000      # how many tosses for each coin
BIAS_A = 0.50         # the first coin's bias
BIAS_B = 0.55         # the second coin's bias
SEED_A = 7            # seed for coin A
SEED_B = 8            # seed for coin B

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from expkit.plot.story import PALETTE, apply_story_style, reference_line
from expkit.sim.coin import bernoulli_sequence, running_fraction


def main():
    apply_story_style()
    seq_a = bernoulli_sequence(N_TOSSES, p=BIAS_A, seed=SEED_A)
    seq_b = bernoulli_sequence(N_TOSSES, p=BIAS_B, seed=SEED_B)
    rf_a = running_fraction(seq_a)
    rf_b = running_fraction(seq_b)

    print(f"\nCoin A (bias={BIAS_A}): {int(seq_a.sum())} heads in {N_TOSSES} tosses, final fraction {rf_a[-1]:.4f}")
    print(f"Coin B (bias={BIAS_B}): {int(seq_b.sum())} heads in {N_TOSSES} tosses, final fraction {rf_b[-1]:.4f}")
    print(f"Difference at end: {rf_b[-1] - rf_a[-1]:+.4f} (true difference: {BIAS_B - BIAS_A:+.4f})")
    print(f"\nWatch when they separate. Below 100 tosses they are jumbled.")
    print(f"Above a few thousand tosses they are clearly different (if the bias gap is at least a couple of percent).\n")

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    cuts = [(min(100, N_TOSSES), "after 100"),
            (min(1000, N_TOSSES), "after 1,000"),
            (N_TOSSES, f"after {N_TOSSES:,}")]
    for ax, (n, label) in zip(axes, cuts):
        ax.plot(np.arange(1, n + 1), rf_a[:n], color=PALETTE["contrast"], linewidth=1.4, label=f"coin A (bias {BIAS_A})")
        ax.plot(np.arange(1, n + 1), rf_b[:n], color=PALETTE["focus"], linewidth=1.4, label=f"coin B (bias {BIAS_B})")
        reference_line(ax, BIAS_A)
        reference_line(ax, BIAS_B)
        ax.set_xlim(1, n)
        ax.set_ylim(0, 1)
        ax.set_title(label)
        ax.set_xlabel("toss number")
        if ax is axes[0]:
            ax.set_ylabel("fraction of heads so far")
            ax.legend(loc="lower right")
    plt.show()


if __name__ == "__main__":
    main()
