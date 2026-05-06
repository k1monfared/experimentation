"""What should I believe about the coin, given what I just saw?

The chapter draws the belief curve for "60 heads in 100 tosses". This
script lets me change either number and see how my belief about the
coin's underlying bias shifts. Try OBSERVED_HEADS = 6 with
N_TOSSES = 10, then OBSERVED_HEADS = 60 with N_TOSSES = 100, then
600 with 1000. Same fraction of heads, very different shapes.

To play: change the parameters, then run with

    python chapters/02-how-sure/play/belief_curve.py
"""

# Parameters you can change
OBSERVED_HEADS = 60   # how many heads I actually saw
N_TOSSES = 100        # how many times I tossed

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
    if OBSERVED_HEADS < 0 or OBSERVED_HEADS > N_TOSSES:
        raise ValueError("OBSERVED_HEADS must be between 0 and N_TOSSES")

    # Belief curve given a flat prior (every bias equally plausible before seeing data).
    # After seeing k heads in n tosses, the belief is a Beta(1+k, 1+n-k) shape.
    a, b = 1 + OBSERVED_HEADS, 1 + (N_TOSSES - OBSERVED_HEADS)
    ps = np.linspace(0.001, 0.999, 1000)
    belief = stats.beta.pdf(ps, a, b)

    # The 95% range
    lo = stats.beta.ppf(0.025, a, b)
    hi = stats.beta.ppf(0.975, a, b)
    centre = a / (a + b)

    print(f"\nObservation: {OBSERVED_HEADS} heads in {N_TOSSES} tosses (fraction {OBSERVED_HEADS / N_TOSSES:.3f}).")
    print(f"Belief curve centre: {centre:.4f}")
    print(f"95% range of plausible bias: [{lo:.4f}, {hi:.4f}]")
    if lo > 0.5:
        print(f"The 95% range is entirely above 0.5. The data is convinced the coin leans heads.")
    elif hi < 0.5:
        print(f"The 95% range is entirely below 0.5. The data is convinced the coin leans tails.")
    else:
        print(f"The 95% range still includes 0.5. The data has not ruled out fair.\n")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(ps, 0, belief, color=PALETTE["focus"], alpha=0.35)
    ax.plot(ps, belief, color=PALETTE["focus"], linewidth=2)
    ax.axvline(0.5, color=PALETTE["muted"], linestyle="--", linewidth=1)
    ax.axvline(lo, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
    ax.axvline(hi, color=PALETTE["ink"], linestyle=":", linewidth=0.8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("possible fairness of the coin")
    ax.set_ylabel("how strongly I now believe each value")
    ax.set_title(f"Belief after seeing {OBSERVED_HEADS} heads in {N_TOSSES} tosses")
    plt.show()


if __name__ == "__main__":
    main()
