"""How often do six simultaneous tests on a fair die wrongly fire?

Each face individually has a 5% chance of being wrongly flagged.
With six faces, the chance that AT LEAST ONE gets flagged is much
higher. The script simulates many fair-die experiments and counts
how often this trap fires, naively and with the Bonferroni correction.

To play, run:

    python chapters/07-the-die/play/multiple_comparisons.py
"""

N_PER_DIE = 600
N_DICE = 1000
THRESHOLD = 0.05

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(72)
    naive = bonf = 0
    for _ in range(N_DICE):
        rolls = rng.choice(6, size=N_PER_DIE)
        counts = np.bincount(rolls, minlength=6)
        any_naive = any_bonf = False
        for c in counts:
            pval = stats.binomtest(int(c), N_PER_DIE, p=1/6, alternative="two-sided").pvalue
            if pval < THRESHOLD: any_naive = True
            if pval < THRESHOLD / 6: any_bonf = True
        if any_naive: naive += 1
        if any_bonf: bonf += 1
    print(f"\n{N_DICE} simulated fair dice, {N_PER_DIE} rolls each.\n")
    print(f"Naive (each face tested at {THRESHOLD * 100:.1f}%):")
    print(f"  At least one face wrongly flagged: {naive / N_DICE * 100:.1f}% of dice")
    print(f"\nBonferroni-corrected (each face tested at {THRESHOLD * 100 / 6:.4f}%):")
    print(f"  At least one face wrongly flagged: {bonf / N_DICE * 100:.1f}% of dice")
    print(f"\nThe correction works at the cost of being more conservative.")


if __name__ == "__main__":
    main()
