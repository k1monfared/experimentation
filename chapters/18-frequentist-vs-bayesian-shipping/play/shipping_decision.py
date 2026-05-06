"""When do two decision frameworks actually disagree?

Simulate an A/B test and apply both a frequentist rule (p<0.05 and
positive) and a Bayesian rule (P(lift > MMU) > 0.95). Report what each
rule says and whether they agree.

To play, run:

    python chapters/18-frequentist-vs-bayesian-shipping/play/shipping_decision.py
"""

TRUE_EFFECT = 0.008   # true lift (set to 0 to see false-ship rates)
CONTROL_RATE = 0.05
N_PER_ARM = 2000
MMU = 0.005           # minimum meaningful uplift for the Bayesian rule
SEED = 0

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy import stats


def main():
    rng = np.random.default_rng(SEED)
    n = N_PER_ARM
    s_c = rng.binomial(n, CONTROL_RATE)
    s_t = rng.binomial(n, max(0, min(1, CONTROL_RATE + TRUE_EFFECT)))
    diff = s_t/n - s_c/n
    p_pool = (s_c + s_t) / (2*n)
    se = np.sqrt(p_pool * (1 - p_pool) * 2 / n) if p_pool > 0 else 1.0
    pval = float(2 * stats.norm.sf(abs(diff/se))) if se > 0 else 1.0
    freq_says = pval < 0.05 and diff > 0

    samples_c = rng.beta(1+s_c, 1+n-s_c, size=20000)
    samples_t = rng.beta(1+s_t, 1+n-s_t, size=20000)
    prob_above_mmu = float((samples_t - samples_c > MMU).mean())
    bayes_says = prob_above_mmu > 0.95

    print(f"\nTrue effect: {TRUE_EFFECT*100:+.2f}pp on {CONTROL_RATE*100:.0f}% baseline")
    print(f"Observed: control={s_c}/{n} ({s_c/n:.4f}), treatment={s_t}/{n} ({s_t/n:.4f})")
    print(f"Observed diff: {diff*100:+.3f}pp\n")
    print(f"Frequentist (p<0.05 AND positive): p={pval:.4f} → {'SHIP' if freq_says else 'hold'}")
    print(f"Bayesian (P(lift>{MMU*100:.1f}pp)>0.95): P={prob_above_mmu:.3f} → {'SHIP' if bayes_says else 'hold'}")
    if freq_says == bayes_says:
        print(f"\nBoth rules agree: {'ship' if freq_says else 'hold'}.")
    else:
        print(f"\nRules DISAGREE. This is the borderline territory the chapter is about.")


if __name__ == "__main__":
    main()
