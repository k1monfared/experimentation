"""How far does a headline from one population carry to another?

The study was run in 22-year-old college students and found a +5pp lift.
The real population is a mix of segments. Each segment has its own true
lift. Weight the per-segment lifts by the population shares, and the
headline often shrinks, vanishes, or flips sign.

Edit the SEGMENTS list below to try a different mix. Each row is:
    (name, population share, baseline outcome rate, treatment lift)
Shares must sum to 1.0.

The script reports:
    - the studied-cohort lift (what the press release says),
    - the population-weighted lift (what the intervention does in the wild),
    - the per-segment lifts from a finite simulated sample of N_UNIVERSE users.

To play, run:

    python chapters/09-wine-and-the-small-print/play/external_validity_sim.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from expkit.sim.user_segments import SegmentSpec, segmented_binary  # noqa: E402

STUDIED_LIFT = 0.05
N_UNIVERSE = 20000
SEED = 901

SEGMENTS = [
    # (name, share, baseline, treatment_lift)
    ("22yo college students",   0.10, 0.40,  0.05),
    ("40yo under stress",       0.20, 0.55, -0.02),
    ("65+ healthy adults",      0.20, 0.30,  0.01),
    ("pregnant women",          0.05, 0.45, -0.10),
    ("teens",                   0.10, 0.20, -0.05),
    ("middle-aged sedentary",   0.35, 0.50,  0.00),
]


def main():
    total_share = sum(s[1] for s in SEGMENTS)
    if abs(total_share - 1.0) > 1e-6:
        print(f"ERROR: segment shares sum to {total_share:.4f}, not 1.0.")
        return

    specs = [SegmentSpec(n, f, b, l) for (n, f, b, l) in SEGMENTS]
    sim = segmented_binary(N_UNIVERSE, specs, seed=SEED)

    print("\nStudied-cohort headline lift: +{:.3f} ({:+.1f} pp)".format(STUDIED_LIFT, STUDIED_LIFT * 100))
    print("\nPer-segment ground-truth lifts (what was injected) and simulated-sample estimates:")
    print(f"  {'segment':<28} {'share':>6} {'truth':>8} {'sample':>8} {'n_seg':>8}")
    weighted_truth = 0.0
    for spec in specs:
        arr = sim[spec.name]
        n_seg = len(arr["control"]) + len(arr["treatment"])
        sample = arr["treatment"].mean() - arr["control"].mean()
        weighted_truth += spec.fraction * spec.treatment_lift
        print(f"  {spec.name:<28} {spec.fraction:>6.2f} {spec.treatment_lift:>+8.3f} {sample:>+8.3f} {n_seg:>8d}")

    print(f"\nPopulation-weighted ground-truth lift: {weighted_truth:+.4f} ({weighted_truth * 100:+.2f} pp)")
    if weighted_truth > 0:
        print("  The wider-world average is positive, but probably smaller than the headline.")
    elif weighted_truth < 0:
        print("  The wider-world average is negative. The headline is misleading.")
    else:
        print("  The wider-world average is zero. The headline does not carry.")
    print("\nThe press release reads the first number. The population feels the last one.")


if __name__ == "__main__":
    main()
