"""Roll a die many times and check if it is fair.

Set the bias for face 6 (the loaded one). The other five faces split
the remainder evenly. The script rolls the die and runs the chi-square
goodness-of-fit test, plus computes the Dirichlet posterior over each
face's probability.

Try LOADED_FACE_PROB = 1/6 (a fair die) and LOADED_FACE_PROB = 1/3
(strongly loaded). At small N the loaded version often slips by
undetected; at large N it gets caught easily.

To play, run:

    python chapters/07-the-die/play/loaded_die_detector.py
"""

LOADED_FACE_PROB = 1/3
N_ROLLS = 600

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    other = (1 - LOADED_FACE_PROB) / 5
    p = [other] * 5 + [LOADED_FACE_PROB]
    rng = np.random.default_rng(72)
    rolls = rng.choice(6, size=N_ROLLS, p=p)
    counts = np.bincount(rolls, minlength=6)
    chi2, pval = stats.chisquare(counts, [N_ROLLS / 6] * 6)[:2]
    print(f"\nDie: face 6 has prob {LOADED_FACE_PROB:.3f}, others {other:.3f} each.")
    print(f"Number of rolls: {N_ROLLS}\n")
    print(f"Counts per face:")
    for i, c in enumerate(counts):
        bar = "#" * int(c / counts.max() * 40)
        print(f"  face {i+1}: {c:4d}  {bar}")
    print(f"\nChi-square test (against fair-die hypothesis):")
    print(f"  p-value: {pval:.4e}")
    if pval < 0.05:
        print(f"  Reject fair: this die looks loaded.")
    else:
        print(f"  Cannot reject fair: data is consistent with a fair die.")
    print(f"\nDirichlet posterior 95% credible intervals for each face's probability:")
    for i, c in enumerate(counts):
        lo = stats.beta.ppf(0.025, 1 + c, 1 + N_ROLLS - c)
        hi = stats.beta.ppf(0.975, 1 + c, 1 + N_ROLLS - c)
        marker = " <-- 1/6" if abs(0.1667 - (lo + hi) / 2) < 0.02 else ""
        print(f"  face {i+1}: [{lo:.4f}, {hi:.4f}]{marker}")


if __name__ == "__main__":
    main()
