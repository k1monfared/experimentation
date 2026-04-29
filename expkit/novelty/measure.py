"""Measurement schemes for novelty effects."""

from __future__ import annotations

import numpy as np
import pandas as pd


def by_calendar_day(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the event log by calendar day from launch.

    Returns a frame with one row per (day, arm) and the conversion rate.
    """
    return df.groupby(["day", "arm"])["outcome"].mean().unstack().reset_index()


def by_days_since_exposure(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by per-user time since first exposure (treatment only).

    Returns one row per ``days_since_first_exposure`` value with the treatment
    conversion rate. Control gets a single overall mean for comparison.
    """
    treat = df[df["arm"] == "treatment"]
    treat = treat.dropna(subset=["days_since_first_exposure"])
    treat_rate = treat.groupby("days_since_first_exposure")["outcome"].mean().rename("treatment").reset_index()
    control_mean = float(df[df["arm"] == "control"]["outcome"].mean())
    treat_rate["control"] = control_mean
    return treat_rate


def by_exposure_count(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by per-user exposure count (treatment only)."""
    treat = df[df["arm"] == "treatment"]
    out = treat.groupby("exposure_count")["outcome"].mean().rename("treatment").reset_index()
    out["control"] = float(df[df["arm"] == "control"]["outcome"].mean())
    return out
