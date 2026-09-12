"""Closed-form optics formulas. Pure functions; units documented per function.

Sources:
- Smith, W. J., Modern Optical Engineering, 4th ed. (Airy disk, DOF, MTF cutoff)
- Hecht, Optics, 5th ed. (Rayleigh, Sparrow, Abbe)
- Dawes, W. R. (1867) empirical double-star limit
- Saleh & Teich, Fundamentals of Photonics (Gaussian beams)
- Drexler & Fujimoto (eds.), Optical Coherence Tomography (OCT resolution)
"""
from __future__ import annotations

import math

ARCSEC_PER_RAD = 206264.80624709636


def na_from_fnum(fnum: float) -> float:
    """Paraxial NA = 1/(2 F#)."""
    return 1.0 / (2.0 * fnum)


def fnum_from_na(na: float) -> float:
    return 1.0 / (2.0 * na)


def airy_radius(wavelength: float, *, fnum: float | None = None, na: float | None = None) -> float:
    """Radius of first dark ring: 1.22 λ F# == 0.61 λ / NA. Same unit as wavelength."""
    if fnum is None and na is None:
        raise ValueError("fnum or na required")
    if fnum is None:
        fnum = fnum_from_na(na)  # type: ignore[arg-type]
    return 1.22 * wavelength * fnum


def airy_fwhm(wavelength: float, na: float) -> float:
    """FWHM of Airy pattern ≈ 0.51 λ/NA (≈ 1.03 λ F#)."""
    return 0.51 * wavelength / na


def rayleigh(wavelength: float, na: float) -> float:
    return 0.61 * wavelength / na


def sparrow(wavelength: float, na: float) -> float:
    """Sparrow limit for incoherent circular pupil, 0.47 λ/NA (Hecht)."""
    return 0.47 * wavelength / na


def abbe(wavelength: float, na: float) -> float:
    return wavelength / (2.0 * na)


def rayleigh_angular_rad(wavelength: float, diameter: float) -> float:
    """1.22 λ/D; wavelength and diameter in the same unit."""
    return 1.22 * wavelength / diameter


def rad_to_arcsec(rad: float) -> float:
    return rad * ARCSEC_PER_RAD


def dawes_arcsec(diameter_mm: float) -> float:
    """Dawes empirical limit, 116/D[mm] arcsec."""
    return 116.0 / diameter_mm


def dof_half_range(wavelength: float, na: float) -> float:
    """Rayleigh quarter-wave depth of focus, half range ±λ/(2 NA²) == ±2 λ F#² (Smith)."""
    return wavelength / (2.0 * na * na)


def dof_geometric_half(coc: float, fnum: float) -> float:
    """Geometric half depth of focus for an allowed blur circle: ±c F#."""
    return coc * fnum


def mtf_cutoff_cyc_per_mm(wavelength_um: float, fnum: float) -> float:
    """Incoherent cutoff 1/(λ F#) in cycles/mm with λ in µm."""
    return 1000.0 / (wavelength_um * fnum)


def mtf_diffraction(nu_over_cutoff: float) -> float:
    """Diffraction-limited incoherent MTF of a circular pupil (Smith eq. 11.4)."""
    x = nu_over_cutoff
    if x <= 0.0:
        return 1.0
    if x >= 1.0:
        return 0.0
    return (2.0 / math.pi) * (math.acos(x) - x * math.sqrt(1.0 - x * x))


def sampling_q(wavelength_um: float, fnum: float, pixel_um: float) -> float:
    """Q = λ F# / p. Q = 2 is Nyquist-sampled at the diffraction cutoff."""
    return wavelength_um * fnum / pixel_um


# Gaussian beams (1/e² radius w, M² beam quality)
def rayleigh_range(w0: float, wavelength: float, m2: float = 1.0) -> float:
    return math.pi * w0 * w0 / (m2 * wavelength)


def divergence_half_angle_rad(w0: float, wavelength: float, m2: float = 1.0) -> float:
    return m2 * wavelength / (math.pi * w0)


def beam_radius(z: float, w0: float, zr: float) -> float:
    return w0 * math.sqrt(1.0 + (z / zr) ** 2)


def focused_waist(wavelength: float, focal: float, w_in: float, m2: float = 1.0) -> float:
    """Waist after a lens for a collimated input beam of 1/e² radius w_in: M² λ f / (π w_in)."""
    return m2 * wavelength * focal / (math.pi * w_in)


# OCT (Drexler & Fujimoto ch. 2)
def oct_axial_resolution(center_wavelength: float, bandwidth_fwhm: float, n: float = 1.0) -> float:
    """Δz = (2 ln 2 / π) λ0² / Δλ / n for a Gaussian spectrum."""
    return (2.0 * math.log(2.0) / math.pi) * center_wavelength**2 / bandwidth_fwhm / n


def oct_lateral_resolution(wavelength: float, focal: float, beam_diameter: float) -> float:
    """1/e² focal spot diameter Δx = 4 λ f / (π D) for 1/e² beam diameter D at the lens."""
    return 4.0 * wavelength * focal / (math.pi * beam_diameter)


def confocal_parameter(spot_diameter: float, wavelength: float) -> float:
    """b = 2 z_R = π Δx² / (2 λ)."""
    return math.pi * spot_diameter**2 / (2.0 * wavelength)


# Microscopy
def micro_axial_resolution(wavelength: float, na: float, n: float = 1.0) -> float:
    """Axial (widefield) resolution ≈ 2 λ n / NA²."""
    return 2.0 * wavelength * n / (na * na)


def nyquist_pixel_at_camera(resolution_object: float, magnification: float) -> float:
    """Largest camera pixel that samples `resolution_object` at Nyquist: M·d/2."""
    return magnification * resolution_object / 2.0
