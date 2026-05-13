"""Simulate an A/B test with two user segments and compare pooled vs per-segment views.

Two segments with different baseline rates and different sizes. The
treatment lifts both segments by the same absolute amount (LIFT). The
script runs a two-proportion z-test inside each segment and then on
the pooled population, so the per-segment answer and the pooled
answer can be read side by side.

Defaults: 200 power users at a 30 percent baseline, 1800 casuals at a
5 percent baseline, same 2 percentage point lift in each. The pooled
test sees mostly the casual effect. The power-user test has no power
at N = 200 per arm. Neither is wrong, they answer different questions.

Push LIFT up and both tests eventually agree. Shrink POWER_USER_SIZE
further and the per-segment power-user test becomes pure noise. Move
the baselines apart and the pooling bias gets easier to see.

To play, run:

    python chapters/08-from-dice-to-ab/play/stratified_runner.py
"""

POWER_USER_SIZE = 200
POWER_USER_BASELINE = 0.30
CASUAL_SIZE = 1800
CASUAL_BASELINE = 0.05
LIFT = 0.02  # absolute lift in each segment

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def two_prop_z(s_t, n_t, s_c, n_c):
    p_pool = (s_t + s_c) / (n_t + n_c)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    diff = s_t / n_t - s_c / n_c
    z = diff / se if se > 0 else 0.0
    p = 2 * stats.norm.sf(abs(z))
    return diff, z, p


def run_segment(rng, name, n_per_arm, p_control, p_treatment):
    s_c = rng.binomial(n_per_arm, p_control)
    s_t = rng.binomial(n_per_arm, p_treatment)
    diff, z, p = two_prop_z(s_t, n_per_arm, s_c, n_per_arm)
    print(f"  {name}: N = {n_per_arm} per arm")
    print(f"    control: {s_c}/{n_per_arm} = {s_c/n_per_arm:.4f}")
    print(f"    treatment: {s_t}/{n_per_arm} = {s_t/n_per_arm:.4f}")
    print(f"    diff = {diff:+.4f}, z = {z:.3f}, p = {p:.4f}")
    return s_c, s_t


def main():
    rng = np.random.default_rng(0)

    print("\nPer-segment view (each segment asks 'is the effect nonzero here?'):\n")
    s_c_power, s_t_power = run_segment(
        rng, "power-users", POWER_USER_SIZE,
        POWER_USER_BASELINE, POWER_USER_BASELINE + LIFT,
    )
    s_c_casual, s_t_casual = run_segment(
        rng, "casuals", CASUAL_SIZE,
        CASUAL_BASELINE, CASUAL_BASELINE + LIFT,
    )

    # Pooled view: combine counts across segments
    total_n = POWER_USER_SIZE + CASUAL_SIZE
    s_c_total = s_c_power + s_c_casual
    s_t_total = s_t_power + s_t_casual
    diff, z, p = two_prop_z(s_t_total, total_n, s_c_total, total_n)

    print("\nPooled view (asks 'is the average effect nonzero across everyone?'):")
    print(f"  N = {total_n} per arm")
    print(f"  control: {s_c_total}/{total_n} = {s_c_total/total_n:.4f}")
    print(f"  treatment: {s_t_total}/{total_n} = {s_t_total/total_n:.4f}")
    print(f"  diff = {diff:+.4f}, z = {z:.3f}, p = {p:.4f}\n")
    print("The pooled number is dominated by whichever segment has more users.")
    print("Same absolute lift in both groups, very different detectability.")


if __name__ == "__main__":
    main()
