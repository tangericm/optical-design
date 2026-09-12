"""FFT-based PSF/MTF from a pupil wavefront. Units: PSF sample pitch in λF#, frequency in ν/ν_cutoff."""
from __future__ import annotations

import numpy as np


def _peak_and_center(psf: np.ndarray) -> tuple[float, tuple[int, int]]:
    idx = np.unravel_index(int(np.argmax(psf)), psf.shape)
    return float(psf[idx]), (int(idx[0]), int(idx[1]))


def psf_from_wavefront(wmap_waves: np.ndarray, mask: np.ndarray, pad: int = 8) -> dict:
    npix = mask.shape[0]
    dpx = int(np.count_nonzero(mask[npix // 2]))  # pupil diameter in samples along the center row
    M = npix * pad
    w = np.where(mask, np.nan_to_num(wmap_waves), 0.0)
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
    pitch = dpx / M  # PSF sample pitch in units of λF#

    yy, xx = np.indices(psf.shape)
    r = np.hypot(yy - center[0], xx - center[1]) * pitch
    ee_airy = float(psf_n[r <= 1.22].sum())

    row = psf[center[0]]
    half = peak / 2
    left = center[1]
    while left > 0 and row[left] > half:
        left -= 1
    right = center[1]
    while right < M - 1 and row[right] > half:
        right += 1
    # linear interpolation at the half-maximum crossings; guard degenerate/flat rows
    denom_l = row[left + 1] - row[left]
    xl = left + (half - row[left]) / denom_l if denom_l != 0 else float(left)
    denom_r = row[right - 1] - row[right]
    xr = right - (half - row[right]) / denom_r if denom_r != 0 else float(right)
    fwhm = (xr - xl) * pitch
    return {"psf": psf_n, "strehl": float(strehl), "pixel_lambda_fnum": float(pitch),
            "fwhm_lambda_fnum": float(fwhm), "encircled_energy_airy": ee_airy, "center": center}


def mtf_from_psf(psf: np.ndarray, pixel_lambda_fnum: float):
    otf = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(psf)))
    mtf = np.abs(otf) / np.abs(otf).max()
    M = psf.shape[0]
    c = M // 2
    # frequency step per bin = 1/(M·pitch) in units of 1/(λF#) == ν_cutoff
    step = 1.0 / (M * pixel_lambda_fnum)
    nu = np.arange(0, M - c) * step
    keep = nu <= 1.0
    return nu[keep], mtf[c, c:][keep], mtf[c:, c][keep]
