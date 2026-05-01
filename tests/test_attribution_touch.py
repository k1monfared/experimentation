"""Tests for expkit.attribution.touch."""

from __future__ import annotations

import pytest

from expkit.attribution.touch import (
    aggregate_credit,
    first_touch,
    last_touch,
    linear,
    time_decay,
)


def test_first_touch_assigns_full_credit_to_first():
    assert first_touch(["search", "social", "email"]) == {"search": 1.0}


def test_last_touch_assigns_full_credit_to_last():
    assert last_touch(["search", "social", "email"]) == {"email": 1.0}


def test_first_and_last_handle_empty():
    assert first_touch([]) == {}
    assert last_touch([]) == {}


def test_linear_distributes_evenly():
    out = linear(["a", "b", "c", "d"])
    assert sum(out.values()) == pytest.approx(1.0)
    for k in ("a", "b", "c", "d"):
        assert out[k] == pytest.approx(0.25)


def test_linear_aggregates_repeats():
    out = linear(["a", "b", "a", "a"])
    assert sum(out.values()) == pytest.approx(1.0)
    assert out["a"] == pytest.approx(0.75)
    assert out["b"] == pytest.approx(0.25)


def test_time_decay_normalizes_to_one():
    out = time_decay(["a", "b", "c"], times=[0.0, 5.0, 10.0], half_life=5.0)
    assert sum(out.values()) == pytest.approx(1.0)


def test_time_decay_emphasizes_recent():
    out = time_decay(["far", "near"], times=[0.0, 7.0], half_life=7.0)
    assert out["near"] > out["far"]


def test_aggregate_credit_only_counts_converters():
    journeys = [
        (["a", "b"], [0, 1], 1),
        (["a", "c"], [0, 1], 0),  # not converted
        (["b", "c"], [0, 1], 1),
    ]
    df = aggregate_credit(journeys, scheme="last")
    totals = dict(zip(df["channel"], df["credit"]))
    # last-touch on the two converted journeys: b once, c once
    assert totals.get("b", 0) == pytest.approx(1.0)
    assert totals.get("c", 0) == pytest.approx(1.0)


def test_aggregate_credit_unknown_scheme_raises():
    with pytest.raises(ValueError):
        aggregate_credit([(["a"], [0], 1)], scheme="bogus")
