"""FFT-based PSF/MTF from a pupil wavefront. Units: PSF sample pitch in λF#, frequency in ν/ν_cutoff."""
from __future__ import annotations

import numpy as np

from _lib.wfmap import infer_pupil


def _peak_and_center(psf: np.ndarray) -> tuple[float, tuple[int, int]]:
    idx = np.unravel_index(int(np.argmax(psf)), psf.shape)
    return float(psf[idx]), (int(idx[0]), int(idx[1]))


def psf_from_wavefront(wmap_waves: np.ndarray, mask: np.ndarray, pad: int = 8,
                       *, pupil_diameter_px: float | None = None) -> dict:
    """Uniform-amplitude scalar pupil; mask=False means opaque, not missing data.

    Diameter is the normalization diameter D in input sample intervals, so image
    pitch is D / FFT-size in lambda*F#. Legacy callers infer a circular outer rim;
    asymmetric or clipped apertures require an explicitly supplied diameter.
    """
    wmap_waves, mask = np.asarray(wmap_waves), np.asarray(mask)
    if (mask.ndim != 2 or mask.shape[0] != mask.shape[1] or mask.shape[0] < 2
            or wmap_waves.shape != mask.shape):
        raise ValueError("wavefront and mask must be matching square arrays of size >= 2")
    if mask.dtype != bool:
        raise ValueError("pupil mask must be boolean (uniform amplitude)")
    if not mask.any() or not np.isfinite(wmap_waves[mask]).all() or np.iscomplexobj(wmap_waves):
        raise ValueError("pupil must contain finite real wavefront samples")
    if isinstance(pad, bool) or not isinstance(pad, (int, np.integer)) or pad < 2:
        raise ValueError("pad must be an integer >= 2 to avoid circular pupil autocorrelation")
    npix = mask.shape[0]
    dpx = 2 * infer_pupil(mask)["radius_px"] if pupil_diameter_px is None else float(pupil_diameter_px)
    if not np.isfinite(dpx) or dpx <= 0:
        raise ValueError("pupil diameter in sample intervals must be finite and positive")
    M = npix * pad
    w = np.where(mask, wmap_waves, 0.0)
    field = mask * np.exp(2j * np.pi * w)
    ref = mask.astype(complex)

    def _psf(f):
        F = np.fft.fftshift(np.fft.fft2(f, s=(M, M)))
        return np.abs(F) ** 2

    psf, psf_ref = _psf(field), _psf(ref)
    peak, center = _peak_and_center(psf)
    peak_ref, _ = _peak_and_center(psf_ref)
    strehl = peak / peak_ref
    psf_n = psf / psf.sum()
    psf_ref_n = psf_ref / psf_ref.sum()
    pitch = dpx / M  # PSF sample pitch in units of λF#

    yy, xx = np.indices(psf.shape)
    dy = (yy - center[0] + M // 2) % M - M // 2
    dx = (xx - center[1] + M // 2) % M - M // 2
    r = np.hypot(dy, dx) * pitch
    ee_airy = float(psf_n[r <= 1.22].sum())

    # Recenter the periodic FFT image before finding the peak's width. A tilted
    # pupil can place its peak at an array boundary.
    row = np.roll(psf[center[0]], M // 2 - center[1])
    half = peak / 2
    left = M // 2
    while left > 0 and row[left] > half:
        left -= 1
    right = M // 2
    while right < M - 1 and row[right] > half:
        right += 1
    # linear interpolation at the half-maximum crossings; guard degenerate/flat rows
    denom_l = row[left + 1] - row[left]
    xl = left + (half - row[left]) / denom_l if denom_l != 0 else float(left)
    denom_r = row[right - 1] - row[right]
    xr = right - (half - row[right]) / denom_r if denom_r != 0 else float(right)
    fwhm = (xr - xl) * pitch
    return {"psf": psf_n, "ideal_psf": psf_ref_n, "strehl": float(strehl), "pixel_lambda_fnum": float(pitch),
            "fwhm_lambda_fnum": float(fwhm), "encircled_energy_airy": ee_airy, "center": center}


def mtf_from_psf(psf: np.ndarray, pixel_lambda_fnum: float):
    psf = np.asarray(psf)
    if (psf.ndim != 2 or psf.shape[0] != psf.shape[1] or psf.shape[0] < 2
            or not np.isfinite(psf).all() or np.iscomplexobj(psf)
            or np.any(psf < 0) or psf.sum() <= 0):
        raise ValueError("PSF must be a finite nonnegative square array with positive energy")
    if not np.isfinite(pixel_lambda_fnum) or pixel_lambda_fnum <= 0:
        raise ValueError("PSF sample pitch must be finite and positive")
    otf = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(psf)))
    mtf = np.abs(otf) / np.abs(otf).max()
    M = psf.shape[0]
    c = M // 2
    # frequency step per bin = 1/(M·pitch) in units of 1/(λF#) == ν_cutoff
    step = 1.0 / (M * pixel_lambda_fnum)
    nu = np.arange(0, M - c) * step
    keep = nu <= 1.0
    return nu[keep], mtf[c, c:][keep], mtf[c:, c][keep]
