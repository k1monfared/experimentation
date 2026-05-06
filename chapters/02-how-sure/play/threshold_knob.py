"""How does the surprise zone change when I move the threshold?

The chapter picks five percent as the threshold for "surprising". This
script shows where the cutoff lands at any threshold I want, so I can
feel the trade-off between false alarms (too loose) and missed real
biases (too tight).

To play: change the threshold and the sample size, then run with

    python chapters/02-how-sure/play/threshold_knob.py
"""

# Parameters you can change
N_TOSSES = 100        # how many tosses in the experiment
THRESHOLD = 0.05      # the surprise threshold (0.05 = 5%, 0.01 = 1%, 0.10 = 10%)

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from expkit.plot.story import PALETTE, apply_story_style


def main():
    apply_story_style()
    ks = np.arange(0, N_TOSSES + 1)
    pmf = stats.binom.pmf(ks, N_TOSSES, 0.5)

    # Walk inward from the tails in symmetric pairs until the threshold budget is used up.
    cum = 0.0
    surprise_zone = set()
    for k in range(N_TOSSES // 2 + 1):
        j = N_TOSSES - k
        add = pmf[k] + (pmf[j] if k != j else 0.0)
        if cum + add > THRESHOLD:
            break
        surprise_zone.add(int(k))
        if j != k:
            surprise_zone.add(int(j))
        cum += add

    surprise_low = max((k for k in surprise_zone if k < N_TOSSES // 2), default=None)
    surprise_high = min((k for k in surprise_zone if k > N_TOSSES // 2), default=None)

    print(f"\nThreshold: {THRESHOLD * 100:.1f}% surprise budget on a fair {N_TOSSES}-toss experiment.")
    print(f"Surprise zone: {surprise_low} or fewer, OR {surprise_high} or more (out of {N_TOSSES} tosses).")
    print(f"Used budget: {cum * 100:.2f}% (just under your {THRESHOLD * 100:.1f}% target).")
    print(f"\nSo if I see {surprise_high} or more heads, I will call the coin biased.")
    print(f"If I see anything between {surprise_low + 1 if surprise_low is not None else 0} and {surprise_high - 1 if surprise_high is not None else N_TOSSES} heads, I will not.\n")

    # Plot
    colors = [PALETTE["contrast"] if int(k) in surprise_zone else PALETTE["focus"] for k in ks]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(ks, pmf * 100, color=colors, width=0.85)
    ax.set_xlim(0, N_TOSSES)
    ax.set_xlabel(f"number of heads (out of {N_TOSSES})")
    ax.set_ylabel("percent of fair-coin runs landing here")
    ax.set_title(f"Surprise zone (blue) at threshold {THRESHOLD * 100:.1f}%")
    plt.show()


if __name__ == "__main__":
    main()
