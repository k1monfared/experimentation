"""Simulate behavioral segmentation and per-segment treatment effects.

Run an A/B test where the four behavioral segments respond differently.
See how the aggregate hides the heterogeneity.

To play, run:

    python chapters/11-segmentation/play/segmentation_simulator.py
"""

TREAT_LIFTS = {"active_contributor": 0.10, "active_consumer": 0.04,
               "silent_intentional": -0.03, "passive_consumer": 0.0}
N_TOTAL = 5000
BASE_P = 0.30
SEED = 110

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from expkit.segments.behavioral import simulate_population


def main():
    rng = np.random.default_rng(SEED)
    df = simulate_population(N_TOTAL, seed=SEED)
    df["arm"] = rng.choice(["control", "treatment"], size=N_TOTAL)
    df["outcome"] = 0
    for seg, lift in TREAT_LIFTS.items():
        for arm in ["control", "treatment"]:
            mask = (df["segment"] == seg) & (df["arm"] == arm)
            p = BASE_P + (lift if arm == "treatment" else 0.0)
            df.loc[mask, "outcome"] = rng.binomial(1, max(0, min(1, p)), size=int(mask.sum()))

    pooled = df.groupby("arm")["outcome"].mean()
    print(f"\nPooled: control={pooled['control']:.3f}, treatment={pooled['treatment']:.3f}, lift={pooled['treatment']-pooled['control']:+.3f}")
    print(f"\nPer segment:")
    for seg in sorted(df["segment"].unique()):
        sub = df[df["segment"] == seg]
        c = sub[sub["arm"] == "control"]["outcome"].mean()
        t = sub[sub["arm"] == "treatment"]["outcome"].mean()
        n = len(sub)
        print(f"  {seg:22s}: n={n:4d}  control={c:.3f}  treatment={t:.3f}  lift={t-c:+.3f}  (true={TREAT_LIFTS[seg]:+.3f})")
    print(f"\nChange TREAT_LIFTS to explore how different heterogeneity patterns affect the aggregate.")


if __name__ == "__main__":
    main()
