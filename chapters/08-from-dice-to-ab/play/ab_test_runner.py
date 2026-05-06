"""Simulate an A/B test on a binary outcome and apply both decision rules.

Pick a control rate, a treatment rate, and a sample size. The script
simulates one experiment, runs both the frequentist test and the
Bayesian belief curve, and reports both verdicts.

Try CONTROL_RATE = 0.05, TREATMENT_RATE = 0.06 with SAMPLE_PER_ARM = 1000:
the effect is real but the data is too thin to catch it. Then try
SAMPLE_PER_ARM = 10000: the data is enough.

To play, run:

    python chapters/08-from-dice-to-ab/play/ab_test_runner.py
"""

CONTROL_RATE = 0.05
TREATMENT_RATE = 0.06
SAMPLE_PER_ARM = 1000
MMU = 0.005

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)
    n = SAMPLE_PER_ARM
    s_c = rng.binomial(n, CONTROL_RATE)
    s_t = rng.binomial(n, TREATMENT_RATE)
    obs_c, obs_t = s_c / n, s_t / n
    diff = obs_t - obs_c

    # Frequentist
    p_pool = (s_c + s_t) / (2 * n)
    se = np.sqrt(p_pool * (1 - p_pool) * 2 / n)
    z = diff / se if se > 0 else 0.0
    p = 2 * stats.norm.sf(abs(z))

    # Bayesian
    samples_c = rng.beta(1 + s_c, 1 + n - s_c, size=20000)
    samples_t = rng.beta(1 + s_t, 1 + n - s_t, size=20000)
    diff_samples = samples_t - samples_c
    prob_better = float((diff_samples > 0).mean())
    prob_above_mmu = float((diff_samples > MMU).mean())

    print(f"\nControl: {s_c}/{n} = {obs_c:.4f}")
    print(f"Treatment: {s_t}/{n} = {obs_t:.4f}")
    print(f"Observed difference: {diff:+.4f}")
    print(f"True difference (used to simulate): {TREATMENT_RATE - CONTROL_RATE:+.4f}\n")
    print(f"Frequentist (two-proportion z-test):")
    print(f"  z = {z:.3f}, p = {p:.4f}")
    print(f"  Verdict: {'REJECT (effect found)' if p < 0.05 else 'do not reject (cannot rule out no effect)'}\n")
    print(f"Bayesian (Beta(1,1) priors on each arm):")
    print(f"  P(treatment > control)         = {prob_better:.4f}")
    print(f"  P(treatment > control + {MMU * 100:.1f}pp) = {prob_above_mmu:.4f}")
    print(f"  Verdict (P>MMU > 0.95): {'SHIP' if prob_above_mmu > 0.95 else 'do not ship'}")


if __name__ == "__main__":
    main()
