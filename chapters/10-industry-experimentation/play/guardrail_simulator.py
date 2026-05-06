"""How many guardrail metrics is too many before false alarms dominate?

A typical product team monitors many metrics for regression after a
launch. With many metrics and no correction, at least one will fire
by chance. Try N_METRICS = 20 and see how often a fair launch (no
real effect) trips at least one alarm.

To play, run:

    python chapters/10-industry-experimentation/play/guardrail_simulator.py
"""

N_METRICS = 20
N_TRIALS = 5000
THRESHOLD = 0.05

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np


def main():
    rng = np.random.default_rng(0)
    naive = bonf = 0
    for _ in range(N_TRIALS):
        ps = rng.uniform(0, 1, size=N_METRICS)
        if np.any(ps < THRESHOLD): naive += 1
        if np.any(ps < THRESHOLD / N_METRICS): bonf += 1
    print(f"\n{N_METRICS} metrics monitored, {N_TRIALS} simulated launches under no real effect.\n")
    print(f"Naive (each at {THRESHOLD * 100:.0f}%):")
    print(f"  At least one fires: {naive / N_TRIALS * 100:.1f}% of launches")
    print(f"\nBonferroni (each at {THRESHOLD * 100 / N_METRICS:.4f}%):")
    print(f"  At least one fires: {bonf / N_TRIALS * 100:.1f}% of launches")
    print(f"\nThe naive procedure is broken when monitoring many metrics.")
    print(f"At 20 metrics, false alarms dominate: more often than not, something fires by chance.")


if __name__ == "__main__":
    main()
