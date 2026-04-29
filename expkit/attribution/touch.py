"""Multi-touch attribution: first-touch, last-touch, linear, time-decay."""

from __future__ import annotations

import numpy as np
import pandas as pd


def first_touch(touches: list[str]) -> dict[str, float]:
    """Assign full credit to the first touchpoint."""
    if not touches:
        return {}
    return {touches[0]: 1.0}


def last_touch(touches: list[str]) -> dict[str, float]:
    if not touches:
        return {}
    return {touches[-1]: 1.0}


def linear(touches: list[str]) -> dict[str, float]:
    if not touches:
        return {}
    weight = 1.0 / len(touches)
    out = {}
    for t in touches:
        out[t] = out.get(t, 0.0) + weight
    return out


def time_decay(touches: list[str], times: list[float], half_life: float = 7.0) -> dict[str, float]:
    """Time-decay: weight = 0.5 ** (delta_t / half_life), normalized to sum to 1."""
    if not touches:
        return {}
    times_arr = np.asarray(times, dtype=float)
    last = times_arr.max()
    weights = 0.5 ** ((last - times_arr) / half_life)
    weights = weights / weights.sum()
    out: dict[str, float] = {}
    for t, w in zip(touches, weights):
        out[t] = out.get(t, 0.0) + float(w)
    return out


def aggregate_credit(journeys: list[tuple[list[str], list[float], int]], scheme: str = "linear", half_life: float = 7.0) -> pd.DataFrame:
    """Aggregate channel credit across many user journeys.

    ``journeys`` is a list of (touches, times, converted) tuples. Only converted
    journeys produce credit. Returns a DataFrame summed per channel.
    """
    totals: dict[str, float] = {}
    for touches, times, converted in journeys:
        if not converted:
            continue
        if scheme == "first":
            credit = first_touch(touches)
        elif scheme == "last":
            credit = last_touch(touches)
        elif scheme == "linear":
            credit = linear(touches)
        elif scheme == "time_decay":
            credit = time_decay(touches, times, half_life=half_life)
        else:
            raise ValueError(f"unknown scheme: {scheme}")
        for ch, w in credit.items():
            totals[ch] = totals.get(ch, 0.0) + w
    return pd.DataFrame(sorted(totals.items()), columns=["channel", "credit"])
