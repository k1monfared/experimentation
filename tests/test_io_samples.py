"""Tests for expkit.io.samples."""

from __future__ import annotations

import json

import numpy as np
import pytest

from expkit.io.samples import (
    load_samples,
    read_sidecar,
    save_samples,
)
from expkit.sim.coin import bernoulli_sequence


def test_save_load_roundtrip(tmp_path):
    seq = bernoulli_sequence(50, p=0.4, seed=7)
    res = save_samples(seq, tmp_path / "seq", seed=7, meta={"p": 0.4, "n": 50})
    loaded = load_samples(res.path)
    np.testing.assert_array_equal(loaded, seq)


def test_meta_sidecar_contains_seed_and_checksum(tmp_path):
    seq = bernoulli_sequence(20, p=0.5, seed=1)
    res = save_samples(seq, tmp_path / "tiny", seed=1, meta={"note": "tiny"})
    payload = json.loads(res.meta_path.read_text())
    assert payload["seed"] == 1
    assert payload["sha256"] == res.sha256
    assert payload["meta"] == {"note": "tiny"}


def test_read_sidecar_helper(tmp_path):
    seq = bernoulli_sequence(5, p=0.5, seed=2)
    res = save_samples(seq, tmp_path / "five", seed=2)
    payload = read_sidecar(res.path)
    assert payload["seed"] == 2
    assert "sha256" in payload


def test_save_creates_parent_dir(tmp_path):
    seq = bernoulli_sequence(3, p=0.5, seed=0)
    target = tmp_path / "nested" / "dir" / "x"
    save_samples(seq, target, seed=0)
    assert (tmp_path / "nested" / "dir" / "x.npy").exists()
