"""Simulate a feature with a novelty decay and watch the metrics diverge.

Choose a true long-run effect (can be zero, positive, or negative) and
an initial novelty boost on top of it. The script shows what each
metric reports at the 7-day test window vs the 30-day steady state.

To play, run:

    python chapters/14-novelty/play/novelty_curve.py
"""

INITIAL_NOVELTY_LIFT = 0.10   # boost on day 1 (decays with half-life)
HALF_LIFE_DAYS = 7.0          # how fast the novelty wears off
TRUE_LONG_RUN_LIFT = 0.02     # what the feature actually delivers at steady state
TEST_WINDOW_DAYS = 7          # typical A/B test duration

import sys
import numpy as np


def main():
    days = np.arange(0, 61)
    novelty = INITIAL_NOVELTY_LIFT * np.exp(-days / HALF_LIFE_DAYS)
    total_lift = novelty + TRUE_LONG_RUN_LIFT

    at_window = total_lift[TEST_WINDOW_DAYS]
    at_steady = total_lift[60]

    print(f"\nFeature: initial novelty boost +{INITIAL_NOVELTY_LIFT*100:.1f}pp, half-life {HALF_LIFE_DAYS} days")
    print(f"True long-run effect: {TRUE_LONG_RUN_LIFT*100:+.1f}pp")
    print(f"\nWhat the {TEST_WINDOW_DAYS}-day test sees: {at_window*100:+.2f}pp lift")
    print(f"What the 60-day picture shows: {at_steady*100:+.2f}pp lift")
    if at_window > TRUE_LONG_RUN_LIFT * 1.5:
        print(f"\nRisk: test window overstates the real effect by {(at_window - TRUE_LONG_RUN_LIFT)*100:.1f}pp due to novelty.")
    if at_window > 0 and TRUE_LONG_RUN_LIFT <= 0:
        print(f"\nThe test would say 'ship' — but the feature has zero or negative long-run value.")
    print(f"\nTry TRUE_LONG_RUN_LIFT = 0 (pure novelty) or -0.01 (novelty masking harm).")


if __name__ == "__main__":
    main()
