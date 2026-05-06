"""Demonstrate selection bias: observational comparison vs true causal effect.

People with higher propensity to take a treatment also tend to have
better outcomes for other reasons. The naive comparison overstates
the treatment effect.

To play, run:

    python chapters/19-causal-handoff/play/selection_bias.py
"""

TRUE_EFFECT = 0.30           # actual causal effect of treatment
PROPENSITY_STRENGTH = 1.0    # how much propensity determines treatment (0 = random, higher = more biased)
N = 2000
SEED = 0

import sys
import numpy as np


def main():
    rng = np.random.default_rng(SEED)
    propensity = rng.normal(0, 1, size=N)
    prob_treat = 1 / (1 + np.exp(-PROPENSITY_STRENGTH * propensity))
    treatment = rng.random(N) < prob_treat
    outcome = propensity + TRUE_EFFECT * treatment + rng.normal(0, 0.5, size=N)

    naive_diff = outcome[treatment].mean() - outcome[~treatment].mean()
    # With propensity adjustment (simple: control for propensity decile)
    deciles = np.percentile(propensity, np.arange(0, 110, 10))
    adjusted_diffs = []
    for i in range(10):
        lo, hi = deciles[i], deciles[i+1]
        in_decile = (propensity >= lo) & (propensity < hi)
        t_mask = in_decile & treatment
        c_mask = in_decile & ~treatment
        if t_mask.sum() > 5 and c_mask.sum() > 5:
            adjusted_diffs.append(outcome[t_mask].mean() - outcome[c_mask].mean())
    adjusted = float(np.mean(adjusted_diffs)) if adjusted_diffs else float("nan")

    print(f"\nTrue causal effect: {TRUE_EFFECT:+.3f}")
    print(f"Propensity strength: {PROPENSITY_STRENGTH} (0=random, 2=strongly biased)")
    print(f"\nNaive comparison:        {naive_diff:+.3f}  {'(BIASED)' if abs(naive_diff - TRUE_EFFECT) > 0.05 else '(close to truth)'}")
    print(f"Propensity-adjusted:     {adjusted:+.3f}  (closer to truth)")
    print(f"\nThe bias is {(naive_diff - TRUE_EFFECT)*100:+.0f}% of the true effect.")
    print(f"Try PROPENSITY_STRENGTH = 0 (randomized) to see naive ≈ truth.")
    print(f"Try PROPENSITY_STRENGTH = 2 (highly confounded) to see large bias.")


if __name__ == "__main__":
    main()
