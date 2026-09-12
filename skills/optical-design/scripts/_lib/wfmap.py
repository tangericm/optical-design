"""Wavefront maps: coefficients to map, map I/O, least-squares Zernike fit, RMS and Strehl.

Shared by zernike.py, wavefront.py and interfero.py so no script imports another script.
Maps are square arrays in waves with NaN outside the pupil; coefficients carry a scheme
(see _lib/zernike.py).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

import _lib.zernike as Z

#: (n, m) pairs excluded from RMS unless low orders are kept explicitly.
LOW_ORDER = {(0, 0), (1, 1), (1, -1)}


def coefficients_to_map(scheme: str, coeffs: list[float], npix: int = 256):
    rho, theta, mask = Z.unit_disk(npix)
    B = Z.basis(scheme, len(coeffs), rho, theta)
    wmap = np.tensordot(np.asarray(coeffs, float), B, axes=1)
    wmap[~mask] = np.nan
    return wmap, mask


def load_map(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() == ".npy":
        return np.load(p).astype(float)
    return np.loadtxt(p, delimiter=",").astype(float)


def fit_map(wmap: np.ndarray, scheme: str, nterms: int, mask: np.ndarray | None = None):
    """Least-squares Zernike fit on the inscribed unit disk; NaN samples are ignored."""
    npix = wmap.shape[0]
    if wmap.shape[0] != wmap.shape[1]:
        raise ValueError("map must be square (pupil inscribed)")
    rho, theta, disk = Z.unit_disk(npix)
    valid = disk & np.isfinite(wmap)
    if mask is not None:
        valid &= mask.astype(bool)
    B = Z.basis(scheme, nterms, rho, theta)
    A = B[:, valid].T
    y = wmap[valid]
    coeffs, *_ = np.linalg.lstsq(A, y, rcond=None)
    residual = y - A @ coeffs
    return [float(c) for c in coeffs], float(np.sqrt(np.mean(residual**2)))


def rms_from_coeffs(scheme: str, coeffs: list[float], exclude_low_order: bool = True) -> float:
    total = 0.0
    for c, (n, m) in zip(coeffs, Z.indices(scheme, len(coeffs))):
        if exclude_low_order and (n, m) in LOW_ORDER:
            continue
        total += (c / Z.norm("noll", n, m)) ** 2 if scheme == "fringe" else c * c
    return math.sqrt(total)


def terms(scheme: str, coeffs: list[float]) -> list[dict[str, Any]]:
    j0 = Z.first_index(scheme)
    return [{"j": j0 + i, "n": n, "m": m, "name": Z.name(n, m), "value": c}
            for i, (c, (n, m)) in enumerate(zip(coeffs, Z.indices(scheme, len(coeffs))))]


def strehl_pair(rms_waves: float) -> tuple[float, float]:
    phase = 2 * math.pi * rms_waves
    return 1.0 - phase**2, math.exp(-(phase**2))
