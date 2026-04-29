"""Generators with novelty / decay / ramp time profiles."""

from __future__ import annotations

import numpy as np
import pandas as pd


def novelty_event_log(
    n_users: int,
    days: int,
    base_rate: float,
    initial_lift: float,
    half_life_days: float,
    arrival_rate: float = 0.4,
    seed: int | None = None,
) -> pd.DataFrame:
    """Simulate a per-user, per-day event log under a novelty-decay treatment.

    Each user is randomly assigned to control or treatment with equal
    probability. Each user shows up on day d with probability ``arrival_rate``.
    A treatment user's per-event success probability on day d, measured from
    THEIR first exposure, is ``base_rate + initial_lift * exp(-d / half_life_days)``.

    Returns a long-format DataFrame with columns: user_id, arm, day,
    days_since_first_exposure, exposure_count, outcome.
    """
    rng = np.random.default_rng(seed)
    arms = rng.choice(["control", "treatment"], size=n_users)
    rows = []
    for u in range(n_users):
        arm = str(arms[u])
        first_exposure_day = None
        exposure_count = 0
        for d in range(days):
            if rng.random() < arrival_rate:
                if first_exposure_day is None and arm == "treatment":
                    first_exposure_day = d
                if arm == "treatment":
                    exposure_count += 1
                # success probability
                if arm == "control":
                    p = base_rate
                else:
                    if first_exposure_day is None:
                        p = base_rate
                    else:
                        days_since = d - first_exposure_day
                        p = np.clip(base_rate + initial_lift * np.exp(-days_since / half_life_days), 0.0, 1.0)
                outcome = int(rng.random() < p)
                rows.append({
                    "user_id": u,
                    "arm": arm,
                    "day": d,
                    "days_since_first_exposure": (d - first_exposure_day) if first_exposure_day is not None else None,
                    "exposure_count": exposure_count if arm == "treatment" else 0,
                    "outcome": outcome,
                })
    return pd.DataFrame(rows)
