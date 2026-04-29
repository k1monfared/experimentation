"""Behavioral user segmentation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

BEHAVIORAL_LABELS = ("active_contributor", "active_consumer", "silent_intentional", "passive_consumer")


def label_behavioral(df: pd.DataFrame) -> pd.Series:
    """Label each user with one of four behavioural buckets.

    Expected columns:
      - ``weekly_active_rate`` (fraction of weeks the user was active)
      - ``contribution_rate`` (fraction of sessions where user contributed)
      - ``intentional_rate`` (fraction of sessions where user navigated to specific content)

    The thresholds below are simple medians so the labels are well-defined for
    any input. Real applications would tune these per product.
    """
    medians = df[["weekly_active_rate", "contribution_rate", "intentional_rate"]].median()
    high_active = df["weekly_active_rate"] >= medians["weekly_active_rate"]
    high_contrib = df["contribution_rate"] >= medians["contribution_rate"]
    high_intent = df["intentional_rate"] >= medians["intentional_rate"]
    label = pd.Series("passive_consumer", index=df.index, dtype=object)
    label[high_active & high_contrib] = "active_contributor"
    label[high_active & ~high_contrib & high_intent] = "active_consumer"
    label[~high_active & high_intent] = "silent_intentional"
    return label


def simulate_population(n_users: int, seed: int | None = None) -> pd.DataFrame:
    """Generate a synthetic user population with the three behavioural axes."""
    rng = np.random.default_rng(seed)
    weekly = rng.beta(2, 5, size=n_users)
    contrib = rng.beta(1.5, 8, size=n_users)
    intent = rng.beta(2, 4, size=n_users)
    df = pd.DataFrame({"weekly_active_rate": weekly, "contribution_rate": contrib, "intentional_rate": intent})
    df["segment"] = label_behavioral(df)
    return df
