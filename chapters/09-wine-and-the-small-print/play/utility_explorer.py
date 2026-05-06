"""When does a target benefit outweigh a harm?

Set the target effect, the harm effect, and a weighting on the target.
The script tells me whether the weighted utility is positive (ship)
or negative (do not ship), and where the boundary weight is.

Try TARGET = 0.3, HARM = -0.4, and various weights from 0.4 to 0.7.
At weight 0.5, the utility is negative (more harm than target).
At weight 0.6, slightly positive.

To play, run:

    python chapters/09-wine-and-the-small-print/play/utility_explorer.py
"""

TARGET_EFFECT = 0.30
HARM_EFFECT = -0.40
WEIGHT_ON_TARGET = 0.50

import sys


def main():
    w = WEIGHT_ON_TARGET
    u = w * TARGET_EFFECT + (1 - w) * HARM_EFFECT
    boundary = abs(HARM_EFFECT) / (TARGET_EFFECT + abs(HARM_EFFECT))
    print(f"\nTarget effect: {TARGET_EFFECT:+.2f} (good)")
    print(f"Harm effect:   {HARM_EFFECT:+.2f} (bad)")
    print(f"Weight on target: {w:.2f} (1 - w = {1 - w:.2f} on harm)\n")
    print(f"Weighted utility: {u:+.4f}")
    print(f"Verdict: {'SHIP (positive utility)' if u > 0 else 'DO NOT SHIP (negative utility)'}\n")
    print(f"Boundary weight (where utility = 0): {boundary:.4f}")
    print(f"  At weights below {boundary:.2f}: do not ship.")
    print(f"  At weights above {boundary:.2f}: ship.")
    print(f"\nTwo stakeholders with different weights look at the same data and reach different decisions.")
    print(f"The data does not pick the weight. The weight is a values question.")


if __name__ == "__main__":
    main()
