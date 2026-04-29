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


def _write_meta(path: Path, seed: int | str | None, meta: dict | None) -> Path:
    payload = {"seed": seed, "sha256": _sha256_file(path), "meta": meta or {}}
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


def save_idata(idata, path: str | Path, seed: int | str | None = None, meta: dict | None = None) -> SaveResult:
    """Save an arviz ``InferenceData`` to ``path`` (.nc) with sidecar metadata."""
    path = Path(path)
    if path.suffix != ".nc":
        path = path.with_suffix(".nc")
    path.parent.mkdir(parents=True, exist_ok=True)
    idata.to_netcdf(str(path))
    meta_path = _write_meta(path, seed, meta)
    return SaveResult(path=path, sha256=_sha256_file(path), meta_path=meta_path)


def load_idata(path: str | Path):
    """Load an arviz ``InferenceData`` previously written by :func:`save_idata`."""
    return az.from_netcdf(str(Path(path)))


def read_sidecar(path: str | Path) -> dict:
    """Read the ``.meta.json`` sidecar for a sample or trace file."""
    p = Path(path)
    sidecar = p.with_suffix(p.suffix + ".meta.json")
    return json.loads(sidecar.read_text())
