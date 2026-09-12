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
    raw = np.load(p, allow_pickle=False) if p.suffix.lower() == ".npy" else np.loadtxt(p, delimiter=",")
    if np.iscomplexobj(raw):
        raise ValueError("map must contain real wavefront samples")
    wmap = raw.astype(float)
    if np.isinf(wmap).any():
        raise ValueError("map cannot contain infinity; use NaN for opaque aperture pixels")
    return wmap


def pupil_grid(shape: tuple[int, int], pupil: dict[str, Any]):
    """rho, theta and a boolean mask for the circular pupil `{center_px, radius_px}`."""
    cy, cx = pupil["center_px"]
    radius = float(pupil["radius_px"])
    if not np.isfinite([cy, cx, radius]).all() or radius <= 0:
        raise ValueError("pupil center and radius must be finite; radius must be positive")
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


def infer_pupil(valid: np.ndarray) -> dict[str, Any]:
    """Estimate a circular outer rim; masked pixels are not measurement samples.

    This centroid/rim estimate assumes a complete symmetric pupil. Supply explicit
    geometry for clipped/asymmetric pupils; sampled data cannot determine a missing rim.
    """
    if valid.ndim != 2 or not valid.any():
        raise ValueError("map has no valid samples inside the pupil")
    ys, xs = np.nonzero(valid)
    cy, cx = float(ys.mean()), float(xs.mean())
    radius = _pupil_radius(valid, cy, cx)
    if radius <= 0:
        raise ValueError("pupil must span more than one spatial sample")
    return {"center_px": [cy, cx], "radius_px": radius}


def fit_map(wmap: np.ndarray, scheme: str, nterms: int, mask: np.ndarray | None = None,
            *, pupil: dict[str, Any] | None = None):
    """Least-squares Zernike fit over the pupil the valid samples occupy.

    The normalization circle comes from the data, not from the canvas, so a pupil filling
    only part of the canvas still returns unscaled coefficients. Its centre is the centroid
    of the valid pixels; its radius is the farthest valid pixel from that centroid, snapped
    to the nearest half pixel (see `_pupil_radius` — invalid pixels are never consulted, so
    an interior dead pixel or obscuration cannot pull the radius down). An all-finite square
    input carries no pupil boundary, so the inscribed circle is assumed; that case reproduces
    `Z.unit_disk` exactly (centre (npix−1)/2, radius npix/2). NaN samples are ignored.

    Returns (coefficients, residual_rms, pupil). Pupil includes center/radius plus
    rank, condition_number, valid_samples, valid_coverage_fraction, fit_terms and
    fit_rms_on_mask (standard deviation of reconstruction; tilt retained).
    """
    if wmap.ndim != 2 or wmap.shape[0] != wmap.shape[1] or wmap.shape[0] < 2:
        raise ValueError("map must be square (pupil inscribed)")
    if np.iscomplexobj(wmap) or np.isinf(wmap).any():
        raise ValueError("map must contain real waves or NaN aperture pixels, not infinity")
    if isinstance(nterms, bool) or not isinstance(nterms, (int, np.integer)) or nterms <= 0:
        raise ValueError("nterms must be a positive integer")
    valid = np.isfinite(wmap)
    if mask is not None:
        if mask.shape != wmap.shape:
            raise ValueError("map and mask must have matching shapes")
        valid = valid & mask.astype(bool)
    if pupil is not None:
        valid &= pupil_grid(wmap.shape, pupil)[2]
    elif valid.all():
        valid = valid & Z.unit_disk(wmap.shape[0])[2]
        pupil = {"center_px": [(wmap.shape[0] - 1) / 2] * 2, "radius_px": wmap.shape[0] / 2}
    if not valid.any():
        raise ValueError("map has no valid samples inside the pupil")
    pupil = infer_pupil(valid) if pupil is None else dict(pupil)
    rho, theta, _circle = pupil_grid(wmap.shape, pupil)
    B = Z.basis(scheme, nterms, rho, theta)
    A = B[:, valid].T
    y = wmap[valid]
    coeffs, _, rank, singular_values = np.linalg.lstsq(A, y, rcond=None)
    if rank < nterms:
        raise ValueError(f"Zernike fit is rank deficient ({rank} < {nterms}); reduce terms or provide more pupil coverage")
    reconstructed = A @ coeffs
    residual = y - reconstructed
    pupil.update({"rank": int(rank), "condition_number": float(singular_values[0] / singular_values[-1]),
                  "valid_samples": int(valid.sum()), "valid_coverage_fraction": float(valid.sum() / _circle.sum()),
                  "fit_rms_on_mask": float(np.std(reconstructed)), "fit_terms": nterms})
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
