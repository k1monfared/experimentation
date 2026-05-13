"""A positive aggregate can hide a cohort that regressed. Which cohorts get harmed?

COHORT_WEIGHTS are the share of users in each cohort. COHORT_LIFTS are
their click-rate lifts in percent. The aggregate is the weighted sum.
The trap: the aggregate is positive, and the most-valuable cohort (the
first one, by convention) has a negative lift. Try boosting the long
tail lift and the aggregate looks even better while the most-engaged
cohort stays hurt.

To play, run:

    python chapters/10-industry-experimentation/play/aggregate_cohort_simulator.py
"""

COHORT_NAMES = ["most engaged 10%", "moderate 30%", "long tail 60%"]
COHORT_WEIGHTS = [0.10, 0.30, 0.60]
COHORT_LIFTS = [-2.0, 3.0, 6.0]
VALUE_PER_COHORT = [10.0, 3.0, 1.0]  # revenue weight, not population weight

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))


def main():
    assert len(COHORT_NAMES) == len(COHORT_WEIGHTS) == len(COHORT_LIFTS) == len(VALUE_PER_COHORT)
    assert abs(sum(COHORT_WEIGHTS) - 1.0) < 1e-6, "COHORT_WEIGHTS must sum to 1"

    pop_aggregate = sum(w * l for w, l in zip(COHORT_WEIGHTS, COHORT_LIFTS))
    value_weights = [w * v for w, v in zip(COHORT_WEIGHTS, VALUE_PER_COHORT)]
    total_value = sum(value_weights)
    value_aggregate = sum(vw * l for vw, l in zip(value_weights, COHORT_LIFTS)) / total_value

    print()
    print(f"{'cohort':<22} {'weight':>8} {'lift (%)':>10} {'value':>8}")
    for n, w, l, v in zip(COHORT_NAMES, COHORT_WEIGHTS, COHORT_LIFTS, VALUE_PER_COHORT):
        print(f"{n:<22} {w:>8.2f} {l:>+10.2f} {v:>8.1f}")

    print(f"\nPopulation-weighted aggregate lift:  {pop_aggregate:+.2f}%")
    print(f"Value-weighted aggregate lift:       {value_aggregate:+.2f}%")

    losers = [n for n, l in zip(COHORT_NAMES, COHORT_LIFTS) if l < 0]
    if losers:
        print(f"\nCohorts that regressed: {', '.join(losers)}.")
    else:
        print("\nNo cohort regressed under these settings.")

    if pop_aggregate > 0 and value_aggregate < 0:
        print("The headline (population-weighted) is positive, but the value-weighted view is negative.")
        print("Shipping on the headline harms the cohort that drives the business.")
    elif pop_aggregate > 0 and any(l < 0 for l in COHORT_LIFTS):
        print("Aggregate looks good. At least one cohort went backward.")
        print("Whether you ship depends on how much that cohort matters to the business.")
    elif pop_aggregate > 0:
        print("Aggregate is positive and no cohort regressed under these settings.")
    else:
        print("Aggregate is not positive. The headline story is already telling you the truth.")


if __name__ == "__main__":
    main()
