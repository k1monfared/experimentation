"""Build Simpson's paradox interactively.

Pick segment sizes, baselines, treatment lifts, and assignment bias.
Watch the aggregate flip while every segment is positive.

To play, run:

    python chapters/12-simpsons-paradox/play/paradox_builder.py
"""

# Segment A: small, high baseline. Segment B: large, low baseline.
FRAC_A = 0.20        # fraction of population in segment A
BASE_A = 0.80        # baseline outcome rate in segment A
BASE_B = 0.20        # baseline outcome rate in segment B
LIFT = 0.05          # treatment lift in BOTH segments (true, identical)
TREAT_SHARE_A = 0.20  # fraction of segment A assigned to treatment (imbalanced)
TREAT_SHARE_B = 0.80  # fraction of segment B assigned to treatment (imbalanced)
N = 10000

import sys
import numpy as np


def main():
    rng = np.random.default_rng(0)
    frac_b = 1 - FRAC_A
    n_a, n_b = int(N * FRAC_A), int(N * frac_b)

    # Segment A: few treated
    t_a = int(n_a * TREAT_SHARE_A)
    c_a = n_a - t_a
    t_a_out = rng.binomial(t_a, BASE_A + LIFT)
    c_a_out = rng.binomial(c_a, BASE_A)

    # Segment B: mostly treated
    t_b = int(n_b * TREAT_SHARE_B)
    c_b = n_b - t_b
    t_b_out = rng.binomial(t_b, BASE_B + LIFT)
    c_b_out = rng.binomial(c_b, BASE_B)

    # Per-segment effects
    per_a = t_a_out/t_a - c_a_out/c_a
    per_b = t_b_out/t_b - c_b_out/c_b

    # Aggregate
    total_treat = t_a + t_b
    total_ctrl = c_a + c_b
    agg_treat = (t_a_out + t_b_out) / total_treat
    agg_ctrl = (c_a_out + c_b_out) / total_ctrl
    agg_diff = agg_treat - agg_ctrl

    print(f"\nSegment A: n={n_a}, baseline={BASE_A:.2f}, treat_share={TREAT_SHARE_A:.0%}")
    print(f"  per-segment lift: {per_a:+.3f} (true: {LIFT:+.3f})")
    print(f"\nSegment B: n={n_b}, baseline={BASE_B:.2f}, treat_share={TREAT_SHARE_B:.0%}")
    print(f"  per-segment lift: {per_b:+.3f} (true: {LIFT:+.3f})")
    print(f"\nAggregate effect: {agg_diff:+.3f} (should be {LIFT:+.3f} but assignment is imbalanced)")
    if agg_diff < 0 and LIFT > 0:
        print(f"\n*** Simpson's paradox! Both segments positive, aggregate is NEGATIVE. ***")
    elif agg_diff < LIFT * 0.5:
        print(f"\nNear-paradox: aggregate is far below the true within-segment effect.")
    print(f"\nTry TREAT_SHARE_A = 0.50 and TREAT_SHARE_B = 0.50 to see balanced assignment restore the truth.")


if __name__ == "__main__":
    main()
