"""Demonstrate CUPED variance reduction on a simulated A/B test.

Users with higher pre-experiment revenue tend to have higher
during-experiment revenue. Subtracting the pre-experiment baseline
(CUPED) shrinks the noise, making the same sample size more powerful.

To play, run:

    python chapters/16-metric-quality/play/cuped_demo.py
"""

N_PER_ARM = 500
PRE_MEAN = 10.0
PRE_STD = 4.0
TRUE_EFFECT = 0.50
NOISE_STD = 4.0
SEED = 0

import sys
import numpy as np


def main():
    rng = np.random.default_rng(SEED)
    n = N_PER_ARM
    pre_c = rng.normal(PRE_MEAN, PRE_STD, size=n)
    pre_t = rng.normal(PRE_MEAN, PRE_STD, size=n)
    dur_c = pre_c + rng.normal(0, NOISE_STD, size=n)
    dur_t = pre_t + TRUE_EFFECT + rng.normal(0, NOISE_STD, size=n)

    # CUPED
    theta = np.cov(dur_c, pre_c)[0, 1] / np.var(pre_c)
    cuped_c = dur_c - theta * (pre_c - pre_c.mean())
    cuped_t = dur_t - theta * (pre_t - pre_t.mean())

    se_raw = np.sqrt(dur_c.var(ddof=1)/n + dur_t.var(ddof=1)/n)
    se_cuped = np.sqrt(cuped_c.var(ddof=1)/n + cuped_t.var(ddof=1)/n)
    diff_raw = dur_t.mean() - dur_c.mean()
    diff_cuped = cuped_t.mean() - cuped_c.mean()

    print(f"\nN per arm: {n}, true effect: {TRUE_EFFECT}")
    print(f"Pre-experiment correlation with during: {np.corrcoef(pre_c, dur_c)[0,1]:.3f}")
    print(f"\nRaw comparison:   diff={diff_raw:+.3f}, SE={se_raw:.3f}, 95% CI [{diff_raw-1.96*se_raw:.3f}, {diff_raw+1.96*se_raw:.3f}]")
    print(f"CUPED comparison: diff={diff_cuped:+.3f}, SE={se_cuped:.3f}, 95% CI [{diff_cuped-1.96*se_cuped:.3f}, {diff_cuped+1.96*se_cuped:.3f}]")
    print(f"\nVariance reduction: {(1 - se_cuped/se_raw)*100:.0f}%")
    print(f"Equivalent to multiplying sample size by {(se_raw/se_cuped)**2:.1f}x.")


if __name__ == "__main__":
    main()
