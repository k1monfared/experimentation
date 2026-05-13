"""Compare decay, primacy, and U-shape patterns at the same test window.

A 7-day A/B test reads one number, the mean effect in the first week. But
the same mean can come from very different shapes. Decay says the early
win will fade. Primacy says the early flat reading hides a later win.
U-shape says the early dip hides a later recovery. Reaching for one shape
when another is true is how programs ship too early or give up too early.

To play, run:

    python chapters/14-novelty/play/decay_shapes.py
"""

INITIAL_AMPLITUDE = 0.06   # peak magnitude of the pattern (fraction)
DECAY_TIMESCALE = 5.0      # days, for the decay shape
PRIMACY_TIMESCALE = 10.0   # days, for the primacy ramp
U_SHAPE_PERIOD = 12.0      # days, wavelength of the U-shape
TEST_WINDOW_DAYS = 7
STEADY_STATE_DAY = 30

import numpy as np


def main():
    days = np.arange(0, 41)
    decay = INITIAL_AMPLITUDE * np.exp(-days / DECAY_TIMESCALE)
    primacy = INITIAL_AMPLITUDE * (1 - np.exp(-days / PRIMACY_TIMESCALE))
    u_shape = INITIAL_AMPLITUDE * np.cos(days / U_SHAPE_PERIOD) ** 2 - 0.02

    shapes = {
        "decay (classic novelty)": decay,
        "primacy (slow ramp-up)": primacy,
        "U-shape (dip then recovery)": u_shape,
    }

    print(f"\nTest window: first {TEST_WINDOW_DAYS} days, mean effect")
    print(f"Steady state reference: day {STEADY_STATE_DAY}\n")
    for name, curve in shapes.items():
        window_mean = curve[:TEST_WINDOW_DAYS + 1].mean()
        steady = curve[STEADY_STATE_DAY]
        direction = "SHIP" if window_mean > 0.01 else "NO SHIP"
        wrong = (
            (direction == "SHIP" and steady <= 0.01)
            or (direction == "NO SHIP" and steady > 0.01)
        )
        flag = "  <-- wrong call" if wrong else ""
        print(f"{name:32s}  day-7 mean = {window_mean*100:+.2f}pp  |  day-30 = {steady*100:+.2f}pp  |  call: {direction}{flag}")

    print("\nThe same test window can ship a decay (fading win), reject a primacy")
    print("(real win, not yet visible), and misread a U-shape in either direction.")


if __name__ == "__main__":
    main()
