"""How would the 10,000 people story actually look if I ran it?

Imagine N_PEOPLE people each given the same coin. Each one tosses it
N_TOSSES times and counts heads. This script simulates that whole
crowd, prints how many of them landed at each result, and draws the
histogram. Change the bias to see what happens when the coin is not
fair, and the histogram slides over.

To play: change the parameters at the top, then run with

    python chapters/02-how-sure/play/many_people_tossing.py
"""

# Parameters you can change
N_PEOPLE = 10000      # how many imagined people are in the crowd
N_TOSSES = 100        # how many times each person tosses the coin
BIAS = 0.5            # the coin's true bias (0.5 = fair, 0.55 = slight heads bias, 0.6 = clearly biased)
SEED = 42             # change this to get a different random crowd

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from expkit.plot.story import PALETTE, apply_story_style


def main():
    apply_story_style()
    rng = np.random.default_rng(SEED)
    # Each person's number of heads in N_TOSSES tosses with probability BIAS.
    head_counts = rng.binomial(N_TOSSES, BIAS, size=N_PEOPLE)

    # Tally up
    counts = np.bincount(head_counts, minlength=N_TOSSES + 1)

    # Print a few interesting bins so the reader can read the numbers
    print(f"\n{N_PEOPLE} imagined people, each tossing a coin (bias={BIAS}) {N_TOSSES} times.\n")
    print("How many people got each number of heads (a few highlights):")
    for k in [N_TOSSES // 4, N_TOSSES * 35 // 100, N_TOSSES * 45 // 100, N_TOSSES // 2,
              N_TOSSES * 55 // 100, N_TOSSES * 60 // 100, N_TOSSES * 65 // 100, N_TOSSES * 3 // 4]:
        print(f"  exactly {k} heads: {counts[k]} people")

    print(f"\nMost common count: {head_counts.mean():.1f} (close to {N_TOSSES * BIAS:.0f}, which is {N_TOSSES} * {BIAS})")
    print(f"Spread of results: {head_counts.std():.2f} (the typical wobble in heads count)\n")

    # Plot
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(np.arange(N_TOSSES + 1), counts, color=PALETTE["focus"], width=0.85)
    ax.set_xlim(0, N_TOSSES)
    ax.set_xlabel(f"number of heads (out of {N_TOSSES} tosses)")
    ax.set_ylabel(f"how many of the {N_PEOPLE} people landed there")
    ax.set_title(f"{N_PEOPLE} people, each tossing a coin (bias={BIAS}) {N_TOSSES} times")
    plt.show()


if __name__ == "__main__":
    main()
