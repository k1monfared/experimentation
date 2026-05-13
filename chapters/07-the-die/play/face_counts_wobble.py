"""Roll a fair die N times and watch the face counts wobble.

Change N and SEED below. Small N shows big per-face swings; large N
shows counts settling into a tight band around N/6.

To play, run:

    python chapters/07-the-die/play/face_counts_wobble.py
"""

N = 60
SEED = 72

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np


def main():
    rng = np.random.default_rng(SEED)
    rolls = rng.choice(6, size=N)
    counts = np.bincount(rolls, minlength=6)
    expected = N / 6
    print(f"\nFair die, {N} rolls (seed {SEED}). Each face expected: {expected:.1f}.\n")
    peak = max(counts.max(), 1)
    for i, c in enumerate(counts):
        bar = "#" * int(c / peak * 40)
        delta = c - expected
        sign = "+" if delta >= 0 else ""
        print(f"  face {i+1}: {c:4d}  ({sign}{delta:+.1f})  {bar}")
    fraction_off = np.abs(counts - expected).max() / expected
    print(f"\nLargest single-face miss: {fraction_off * 100:.1f}% of expected.")
    print("Try N = 60, then 600, then 6000. The wobble shrinks like 1/sqrt(N).")


if __name__ == "__main__":
    main()
