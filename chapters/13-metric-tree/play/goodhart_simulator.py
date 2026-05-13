"""A proxy that is positively correlated cross-sectionally and
negatively correlated under optimization.

Clicks and revenue rise together across organic variation. A team then
pushes a clickbait variant that raises clicks by CLICKBAIT_BOOST_PCT at
the cost of a BOUNCE_RATE_PENALTY: bounce rate goes up and revenue per
click falls. The script reports both views of the proxy.

Watch r_cross stay positive while r_opt goes negative as you raise
CLICKBAIT_BOOST_PCT or BOUNCE_RATE_PENALTY. Goodhart's law in numbers.

To play, run:

    python chapters/13-metric-tree/play/goodhart_simulator.py
"""

N = 200
CLICKBAIT_BOOST_PCT = 30.0
BOUNCE_RATE_PENALTY = 0.40
BASELINE_CTR = 0.05
BASELINE_REV_PER_CLICK = 1.00
SEED = 1

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np


def main():
    rng = np.random.default_rng(SEED)

    # Cross-sectional: organic variation in quality drives both clicks and revenue up.
    quality = rng.normal(0, 1, N)
    clicks_cross = BASELINE_CTR * (1 + 0.20 * quality) + rng.normal(0, 0.002, N)
    revenue_cross = BASELINE_REV_PER_CLICK * clicks_cross * (1 + 0.10 * quality)
    r_cross = float(np.corrcoef(clicks_cross, revenue_cross)[0, 1])

    # Optimization: push a clickbait lever. Clicks go up by CLICKBAIT_BOOST_PCT,
    # but each click converts BOUNCE_RATE_PENALTY less to revenue.
    lever = rng.uniform(0, 1, N)  # how hard each experiment pushes the clickbait lever
    clicks_opt = BASELINE_CTR * (1 + (CLICKBAIT_BOOST_PCT / 100.0) * lever) + rng.normal(0, 0.002, N)
    revenue_opt = BASELINE_REV_PER_CLICK * clicks_opt * (1 - BOUNCE_RATE_PENALTY * lever)
    r_opt = float(np.corrcoef(clicks_opt, revenue_opt)[0, 1])

    print(f"\nClickbait lever up to {CLICKBAIT_BOOST_PCT:.0f}% clicks, bounce penalty {BOUNCE_RATE_PENALTY:.2f} per unit lever.")
    print()
    print(f"Cross-sectional (organic quality varies): r(clicks, revenue) = {r_cross:+.2f}")
    print(f"Under optimization (clickbait lever pushed): r(clicks, revenue) = {r_opt:+.2f}")
    print()
    mean_rev_cross = revenue_cross.mean()
    mean_rev_opt = revenue_opt.mean()
    print(f"Mean revenue cross-sectional: {mean_rev_cross:.4f}")
    print(f"Mean revenue under clickbait: {mean_rev_opt:.4f}")
    if r_cross > 0 and r_opt < 0:
        print()
        print("Same proxy, same metric pair. Positive in the wild, negative under the knob.")
        print("This is Goodhart. A historical correlation check would have blessed clicks.")
        print("Detecting the flip requires measuring revenue alongside during rollout.")


if __name__ == "__main__":
    main()
