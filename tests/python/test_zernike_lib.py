import math

import numpy as np
import pytest
from _lib import zernike as Z


def test_fringe_table_matches_zemax_ordering():
    idx = Z.indices("fringe", 37)
    assert len(idx) == 37
    # Zemax Fringe: Z1 piston, Z2 x-tilt, Z3 y-tilt, Z4 defocus, Z5/6 astig, Z7/8 coma, Z9 spherical,
    # Z10/11 trefoil, Z16 secondary spherical, Z25 (8,0), Z36 (10,0), Z37 (12,0)
    assert idx[0] == (0, 0) and idx[1] == (1, 1) and idx[2] == (1, -1)
    assert idx[3] == (2, 0) and idx[4] == (2, 2) and idx[5] == (2, -2)
    assert idx[6] == (3, 1) and idx[7] == (3, -1) and idx[8] == (4, 0)
    assert idx[9] == (3, 3) and idx[10] == (3, -3)
    assert idx[15] == (6, 0) and idx[24] == (8, 0) and idx[35] == (10, 0) and idx[36] == (12, 0)


def test_noll_table():
    idx = Z.indices("noll", 15)
    # Noll 1976: j=2 x-tilt (cos), j=3 y-tilt (sin), j=5 astig 45° (sin), j=6 astig 0° (cos),
    # j=7 y-coma (sin), j=8 x-coma (cos), j=11 spherical
    assert idx[1] == (1, 1) and idx[2] == (1, -1)
    assert idx[4] == (2, -2) and idx[5] == (2, 2)
    assert idx[6] == (3, -1) and idx[7] == (3, 1)
    assert idx[10] == (4, 0)


def test_ansi_table():
    idx = Z.indices("ansi", 15)
    # OSA/ANSI Z80.28: j = (n(n+2)+m)/2, m ascending: j=3 (2,-2), j=4 (2,0), j=5 (2,2), j=12 (4,0)
    assert idx[0] == (0, 0) and idx[3] == (2, -2) and idx[4] == (2, 0) and idx[5] == (2, 2) and idx[12] == (4, 0)


def test_radial_polynomials_known_values():
    rho = np.array([0.0, 0.5, 1.0])
    np.testing.assert_allclose(Z.radial(2, 0, rho), 2 * rho**2 - 1)
    np.testing.assert_allclose(Z.radial(4, 0, rho), 6 * rho**4 - 6 * rho**2 + 1)
    np.testing.assert_allclose(Z.radial(3, 1, rho), 3 * rho**3 - 2 * rho)


def test_normalized_terms_have_unit_rms_over_disk():
    rho, theta, mask = Z.unit_disk(512)
    for scheme in ("noll", "ansi"):
        for n, m in Z.indices(scheme, 15)[1:]:
            t = Z.term(scheme, n, m, rho, theta)[mask]
            assert math.sqrt(np.mean(t**2)) == pytest.approx(1.0, abs=0.01), (scheme, n, m)


def test_fringe_terms_are_unnormalized():
    rho, theta, mask = Z.unit_disk(512)
    t = Z.term("fringe", 2, 0, rho, theta)[mask]
    assert math.sqrt(np.mean(t**2)) == pytest.approx(1 / math.sqrt(3), abs=0.01)


def test_names():
    assert Z.name(4, 0) == "spherical" and Z.name(2, -2) == "astigmatism 45deg" and Z.name(3, 1) == "coma x"
