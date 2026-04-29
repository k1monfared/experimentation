"""Dilution: ITT vs per-protocol simulators with non-compliance."""

from __future__ import annotations

import numpy as np
import pandas as pd


def settings_page_experiment(
    n_users: int,
    visit_prob: float,
    base_rate: float,
    treatment_lift_among_visitors: float,
    seed: int | None = None,
) -> pd.DataFrame:
    """Simulate a feature on a settings page where most users never visit.

    All users are randomized to control/treatment (intent-to-treat). Each user
    visits with probability ``visit_prob``. Among visitors, treatment shifts the
    outcome by ``treatment_lift_among_visitors``. Among non-visitors, treatment
    has no effect.

    Returns a frame with columns: user_id, arm, visited, outcome.
    """
    rng = np.random.default_rng(seed)
    arm = rng.choice(["control", "treatment"], size=n_users)
    visited = rng.random(n_users) < visit_prob
    outcome = np.zeros(n_users, dtype=int)
    for i in range(n_users):
        if visited[i]:
            if arm[i] == "treatment":
                p = np.clip(base_rate + treatment_lift_among_visitors, 0.0, 1.0)
            else:
                p = base_rate
        else:
            p = base_rate
        outcome[i] = int(rng.random() < p)
    return pd.DataFrame({"user_id": np.arange(n_users), "arm": arm, "visited": visited, "outcome": outcome})
