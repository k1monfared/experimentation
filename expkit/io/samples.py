"""Save and load samples and PyMC traces with checksum and seed metadata."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import arviz as az
import numpy as np


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class SaveResult:
    path: Path
    sha256: str
    meta_path: Path


def _write_meta(path: Path, seed: int | str | None, meta: dict | None, sha256: str | None = None) -> Path:
    payload = {
        "seed": seed,
        "sha256": sha256 if sha256 is not None else _sha256_file(path),
        "meta": meta or {},
    }
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return meta_path


def save_samples(arr: np.ndarray, path: str | Path, seed: int | str | None = None, meta: dict | None = None) -> SaveResult:
    """Save a numpy array to ``path`` (npy) and write a sidecar ``.meta.json``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)
    if path.suffix != ".npy":
        path = path.with_suffix(".npy")
    meta_path = _write_meta(path, seed, meta)
    return SaveResult(path=path, sha256=_sha256_file(path), meta_path=meta_path)


def load_samples(path: str | Path) -> np.ndarray:
    """Load a numpy array previously written by :func:`save_samples`."""
    return np.load(Path(path))


_NONDETERMINISTIC_ATTRS = (
    "created_at",
    "sampling_time",
    "modeling_interface_version",
    "arviz_version",
    "inference_library_version",
)

_NONDETERMINISTIC_SAMPLE_STATS_VARS = (
    "perf_counter_diff",
    "perf_counter_start",
    "process_time_diff",
    "largest_eigval",
    "smallest_eigval",
)


def _normalize_idata_for_repro(idata):
    """Strip wall-clock timestamps and per-run sample_stats vars (timings, eigval NaNs).

    Posterior arrays are seed-deterministic but the netCDF/HDF5 byte layout still
    varies across processes. Stripping these makes the in-memory content stable.
    """
    for group in idata.groups():
        ds = idata[group]
        for attr in _NONDETERMINISTIC_ATTRS:
            ds.attrs.pop(attr, None)
    if "sample_stats" in idata.groups():
        ss = idata.sample_stats
        drop = [v for v in _NONDETERMINISTIC_SAMPLE_STATS_VARS if v in ss.data_vars]
        if drop:
            idata.sample_stats = ss.drop_vars(drop)


def _sha256_idata_canonical(idata) -> str:
    """Hash an ``InferenceData`` over its semantic content rather than file bytes.

    HDF5/netCDF on-disk layout (chunking, internal IDs) is not stable across
    processes, so file-level SHA drifts even when the science is identical.
    This walks groups in sorted order and hashes attrs and array bytes
    deterministically. Non-deterministic attrs and sample_stats vars are
    excluded the same way ``_normalize_idata_for_repro`` strips them.
    """
    h = hashlib.sha256()
    for group_name in sorted(idata.groups()):
        group = idata[group_name]
        h.update(b"\n=group=" + group_name.encode())
        for k in sorted(group.attrs):
            if k in _NONDETERMINISTIC_ATTRS:
                continue
            h.update(f"\nattr:{k}={group.attrs[k]!r}".encode())
        names = sorted(set(group.data_vars).union(group.coords))
        for name in names:
            if name in _NONDETERMINISTIC_SAMPLE_STATS_VARS:
                continue
            arr = np.ascontiguousarray(group[name].values)
            h.update(f"\nvar:{name}:{arr.dtype}:{arr.shape}".encode())
            h.update(arr.tobytes())
    return h.hexdigest()


def save_idata(idata, path: str | Path, seed: int | str | None = None, meta: dict | None = None) -> SaveResult:
    """Save an arviz ``InferenceData`` to ``path`` (.nc) with sidecar metadata.

    The returned ``SaveResult.sha256`` is the canonical content hash, not the
    file hash, so it is stable across machines and process invocations.
    """
    path = Path(path)
    if path.suffix != ".nc":
        path = path.with_suffix(".nc")
    path.parent.mkdir(parents=True, exist_ok=True)
    _normalize_idata_for_repro(idata)
    idata.to_netcdf(str(path))
    canonical = _sha256_idata_canonical(idata)
    meta_path = _write_meta(path, seed, meta, sha256=canonical)
    return SaveResult(path=path, sha256=canonical, meta_path=meta_path)


def load_idata(path: str | Path):
    """Load an arviz ``InferenceData`` previously written by :func:`save_idata`."""
    return az.from_netcdf(str(Path(path)))


def read_sidecar(path: str | Path) -> dict:
    """Read the ``.meta.json`` sidecar for a sample or trace file."""
    p = Path(path)
    sidecar = p.with_suffix(p.suffix + ".meta.json")
    return json.loads(sidecar.read_text())
