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


def coefficients_to_map(scheme: str, coeffs: list[float], npix: int = 256,
                        pupil: dict[str, Any] | None = None):
    """Sum a scheme's terms on an npix² grid; NaN outside the pupil.

    Without `pupil` the unit circle is inscribed in the grid; pass the `pupil` a fit
    reported to put the map back on that fit's normalization circle.
    """
    if pupil is None:
        rho, theta, mask = Z.unit_disk(npix)
    else:
        rho, theta, mask = pupil_grid((npix, npix), pupil)
    B = Z.basis(scheme, len(coeffs), rho, theta)
    wmap = np.tensordot(np.asarray(coeffs, float), B, axes=1)
    wmap[~mask] = np.nan
    return wmap, mask


def load_map(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() == ".npy":
        return np.load(p).astype(float)
    return np.loadtxt(p, delimiter=",").astype(float)


def pupil_grid(shape: tuple[int, int], pupil: dict[str, Any]):
    """rho, theta and a boolean mask for the circular pupil `{center_px, radius_px}`."""
    cy, cx = pupil["center_px"]
    radius = float(pupil["radius_px"])
    yy, xx = np.indices(shape)
    dy, dx = yy - float(cy), xx - float(cx)
    rho = np.hypot(dy, dx) / radius
    return rho, np.arctan2(dy, dx), rho <= 1.0


def _pupil_radius(valid: np.ndarray, cy: float, cx: float) -> float:
    """Pupil radius in pixels from a boolean pupil mask and its centre.

    Only valid pixels are consulted: radius is the farthest valid pixel from the centroid,
    snapped to the nearest half pixel. Invalid pixels are never used to bracket the edge — a
    single invalid pixel *inside* the aperture (a dead pixel, an obscuration) sits close to
    the centre, and bracketing against the nearest invalid pixel anywhere on the grid would
    collapse the estimate toward that interior point instead of the true rim.

    A synthetic disk digitized on an npix grid falls short of the generating radius npix/2
    by a sub-pixel amount that shrinks as the grid gets finer (measured: 0.047 px at npix=32,
    0.023 px at npix=64, 0.057 px at npix=96, 0.027 px at npix=128, 0.006 px at npix=256) —
    no single additive constant reproduces npix/2 exactly across sizes, so the estimate is
    snapped to the nearest half pixel instead. That reproduces the generating radius exactly
    for every npix above, which is what the map -> fit round trip needs. A genuinely
    non-round measured radius is snapped the same way; half-pixel granularity is the
    resolution of this estimator once it may not look at invalid pixels.
    """
    ys, xs = np.nonzero(valid)
    max_d = float(np.max(np.hypot(ys - cy, xs - cx)))
    return round(max_d * 2.0) / 2.0


def fit_map(wmap: np.ndarray, scheme: str, nterms: int, mask: np.ndarray | None = None):
    """Least-squares Zernike fit over the pupil the valid samples occupy.

    The normalization circle comes from the data, not from the canvas, so a pupil filling
    only part of the canvas still returns unscaled coefficients. Its centre is the centroid
    of the valid pixels; its radius is the farthest valid pixel from that centroid, snapped
    to the nearest half pixel (see `_pupil_radius` — invalid pixels are never consulted, so
    an interior dead pixel or obscuration cannot pull the radius down). An all-finite square
    input carries no pupil boundary, so the inscribed circle is assumed; that case reproduces
    `Z.unit_disk` exactly (centre (npix−1)/2, radius npix/2). NaN samples are ignored.

    Returns (coefficients, residual_rms, pupil) with
    pupil = {"center_px": [cy, cx], "radius_px": r}.
    """
    if wmap.ndim != 2 or wmap.shape[0] != wmap.shape[1]:
        raise ValueError("map must be square (pupil inscribed)")
    valid = np.isfinite(wmap)
    if mask is not None:
        valid = valid & mask.astype(bool)
    if valid.all():
        valid = valid & Z.unit_disk(wmap.shape[0])[2]
    if not valid.any():
        raise ValueError("map has no valid samples inside the pupil")
    ys, xs = np.nonzero(valid)
    cy, cx = float(ys.mean()), float(xs.mean())
    pupil = {"center_px": [cy, cx], "radius_px": _pupil_radius(valid, cy, cx)}
    rho, theta, _circle = pupil_grid(wmap.shape, pupil)
    B = Z.basis(scheme, nterms, rho, theta)
    A = B[:, valid].T
    y = wmap[valid]
    coeffs, *_ = np.linalg.lstsq(A, y, rcond=None)
    residual = y - A @ coeffs
    return [float(c) for c in coeffs], float(np.sqrt(np.mean(residual**2))), pupil


def rms_from_coeffs(scheme: str, coeffs: list[float], exclude_low_order: bool = True) -> float:
    """RMS over the pupil. Piston is the mean of the wavefront, so it never contributes."""
    total = 0.0
    for c, (n, m) in zip(coeffs, Z.indices(scheme, len(coeffs))):
        if (n, m) == (0, 0):
            continue
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
