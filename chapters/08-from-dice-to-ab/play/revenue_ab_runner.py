"""Simulate a continuous-outcome A/B test on revenue per user.

Pick two arm means, a noise level, and a sample size. The script
simulates one experiment, runs Welch's t-test, and then bootstraps
the mean difference to get a non-parametric 95 percent CI.

Try the default values below. Then push MU_TREATMENT closer to MU_CONTROL,
or shrink SAMPLE_PER_ARM, and watch the t-test and the bootstrap CI
lose their grip on the effect together. Bump SIGMA up and the same
effect stops being detectable: more per-user noise means more data needed.

To play, run:

    python chapters/08-from-dice-to-ab/play/revenue_ab_runner.py
"""

MU_CONTROL = 10.0
MU_TREATMENT = 10.5
SIGMA = 4.0
SAMPLE_PER_ARM = 2000
N_BOOT = 4000

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(0)
    n = SAMPLE_PER_ARM
    rev_c = rng.normal(MU_CONTROL, SIGMA, size=n)
    rev_t = rng.normal(MU_TREATMENT, SIGMA, size=n)
    diff = rev_t.mean() - rev_c.mean()

    # Welch's t-test (no equal-variance assumption)
    t, p = stats.ttest_ind(rev_t, rev_c, equal_var=False)

    # Percentile-method bootstrap of the mean difference
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        bc = rng.choice(rev_c, size=n, replace=True)
        bt = rng.choice(rev_t, size=n, replace=True)
        boot[i] = bt.mean() - bc.mean()
    lo, hi = np.quantile(boot, [0.025, 0.975])

    print(f"\nControl mean: {rev_c.mean():.3f}")
    print(f"Treatment mean: {rev_t.mean():.3f}")
    print(f"Observed difference: {diff:+.3f}")
    print(f"True difference (used to simulate): {MU_TREATMENT - MU_CONTROL:+.3f}\n")
    print(f"Welch t-test:")
    print(f"  t = {t:.3f}, p = {p:.4f}")
    print(f"  Verdict: {'REJECT (effect found)' if p < 0.05 else 'do not reject'}\n")
    print(f"Bootstrap ({N_BOOT} resamples), 95% CI for mean difference:")
    print(f"  [{lo:+.3f}, {hi:+.3f}]")
    print(f"  Verdict (CI excludes 0): {'ship' if lo > 0 else 'do not ship'}")


if __name__ == "__main__":
    main()
