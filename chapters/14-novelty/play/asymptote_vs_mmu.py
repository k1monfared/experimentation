"""Decide ship or not by comparing the asymptotic effect to an MMU.

The two-lens commentary in the chapter lands on a decision rule: ship if
the posterior on the long-run effect exceeds the minimum meaningful uplift
from Chapter 8. Truncate-and-average only hands you a point estimate.
Fitting the decay curve and asking for its asymptote hands you an
interval, and the interval is what the MMU comparison actually needs.

This play shows the same treatment read three ways on a single event log:
the raw day-7 window mean, the truncate-and-average asymptote estimate,
and the fitted exponential-decay asymptote with a rough interval. The
decision flips depending on which estimate you feed the MMU rule.

To play, run:

    python chapters/14-novelty/play/asymptote_vs_mmu.py
"""

TRUE_ASYMPTOTE = 0.015    # long-run lift the feature actually delivers
INITIAL_NOVELTY = 0.06    # first-day novelty bump on top of asymptote
HALF_LIFE_DAYS = 5.0
N_DAYS = 40
BASE_RATE = 0.10
N_USERS_PER_DAY = 200
MMU = 0.01                 # minimum meaningful uplift from Ch 8
SEED = 140

import numpy as np


def simulate(seed=SEED):
    rng = np.random.default_rng(seed)
    days = np.arange(N_DAYS)
    true_lift = TRUE_ASYMPTOTE + INITIAL_NOVELTY * np.exp(-days / HALF_LIFE_DAYS)
    control_obs = rng.binomial(N_USERS_PER_DAY, BASE_RATE, size=N_DAYS) / N_USERS_PER_DAY
    treatment_obs = rng.binomial(
        N_USERS_PER_DAY, np.clip(BASE_RATE + true_lift, 0, 1), size=N_DAYS
    ) / N_USERS_PER_DAY
    return days, control_obs, treatment_obs


def fit_asymptote(days, lift):
    """Simple nonlinear fit of a + b * exp(-t / tau) via grid search."""
    best = (np.inf, 0.0, 0.0, 5.0)
    for tau in np.linspace(1.0, 20.0, 40):
        kernel = np.exp(-days / tau)
        x = np.column_stack([np.ones_like(days, dtype=float), kernel])
        coef, *_ = np.linalg.lstsq(x, lift, rcond=None)
        pred = x @ coef
        resid = np.sum((lift - pred) ** 2)
        if resid < best[0]:
            best = (resid, coef[0], coef[1], tau)
    _, a, b, tau = best
    se_resid = np.sqrt(best[0] / max(len(days) - 3, 1))
    return a, b, tau, se_resid


def main():
    days, control, treatment = simulate()
    lift = treatment - control

    day7_mean = lift[:7].mean()
    truncate_mean = lift[20:].mean()
    a, b, tau, se_resid = fit_asymptote(days, lift)
    asymptote_lo = a - 1.96 * se_resid / np.sqrt(N_DAYS)
    asymptote_hi = a + 1.96 * se_resid / np.sqrt(N_DAYS)

    print(f"\nTrue asymptote: {TRUE_ASYMPTOTE*100:+.2f}pp, MMU: {MMU*100:+.2f}pp\n")
    print(f"Day-7 window mean (naive):        {day7_mean*100:+.2f}pp  -> ship? {day7_mean > MMU}")
    print(f"Truncate day-20+ mean:            {truncate_mean*100:+.2f}pp  -> ship? {truncate_mean > MMU}")
    print(f"Fitted asymptote (a):             {a*100:+.2f}pp")
    print(f"  approx 95% interval:            [{asymptote_lo*100:+.2f}, {asymptote_hi*100:+.2f}]pp")
    print(f"  fit half-life:                  {tau:.1f} days (true = {HALF_LIFE_DAYS:.1f})")
    print(f"  ship? asymptote interval above MMU: {asymptote_lo > MMU}")

    print("\nThe day-7 mean and the fitted asymptote can disagree by more than MMU.")
    print("The truncate approach lands closer, but needs a cut you do not know a priori.")
    print("The fitted interval is the input the MMU rule actually wants.")


if __name__ == "__main__":
    main()
