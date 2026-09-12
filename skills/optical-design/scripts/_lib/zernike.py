"""Zernike polynomials in three index schemes.

Schemes:
- fringe: Zemax "Zernike Fringe" / University of Arizona ordering, 1-based, 37 terms, unnormalized
  (coefficient = peak value of the term at the pupil edge). Order: by n+|m| ascending, then |m|
  descending, cosine before sine; term 37 is (12,0). Source: Wyant & Creath 1992, Table 2; Zemax manual.
- noll: Noll 1976 (JOSA 66, 207), 1-based, RMS-normalized; within a radial order sorted by |m|,
  even j = cosine (m>0), odd j = sine (m<0). Zemax "Zernike Standard" uses this scheme.
- ansi: ANSI Z80.28 / OSA, 0-based, RMS-normalized, j = (n(n+2)+m)/2, m ascending (sine first).
Sign convention in all three: m >= 0 -> cos(mθ), m < 0 -> sin(|m|θ), θ measured from +x toward +y.
"""
from __future__ import annotations

from math import factorial, sqrt

import numpy as np

SCHEMES = ("fringe", "noll", "ansi")


def first_index(scheme: str) -> int:
    return 0 if scheme == "ansi" else 1


def _fringe_indices() -> list[tuple[int, int]]:
    pairs = [(n, m) for n in range(11) for m in range(n % 2, n + 1, 2) if n + m <= 10]
    pairs.sort(key=lambda p: (p[0] + p[1], -p[1]))
    out: list[tuple[int, int]] = []
    for n, m in pairs:
        if m == 0:
            out.append((n, 0))
        else:
            out.append((n, m))
            out.append((n, -m))
    out.append((12, 0))
    return out


def _noll_indices(nterms: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    n = 0
    while len(out) < nterms:
        for m_abs in range(n % 2, n + 1, 2):
            if m_abs == 0:
                out.append((n, 0))
            else:
                j_first = len(out) + 1
                if j_first % 2 == 0:
                    out.append((n, m_abs)); out.append((n, -m_abs))
                else:
                    out.append((n, -m_abs)); out.append((n, m_abs))
        n += 1
    return out[:nterms]


def _ansi_indices(nterms: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    n = 0
    while len(out) < nterms:
        for m in range(-n, n + 1, 2):
            out.append((n, m))
        n += 1
    return out[:nterms]


def indices(scheme: str, nterms: int) -> list[tuple[int, int]]:
    if scheme == "fringe":
        if nterms > 37:
            raise ValueError("fringe scheme has 37 terms")
        return _fringe_indices()[:nterms]
    if scheme == "noll":
        return _noll_indices(nterms)
    if scheme == "ansi":
        return _ansi_indices(nterms)
    raise ValueError(f"unknown scheme {scheme!r}; choose from {SCHEMES}")


def norm(scheme: str, n: int, m: int) -> float:
    if scheme == "fringe":
        return 1.0
    return sqrt(n + 1.0) if m == 0 else sqrt(2.0 * (n + 1.0))


def radial(n: int, m_abs: int, rho: np.ndarray) -> np.ndarray:
    rho = np.asarray(rho, dtype=float)
    out = np.zeros_like(rho)
    for k in range((n - m_abs) // 2 + 1):
        c = ((-1) ** k * factorial(n - k)
             / (factorial(k) * factorial((n + m_abs) // 2 - k) * factorial((n - m_abs) // 2 - k)))
        out += c * rho ** (n - 2 * k)
    return out


def term(scheme: str, n: int, m: int, rho: np.ndarray, theta: np.ndarray) -> np.ndarray:
    ang = np.cos(m * theta) if m >= 0 else np.sin(-m * theta)
    return norm(scheme, n, m) * radial(n, abs(m), rho) * ang


def basis(scheme: str, nterms: int, rho: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return np.stack([term(scheme, n, m, rho, theta) for n, m in indices(scheme, nterms)])


_NAMES = {
    (0, 0): "piston", (1, 1): "tilt x", (1, -1): "tilt y", (2, 0): "defocus",
    (2, 2): "astigmatism 0deg", (2, -2): "astigmatism 45deg", (3, 1): "coma x", (3, -1): "coma y",
    (3, 3): "trefoil x", (3, -3): "trefoil y", (4, 0): "spherical",
    (4, 2): "secondary astigmatism 0deg", (4, -2): "secondary astigmatism 45deg",
    (4, 4): "tetrafoil x", (4, -4): "tetrafoil y", (5, 1): "secondary coma x", (5, -1): "secondary coma y",
    (6, 0): "secondary spherical", (8, 0): "tertiary spherical",
}


def name(n: int, m: int) -> str:
    return _NAMES.get((n, m), f"Z({n},{m})")


def unit_disk(npix: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Square grid of npix² with the unit circle inscribed; returns rho, theta, boolean mask."""
    x = (np.arange(npix) - (npix - 1) / 2) / (npix / 2)
    xx, yy = np.meshgrid(x, x)
    rho = np.hypot(xx, yy)
    theta = np.arctan2(yy, xx)
    return rho, theta, rho <= 1.0
