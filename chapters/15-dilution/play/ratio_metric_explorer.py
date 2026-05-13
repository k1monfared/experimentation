"""How does the delta method compare to a naive ratio difference?

Outcome is revenue per session. Both numerator (revenue) and
denominator (sessions) are random per user. The naive estimator
(sum of revenue divided by sum of sessions) gives a point but no
honest standard error. The delta method linearizes the ratio
around the means to produce a proper SE.

Toggle PER_SESSION_LIFT and N to see when delta and naive point
estimates match (they should), and when the delta SE would call
the result significant.

To play, run:

    python chapters/15-dilution/play/ratio_metric_explorer.py
"""

PER_SESSION_LIFT = 0.05   # true revenue lift per session in the treatment arm
N = 3000                  # users per arm
SESSIONS_LAMBDA = 8       # mean sessions per user (Poisson)
NOISE_SD = 4.0            # per-user revenue noise
SEED = 0

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from expkit.metrics.delta import delta_two_arm


def main():
    rng = np.random.default_rng(SEED)
    sess_c = rng.poisson(SESSIONS_LAMBDA, N)
    rev_c = rng.normal(2.0 * sess_c, NOISE_SD)
    sess_t = rng.poisson(SESSIONS_LAMBDA, N)
    rev_t = rng.normal((2.0 + PER_SESSION_LIFT) * sess_t, NOISE_SD)

    diff, se, z = delta_two_arm(rev_t, sess_t, rev_c, sess_c)
    naive_diff = (rev_t.sum() / sess_t.sum()) - (rev_c.sum() / sess_c.sum())

    print(f"\nTrue per-session lift: {PER_SESSION_LIFT:+.4f}")
    print(f"Users per arm: {N}, mean sessions per user: {SESSIONS_LAMBDA}")
    print(f"\nNaive ratio diff:    {naive_diff:+.4f}  (no SE, no z)")
    print(f"Delta method: diff = {diff:+.4f}, se = {se:.4f}, z = {z:.2f}")
    verdict = "significant at 0.05" if abs(z) > 1.96 else "not significant at 0.05"
    print(f"Delta z-test: {verdict}")
    print("\nTry PER_SESSION_LIFT = 0.0 to see an A/A run.")
    print("Try N = 300 to see SE widen and z shrink with less data.")


if __name__ == "__main__":
    main()
