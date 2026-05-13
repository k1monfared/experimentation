"""Short-horizon click win, long-horizon retention loss. What horizon reveals the trap?

A feature pumps day-1 clicks by CLICK_BOOST_PCT, the novelty decays with
time constant CLICK_DECAY_DAYS, and retention loss accumulates up to
RETENTION_LOSS_PCT by day 30. Vary HORIZON_DAYS: at 7 the click win is
still positive and the retention loss is barely visible. At 30 the story
reverses. Try shorter CLICK_DECAY_DAYS or larger RETENTION_LOSS_PCT and
watch the crossover move.

To play, run:

    python chapters/10-industry-experimentation/play/clickbait_simulator.py
"""

CLICK_BOOST_PCT = 10.0
CLICK_DECAY_DAYS = 7.0
RETENTION_LOSS_PCT = 5.0
RETENTION_BUILD_DAYS = 12.0
HORIZON_DAYS = 7

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np


def click_lift(day):
    return CLICK_BOOST_PCT * np.exp(-day / CLICK_DECAY_DAYS)


def retention_change(day):
    return -RETENTION_LOSS_PCT * (1 - np.exp(-max(day - 1, 0) / RETENTION_BUILD_DAYS))


def main():
    days = [1, 7, 14, 30]
    print(f"\nClick lift {CLICK_BOOST_PCT:+.0f}% at day 1, decay tau={CLICK_DECAY_DAYS:.0f}d.")
    print(f"Retention loss asymptote {-RETENTION_LOSS_PCT:.0f}pp, build tau={RETENTION_BUILD_DAYS:.0f}d.\n")
    print(f"{'day':>5} {'click lift (%)':>16} {'retention (pp)':>16}")
    for d in days:
        print(f"{d:>5d} {click_lift(d):>16.2f} {retention_change(d):>16.2f}")

    c = click_lift(HORIZON_DAYS)
    r = retention_change(HORIZON_DAYS)
    print(f"\nAt the chosen horizon day {HORIZON_DAYS}:")
    print(f"  click lift = {c:+.2f}%, retention change = {r:+.2f}pp")
    if c > 0 and r > -1:
        print("  Decision on clicks alone would ship. The retention loss is still hiding.")
    elif c > 0 and r <= -1:
        print("  Both signals are visible. The trade-off is in the open.")
    else:
        print("  The click win has faded. The retention loss is fully revealed.")

    # When would the aggregate flip? Solve click_lift(d) + retention_change(d) = 0.
    grid = np.linspace(1, 60, 600)
    combined = click_lift(grid) + retention_change(grid)
    crossover = grid[np.argmin(np.abs(combined))]
    print(f"\nThe click lift and retention change roughly cancel around day {crossover:.1f}.")
    print("Before that day the proxy sells the ship. After it the outcome shows the cost.")


if __name__ == "__main__":
    main()
