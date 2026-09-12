import math

import pytest
from _lib import optics


def test_airy_radius_from_fnum_and_na_agree():
    # Smith, Modern Optical Engineering: first dark ring at 1.22 λ F/#
    assert optics.airy_radius(0.55, fnum=4.0) == pytest.approx(1.22 * 0.55 * 4.0)
    assert optics.airy_radius(0.55, na=0.125) == pytest.approx(optics.airy_radius(0.55, fnum=4.0))


def test_resolution_criteria_order():
    lam, na = 0.5, 0.5
    assert optics.sparrow(lam, na) < optics.abbe(lam, na) < optics.rayleigh(lam, na)
    assert optics.rayleigh(lam, na) == pytest.approx(0.61)
    assert optics.abbe(lam, na) == pytest.approx(0.5)


def test_dof_half_range_matches_2_lambda_fnum_squared():
    # ±λ/(2NA²) == ±2λF² for NA = 1/(2F)
    assert optics.dof_half_range(0.55, optics.na_from_fnum(4.0)) == pytest.approx(2 * 0.55 * 16)


def test_dawes_and_rayleigh_angular():
    assert optics.dawes_arcsec(100.0) == pytest.approx(1.16)
    rad = optics.rayleigh_angular_rad(0.55e-3, 100.0)  # both in mm
    assert optics.rad_to_arcsec(rad) == pytest.approx(1.384, rel=1e-3)


def test_mtf_cutoff_and_diffraction_curve():
    assert optics.mtf_cutoff_cyc_per_mm(0.5, 4.0) == pytest.approx(500.0)
    assert optics.mtf_diffraction(0.0) == pytest.approx(1.0)
    assert optics.mtf_diffraction(1.0) == pytest.approx(0.0, abs=1e-12)
    assert optics.mtf_diffraction(0.5) == pytest.approx(2 / math.pi * (math.acos(0.5) - 0.5 * math.sqrt(0.75)))
    assert optics.mtf_diffraction(1.5) == 0.0
