import math

import numpy as np
import pytest
import zernike
from _lib.wfmap import coefficients_to_map


def test_convert_fringe_defocus_to_noll(run_json):
    # Fringe Z4 = 0.25 waves peak defocus -> Noll j=4 coefficient 0.25/sqrt(3) (RMS-normalized)
    out = run_json(zernike.main, ["convert", "--from", "fringe", "--to", "noll", "--coeffs", "0,0,0,0.25"])
    c = out["results"]["coefficients"]
    assert c[3] == pytest.approx(0.25 / math.sqrt(3))
    assert out["results"]["terms"][3]["name"] == "defocus"


def test_convert_noll_to_ansi_keeps_wavefront(run_json):
    out = run_json(zernike.main, ["convert", "--from", "noll", "--to", "ansi", "--coeffs", "0,0,0,0,0.3,0.1"])
    c = out["results"]["coefficients"]  # ansi j=3 is (2,-2), j=5 is (2,2)
    assert c[3] == pytest.approx(0.3) and c[5] == pytest.approx(0.1)


def test_convert_default_nterms_covers_all_source_terms(run_json):
    # only Fringe Z9 (spherical, (4,0)) is nonzero; Noll needs 11 terms to reach (4,0)
    out = run_json(zernike.main, ["convert", "--from", "fringe", "--to", "noll", "--coeffs", "0,0,0,0,0,0,0,0,0.1"])
    c = out["results"]["coefficients"]
    assert len(c) == 11 and c[10] == pytest.approx(0.1 / math.sqrt(5))
    assert out["warnings"] == []


def test_convert_warns_on_unmapped_terms(run_json):
    out = run_json(zernike.main, ["convert", "--from", "fringe", "--to", "noll", "--nterms", "4", "--coeffs", "0,0,0,0,0,0,0,0,0.1"])
    assert any("dropped" in w for w in out["warnings"])


def test_rms_normalized_scheme_is_root_sum_square(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", "0,0,0,0.3,0.4"])
    assert out["results"]["rms_waves"] == pytest.approx(0.5)


def test_rms_fringe_divides_by_norm(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "fringe", "--coeffs", "0,0,0,0.25"])
    assert out["results"]["rms_waves"] == pytest.approx(0.25 / math.sqrt(3), rel=1e-2)
    assert out["results"]["pv_waves"] == pytest.approx(0.5, rel=2e-2)


def test_rms_excludes_piston_and_tilt_by_default(run_json):
    out = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", "5,1,1,0.3"])
    assert out["results"]["rms_waves"] == pytest.approx(0.3)


def test_strehl_from_rms(run_json):
    out = run_json(zernike.main, ["strehl", "--rms-waves", "0.0714"])   # λ/14
    r = out["results"]
    assert r["strehl_marechal"] == pytest.approx(0.80, abs=0.01)
    assert r["strehl_extended"] == pytest.approx(0.818, abs=0.01)
    assert out["warnings"] == []
    big = run_json(zernike.main, ["strehl", "--rms-waves", "0.3"])
    assert any("valid" in w for w in big["warnings"])
    # Maréchal goes negative past ~0.16 waves; report nothing rather than a wrong number
    assert big["results"]["strehl_marechal"] is None
    assert big["results"]["strehl_extended"] == pytest.approx(math.exp(-(2 * math.pi * 0.3) ** 2))


def test_strehl_from_coeffs(run_json):
    out = run_json(zernike.main, ["strehl", "--scheme", "fringe", "--coeffs", "0,0,0,0.125"])
    assert out["results"]["strehl_marechal"] == pytest.approx(0.794, abs=0.01)


def test_seidel_from_fringe_spherical_and_coma(run_json):
    # Wyant & Creath 1992, Table 3 (0-based Z index there; 1-based here):
    # spherical W040 = 6·Z9 ; coma W131 = 3·√(Z7²+Z8²) ; astig W222 = 2·√(Z5²+Z6²)
    coeffs = [0, 0, 0, 0, 0.05, 0, 0.1, 0, 0.2]
    out = run_json(zernike.main, ["seidel-from-zernike", "--coeffs", ",".join(map(str, coeffs))])
    r = out["results"]
    assert r["spherical_w040_waves"] == pytest.approx(1.2)
    assert r["coma_w131_waves"] == pytest.approx(0.3)
    assert r["coma_angle_deg"] == pytest.approx(0.0)
    assert r["astigmatism_w222_waves"] == pytest.approx(0.1)


