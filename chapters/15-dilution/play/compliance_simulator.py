"""How does compliance rate affect the intent-to-treat estimate?

Set the true drug effect and the compliance rate (fraction of
treatment-arm patients who actually take the drug). The script
shows how the measured ITT dilutes the true effect.

To play, run:

    python chapters/15-dilution/play/compliance_simulator.py
"""

TRUE_EFFECT = 0.10     # true per-treatment effect (pp)
COMPLIANCE = 0.70      # fraction of treatment arm who take the drug
BASE_RATE = 0.30       # outcome rate in untreated
N_PER_ARM = 1000
SEED = 0

import sys
import numpy as np


def main():
    rng = np.random.default_rng(SEED)
    n = N_PER_ARM
    s_c = rng.binomial(n, BASE_RATE)
    compliers = int(n * COMPLIANCE)
    noncompliers = n - compliers
    s_t = rng.binomial(compliers, BASE_RATE + TRUE_EFFECT) + rng.binomial(noncompliers, BASE_RATE)
    itt = s_t / n - s_c / n
    per_protocol_approx = itt / COMPLIANCE  # rough: divide by compliance

    print(f"\nTrue per-treatment effect: {TRUE_EFFECT*100:+.1f}pp")
    print(f"Compliance rate: {COMPLIANCE*100:.0f}%")
    print(f"Base rate: {BASE_RATE*100:.0f}%")
    print(f"\nOutcomes: control={s_c}/{n} ({s_c/n:.3f}), treatment={s_t}/{n} ({s_t/n:.3f})")
    print(f"\nIntent-to-treat estimate: {itt*100:+.2f}pp (measures 'roll-out effect')")
    print(f"Per-protocol approximation: {per_protocol_approx*100:+.2f}pp (measures 'drug effect on compliers')")
    print(f"True effect: {TRUE_EFFECT*100:+.1f}pp")
    print(f"\nAs compliance falls, ITT shrinks toward zero even when the drug really works.")
    print(f"Try COMPLIANCE = 1.0 (perfect) and COMPLIANCE = 0.30 (poor) to see the range.")


if __name__ == "__main__":
    main()
