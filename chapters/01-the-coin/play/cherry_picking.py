"""Find a misleading window inside a long fair-coin run.

The chapter shows that even a perfectly fair coin, tossed long
enough, will somewhere contain a streak of mostly-heads or
mostly-tails. If I cherry-pick that streak and show it to a friend,
they will conclude the coin is biased. This script does that
cherry-pick for me. Long fair sequence, sliding window, find the
first window matching whatever weird pattern I want.

To play: change the parameters, then run with

    python chapters/01-the-coin/play/cherry_picking.py
"""

# Parameters you can change
N_TOSSES = 2000       # how long the full fair-coin run is
WINDOW = 12           # how big a window to look for
TARGET_HEADS = 10     # what looks-suspicious head count to look for in the window
SEED = 42             # change this to get a different long run

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from expkit.plot.story import PALETTE, apply_story_style, coin_strip, reference_line
from expkit.sim.coin import bernoulli_sequence, running_fraction


def main():
    apply_story_style()
    seq = bernoulli_sequence(N_TOSSES, p=0.5, seed=SEED)

    # Sliding window scan
    start = None
    for i in range(N_TOSSES - WINDOW + 1):
        if int(seq[i:i + WINDOW].sum()) == TARGET_HEADS:
            start = i
            break

    if start is None:
        print(f"\nNo window of size {WINDOW} with exactly {TARGET_HEADS} heads found in {N_TOSSES} tosses.")
        print(f"Try a different seed, or relax TARGET_HEADS.")
        return

    sub = seq[start:start + WINDOW]
    print(f"\nFair coin (bias=0.5), {N_TOSSES} tosses, seed {SEED}.")
    print(f"Total heads: {int(seq.sum())} ({seq.sum() / N_TOSSES * 100:.1f}%, exactly what fair predicts).")
    print(f"\nFound a {WINDOW}-toss window with {TARGET_HEADS} heads starting at toss {start + 1}.")
    print(f"Window contents: {sub.tolist()}  (1 = heads, 0 = tails)")
    print(f"\nIf I showed only this window to someone, they would conclude the coin is biased.")
    print(f"They would be wrong.\n")

    fig, axes = plt.subplots(2, 1, figsize=(11, 3.5))
    coin_strip(axes[0], sub.tolist())
    rf = running_fraction(seq)
    axes[1].plot(np.arange(1, N_TOSSES + 1), rf, color=PALETTE["muted"], linewidth=1.0)
    axes[1].axvspan(start + 1, start + WINDOW, color=PALETTE["focus"], alpha=0.25)
    reference_line(axes[1], 0.5)
    axes[1].set_xlim(1, N_TOSSES)
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("toss number in the long run")
    axes[1].set_ylabel("fraction of heads so far")
    plt.show()


if __name__ == "__main__":
    main()