def test_seidel_requires_nine_fringe_terms(run):
    code, _, err = run(zernike.main, ["seidel-from-zernike", "--coeffs", "0,0,0,0.1"])
    assert code == 2 and "9" in err


def test_fit_recovers_known_coefficients(run_json, tmp_path):
    truth = [0, 0, 0, 0.2, 0.05, -0.03, 0, 0, 0.1]
    wmap, _ = coefficients_to_map("fringe", truth, npix=128)
    path = tmp_path / "map.npy"
    np.save(path, wmap)
    out = run_json(zernike.main, ["fit", "--map", str(path), "--scheme", "fringe", "--nterms", "9"])
    np.testing.assert_allclose(out["results"]["coefficients"], truth, atol=1e-6)
    assert out["results"]["residual_rms_waves"] == pytest.approx(0.0, abs=1e-6)
    assert out["results"]["normalization_radius_px"] == pytest.approx(64.0)   # inscribed in 128 px


def test_fit_normalizes_to_the_pupil_not_the_canvas(run_json, tmp_path):
    # 0.1 waves of Fringe Z9 on a 128-px pupil centred in a 256² NaN canvas. Normalizing to
    # the inscribed circle of the canvas would scale Z9 by (R_grid/R_pupil)^4 with zero residual.
    truth = [0.0] * 8 + [0.1]
    pupil_map, _ = coefficients_to_map("fringe", truth, npix=128)
    canvas = np.full((256, 256), np.nan)
    canvas[64:192, 64:192] = pupil_map
    path = tmp_path / "padded.npy"
    np.save(path, canvas)
    out = run_json(zernike.main, ["fit", "--map", str(path), "--scheme", "fringe", "--nterms", "9"])
    r = out["results"]
    assert r["coefficients"][8] == pytest.approx(0.1, abs=1e-3)
    assert r["normalization_radius_px"] == pytest.approx(64.0, abs=1.0)
    assert r["pupil_center_px"] == pytest.approx([127.5, 127.5], abs=0.5)


def test_fit_accepts_csv_with_nan_outside_pupil(run_json, tmp_path):
    truth = [0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1]
    wmap, _ = coefficients_to_map("noll", truth + [0, 0], npix=64)
    path = tmp_path / "map.csv"
    np.savetxt(path, wmap, delimiter=",")
    out = run_json(zernike.main, ["fit", "--map", str(path), "--scheme", "noll", "--nterms", "11"])
    assert out["results"]["coefficients"][8] == pytest.approx(0.1, abs=1e-6)


def test_strehl_without_scheme_is_a_usage_error(run):
    code, _, err = run(zernike.main, ["strehl", "--coeffs", "0,0,0,0.1"])
    assert code == 2 and "scheme" in err.lower()


def test_convert_beyond_the_fringe_scheme_is_a_usage_error(run):
    code, _, err = run(zernike.main, ["convert", "--from", "noll", "--to", "fringe", "--nterms", "40", "--coeffs", "0"])
    assert code == 2 and "37" in err


def test_fit_missing_map_exits_4(run, tmp_path):
    code, _, err = run(zernike.main, ["fit", "--map", str(tmp_path / "nosuch.npy")])
    assert code == 4 and err.startswith("error:")


def test_fit_non_square_map_is_a_usage_error(run, tmp_path):
    path = tmp_path / "bad.npy"
    np.save(path, np.zeros((64, 32)))
    code, _, err = run(zernike.main, ["fit", "--map", str(path)])
    assert code == 2 and "square" in err


def test_per_term_rms_marks_excluded_terms_and_sums_to_rms(run_json):
    coeffs = "0.4,0.2,-0.1,0.25,0,0,0,0,0.1"
    out = run_json(zernike.main, ["rms", "--scheme", "fringe", "--coeffs", coeffs])
    r = out["results"]
    per = r["per_term_rms"]
    assert [e["name"] for e in per if e["excluded"]] == ["piston", "tilt x", "tilt y"]
    assert next(e for e in per if e["name"] == "piston")["rms"] == 0.0
    rss = math.sqrt(sum(e["rms"] ** 2 for e in per if not e["excluded"]))
    assert rss == pytest.approx(r["rms_waves"], rel=1e-6)

    kept = run_json(zernike.main, ["rms", "--scheme", "fringe", "--coeffs", coeffs, "--include-low-order"])
    per = kept["results"]["per_term_rms"]
    assert not any(e["excluded"] for e in per)
    rss = math.sqrt(sum(e["rms"] ** 2 for e in per))
    assert rss == pytest.approx(kept["results"]["rms_waves"], rel=1e-6)
