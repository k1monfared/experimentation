"""Tests for expkit.sim.dilution."""

from __future__ import annotations

import pytest

from expkit.sim.dilution import settings_page_experiment


def test_visit_rate_close_to_target():
    df = settings_page_experiment(20000, visit_prob=0.30, base_rate=0.1, treatment_lift_among_visitors=0.05, seed=0)
    assert df["visited"].mean() == pytest.approx(0.30, abs=0.02)


def test_arms_balanced_around_50_percent():
    df = settings_page_experiment(10000, visit_prob=0.5, base_rate=0.2, treatment_lift_among_visitors=0.0, seed=0)
    treat_frac = (df["arm"] == "treatment").mean()
    assert treat_frac == pytest.approx(0.5, abs=0.02)


def test_treatment_only_helps_visitors():
    df = settings_page_experiment(20000, visit_prob=0.5, base_rate=0.2, treatment_lift_among_visitors=0.20, seed=0)
    visited = df[df["visited"]]
    not_visited = df[~df["visited"]]
    visited_lift = visited[visited["arm"] == "treatment"]["outcome"].mean() - visited[visited["arm"] == "control"]["outcome"].mean()
    nv_lift = not_visited[not_visited["arm"] == "treatment"]["outcome"].mean() - not_visited[not_visited["arm"] == "control"]["outcome"].mean()
    assert visited_lift == pytest.approx(0.20, abs=0.04)
    assert nv_lift == pytest.approx(0.0, abs=0.02)


def test_outcome_binary():
    df = settings_page_experiment(500, visit_prob=0.4, base_rate=0.2, treatment_lift_among_visitors=0.1, seed=0)
    assert set(df["outcome"]) <= {0, 1}


def test_settings_experiment_deterministic():
    a = settings_page_experiment(200, visit_prob=0.3, base_rate=0.2, treatment_lift_among_visitors=0.1, seed=11)
    b = settings_page_experiment(200, visit_prob=0.3, base_rate=0.2, treatment_lift_among_visitors=0.1, seed=11)
    assert (a["outcome"].values == b["outcome"].values).all()
