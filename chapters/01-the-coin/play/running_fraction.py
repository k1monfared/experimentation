"""Toss a coin a lot of times and watch the running fraction settle.

The chapter shows the running fraction settling toward 0.5 over four
panels: 10, 100, 1000, 10000 tosses. This script lets me toss
N_TOSSES times with any bias I choose, then plots the whole running
fraction so I can see for myself how slowly it lands.

To play: change the parameters, then run with

    python chapters/01-the-coin/play/running_fraction.py
"""

# Parameters you can change
N_TOSSES = 10000      # how many tosses to do
BIAS = 0.5            # the coin's true bias (0.5 = fair, 0.55 = slightly heavy on heads)
SEED = 500            # change this to get a different random sequence

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from expkit.plot.story import PALETTE, apply_story_style
from expkit.sim.coin import bernoulli_sequence, running_fraction


def main():
    apply_story_style()
    seq = bernoulli_sequence(N_TOSSES, p=BIAS, seed=SEED)
    rf = running_fraction(seq)

    print(f"\nTossed a coin (bias={BIAS}) {N_TOSSES} times with seed {SEED}.")
    print(f"Total heads: {int(seq.sum())} out of {N_TOSSES} ({seq.sum() / N_TOSSES * 100:.2f}%)")
    print(f"Running fraction at a few checkpoints:")
    for n in [10, 100, 1000, 10000]:
        if n <= N_TOSSES:
            print(f"  after {n:6d} tosses: {rf[n - 1]:.4f}")
    print()

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(np.arange(1, N_TOSSES + 1), rf, color=PALETTE["focus"], linewidth=1.4)
    ax.axhline(BIAS, color=PALETTE["muted"], linestyle="--", linewidth=1, label=f"true bias = {BIAS}")
    ax.set_xlim(1, N_TOSSES)
    ax.set_ylim(0, 1)
    ax.set_xlabel("toss number")
    ax.set_ylabel("fraction of heads so far")
    ax.set_title(f"running fraction over {N_TOSSES} tosses")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
