"""Tests for expkit.io.samples."""

from __future__ import annotations

import json

import arviz as az
import numpy as np
import pytest

from expkit.io.samples import (
    load_idata,
    load_samples,
    read_sidecar,
    save_idata,
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


def _toy_idata(timing_offset: float = 0.0, timestamp: str = "2020-01-01T00:00:00"):
    """Build a small InferenceData with posterior + sample_stats and the kinds of
    nondeterministic attrs/vars that ``_normalize_idata_for_repro`` is supposed to strip.

    The posterior arrays are fixed across calls; only the strip-targeted fields vary.
    Used to assert canonical hashing is stable across run-to-run jitter.

    ``az.from_dict`` changed in arviz 1.0: pre-1.0 took ``posterior=`` etc as keyword
    arguments, 1.0+ takes a single nested dict positionally. Try the new shape first.
    Nondeterministic attrs are attached post-hoc because ``attrs=`` has different
    semantics on the two versions.
    """
    rng = np.random.default_rng(0)
    posterior = {"p": rng.standard_normal((2, 8))}
    sample_stats = {
        "lp": rng.standard_normal((2, 8)),
        "perf_counter_diff": np.full((2, 8), timing_offset),
        "process_time_diff": np.full((2, 8), timing_offset),
    }
    try:
        idata = az.from_dict({"posterior": posterior, "sample_stats": sample_stats})
    except TypeError:
        idata = az.from_dict(posterior=posterior, sample_stats=sample_stats)
    for group in ("posterior", "sample_stats"):
        idata[group].attrs["created_at"] = timestamp
        idata[group].attrs["sampling_time"] = timing_offset
    return idata


def test_save_idata_roundtrip(tmp_path):
    idata = _toy_idata()
    res = save_idata(idata, tmp_path / "trace", seed=42, meta={"chapter": "test"})
    assert res.path.exists()
    assert res.path.suffix == ".nc"
    loaded = load_idata(res.path)
    np.testing.assert_array_equal(
        np.asarray(loaded["posterior"]["p"].values),
        np.asarray(idata["posterior"]["p"].values),
    )


def test_save_idata_hash_ignores_nondeterministic_fields(tmp_path):
    """Two traces with identical posteriors but different timestamps and timings
    must produce the same canonical sha256, otherwise the manifest churns every run.
    """
    a = save_idata(_toy_idata(timing_offset=0.1, timestamp="2020-01-01T00:00:00"),
                   tmp_path / "a", seed=1)
    b = save_idata(_toy_idata(timing_offset=99.9, timestamp="2099-12-31T23:59:59"),
                   tmp_path / "b", seed=1)
    assert a.sha256 == b.sha256


def test_save_idata_hash_changes_when_posterior_changes(tmp_path):
    """Sanity: actual posterior differences must move the canonical sha256."""
    a = save_idata(_toy_idata(), tmp_path / "a", seed=1)
    different = _toy_idata()
    different["posterior"]["p"].values[...] += 1.0
    b = save_idata(different, tmp_path / "b", seed=1)
    assert a.sha256 != b.sha256
