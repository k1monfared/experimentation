"""Compare what a click, retention, and revenue metric each say at 7 vs 60 days.

The novelty lifecycle has three characters that move on different clocks:
the click-rate lift spikes and fades fast, the retention change builds
slowly, and revenue per user crosses zero when the long retention damage
finally outweighs the short click win. A 7-day test window catches only
the first character.

To play, run:

    python chapters/14-novelty/play/lifecycle_horizons.py
"""

CLICK_INITIAL_LIFT = 0.10      # big first-day click lift (fraction)
CLICK_HALF_LIFE = 8.0          # days
RETENTION_LONG_RUN_LOSS = 0.04 # asymptotic retention damage (fraction)
RETENTION_TIMESCALE = 18.0     # days to build
REVENUE_INITIAL_LIFT = 0.03    # short-run revenue bump
REVENUE_DECAY = 10.0           # days
REVENUE_LONG_RUN_LOSS = 0.02   # asymptotic revenue loss
REVENUE_TIMESCALE = 25.0       # days to build the loss

import numpy as np


def main():
    days = np.arange(0, 61)
    click = CLICK_INITIAL_LIFT * np.exp(-days / CLICK_HALF_LIFE)
    retention = -RETENTION_LONG_RUN_LOSS * (1 - np.exp(-days / RETENTION_TIMESCALE))
    revenue = REVENUE_INITIAL_LIFT * np.exp(-days / REVENUE_DECAY) \
        - RETENTION_LONG_RUN_LOSS * (1 - np.exp(-days / REVENUE_TIMESCALE))

    print("\nDay-7 readings (typical test window):")
    print(f"  click-rate lift:     {click[7]*100:+.2f}pp")
    print(f"  retention change:    {retention[7]*100:+.2f}pp")
    print(f"  revenue per user:    {revenue[7]*100:+.2f}%")

    print("\nDay-60 readings (closer to steady state):")
    print(f"  click-rate lift:     {click[60]*100:+.2f}pp")
    print(f"  retention change:    {retention[60]*100:+.2f}pp")
    print(f"  revenue per user:    {revenue[60]*100:+.2f}%")

    zero_crossings = np.where(np.diff(np.sign(revenue)) != 0)[0]
    if len(zero_crossings) > 0:
        print(f"\nRevenue crosses zero around day {int(zero_crossings[0])}.")
        print("Before that day the feature looks like a win, after it looks like a loss.")

    print("\nTry lowering CLICK_INITIAL_LIFT or raising RETENTION_LONG_RUN_LOSS")
    print("to see the window where the 7-day number flips sign from the 60-day number.")


if __name__ == "__main__":
    main()
