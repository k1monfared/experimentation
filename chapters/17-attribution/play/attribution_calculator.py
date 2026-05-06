"""Compute credit under different attribution models for one conversion path.

Edit the TOUCHES list to reflect your customer's journey. Each entry
is a channel name. The conversion is at the end.

To play, run:

    python chapters/17-attribution/play/attribution_calculator.py
"""

TOUCHES = ["youtube_ad", "instagram_post", "google_paid_search", "marketing_email", "organic_visit"]
TOTAL_VALUE = 1.0      # total credit to distribute
TIME_DECAY = 0.5       # decay rate for time-decay model (0.5 = each step back halves the weight)

import sys


def main():
    n = len(TOUCHES)
    if n == 0:
        print("No touches. Add at least one to TOUCHES."); return
    # Last-touch
    last = {t: 0.0 for t in TOUCHES}; last[TOUCHES[-1]] = TOTAL_VALUE
    # First-touch
    first = {t: 0.0 for t in TOUCHES}; first[TOUCHES[0]] = TOTAL_VALUE
    # Linear
    linear = {t: TOTAL_VALUE / n for t in TOUCHES}
    # Time-decay (most recent = most credit)
    weights = [TIME_DECAY ** (n - 1 - i) for i in range(n)]
    total_w = sum(weights)
    decay = {t: (TOTAL_VALUE * w / total_w) for t, w in zip(TOUCHES, weights)}
    # Position-based (U-shaped): 40% first, 40% last, rest split
    pos = {t: 0.0 for t in TOUCHES}
    if n == 1:
        pos[TOUCHES[0]] = TOTAL_VALUE
    elif n == 2:
        pos[TOUCHES[0]] = pos[TOUCHES[-1]] = TOTAL_VALUE / 2
    else:
        pos[TOUCHES[0]] += 0.4 * TOTAL_VALUE
        pos[TOUCHES[-1]] += 0.4 * TOTAL_VALUE
        middle_each = 0.2 * TOTAL_VALUE / (n - 2) if n > 2 else 0
        for t in TOUCHES[1:-1]: pos[t] += middle_each

    print(f"\nConversion path ({n} touches):")
    print(" -> ".join(TOUCHES))
    print(f"\n{'Channel':25s}  {'last':>7s}  {'first':>7s}  {'linear':>7s}  {'time-decay':>10s}  {'position':>9s}")
    print("-" * 75)
    for t in TOUCHES:
        print(f"  {t:23s}  {last[t]:7.3f}  {first[t]:7.3f}  {linear[t]:7.3f}  {decay[t]:10.3f}  {pos[t]:9.3f}")
    print(f"\nSame path, five different credit stories.")


if __name__ == "__main__":
    main()
