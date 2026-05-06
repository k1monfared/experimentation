"""Different runs of the same coin look surprisingly different.

The chapter shows six runs of 100 tosses, each starting fresh, and
how each one wobbles toward fifty in its own way. This script lets
me run as many runs as I want, with whatever bias and length, all
on the same axes so I can feel the wobble.

To play: change the parameters, then run with

    python chapters/01-the-coin/play/many_seeds.py
"""

# Parameters you can change
N_TOSSES = 100        # how many tosses per run
N_RUNS = 6            # how many separate runs to do
BIAS = 0.5            # the coin's true bias
BASE_SEED = 11        # the first seed; subsequent runs use BASE_SEED, BASE_SEED+1, etc.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from expkit.plot.story import PALETTE, SEQUENCE, apply_story_style
from expkit.sim.coin import bernoulli_sequence, running_fraction


def main():
    apply_story_style()
    fig, ax = plt.subplots(figsize=(10, 4.5))

    print(f"\n{N_RUNS} separate runs of {N_TOSSES} tosses each (bias={BIAS}).\n")
    print("Final fractions of heads:")
    for i in range(N_RUNS):
        seed = BASE_SEED + i * 12
        seq = bernoulli_sequence(N_TOSSES, p=BIAS, seed=seed)
        rf = running_fraction(seq)
        color = SEQUENCE[i % len(SEQUENCE)]
        ax.plot(np.arange(1, N_TOSSES + 1), rf, color=color, linewidth=1.3, alpha=0.9)
        print(f"  run {i + 1} (seed {seed}): {int(seq.sum())} heads, final fraction {rf[-1]:.3f}")

    ax.axhline(BIAS, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.set_xlim(1, N_TOSSES)
    ax.set_ylim(0, 1)
    ax.set_xlabel("toss number")
    ax.set_ylabel("fraction of heads so far")
    ax.set_title(f"{N_RUNS} separate runs of {N_TOSSES} tosses, all on the same chart")
    plt.show()


if __name__ == "__main__":
    main()
