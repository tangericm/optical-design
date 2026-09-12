import numpy as np
import pytest
import wavefront
from _lib import fourier, optics
from _lib import zernike as Z


def test_unaberrated_psf_has_unit_strehl_and_airy_energy():
    rho, _theta, mask = Z.unit_disk(128)
    res = fourier.psf_from_wavefront(np.zeros_like(rho), mask, pad=8)
    assert res["strehl"] == pytest.approx(1.0, abs=1e-6)
    assert res["encircled_energy_airy"] == pytest.approx(0.838, abs=0.01)   # Born & Wolf: 83.8 % inside first dark ring
    assert res["fwhm_lambda_fnum"] == pytest.approx(1.03, abs=0.03)


def test_mtf_matches_diffraction_limited_curve():
    rho, _theta, mask = Z.unit_disk(128)
    res = fourier.psf_from_wavefront(np.zeros_like(rho), mask, pad=8)
    nu, mtf_x, _mtf_y = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    for x, m in zip(nu, mtf_x):
        if x <= 0.9:
            assert m == pytest.approx(optics.mtf_diffraction(x), abs=0.01), x


def test_quarter_wave_defocus_gives_strehl_0_8(run_json):
    # W020 = λ/4 -> Fringe Z4 = 0.125 (balanced) -> Strehl ≈ 0.80 (Rayleigh quarter-wave rule)
    out = run_json(wavefront.main, ["psf", "--scheme", "fringe", "--coeffs", "0,0,0,0.125"])
    assert out["results"]["strehl"] == pytest.approx(0.80, abs=0.02)
    assert out["results"]["rms_waves"] == pytest.approx(0.0722, abs=0.002)


def test_psf_physical_units_and_out_file(run_json, tmp_path):
    out_path = tmp_path / "psf.npy"
    out = run_json(wavefront.main, ["psf", "--scheme", "noll", "--coeffs", "0", "--wavelength-um", "0.55", "--fnum", "4", "--out", str(out_path)])
    assert out["results"]["pixel_um"] == pytest.approx(0.55 * 4 * out["results"]["pixel_lambda_fnum"])
    assert out["results"]["airy_radius_um"] == pytest.approx(2.684)
    assert np.load(out_path).ndim == 2


def test_mtf_reports_requested_frequencies_and_nyquist(run_json):
    out = run_json(wavefront.main, ["mtf", "--scheme", "noll", "--coeffs", "0", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "5", "--freqs", "50,100"])
    r = out["results"]
    assert r["cutoff_cyc_per_mm"] == pytest.approx(500.0)
    assert r["nyquist_cyc_per_mm"] == pytest.approx(100.0)
    assert r["mtf_at"]["100"]["x"] == pytest.approx(optics.mtf_diffraction(0.2), abs=0.01)
    assert r["mtf_at"]["100"]["diffraction_limit"] == pytest.approx(optics.mtf_diffraction(0.2))


def test_sample_check(run_json):
    out = run_json(wavefront.main, ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "1.0"])
    assert out["results"]["q"] == pytest.approx(2.0)
    assert out["warnings"] == []
    under = run_json(wavefront.main, ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "5.0"])
    assert under["results"]["q"] == pytest.approx(0.4) and any("aliases" in w for w in under["warnings"])


def test_map_input_matches_coefficient_input(run_json, tmp_path):
    from _lib.wfmap import coefficients_to_map
    coeffs = [0, 0.05, -0.02, 0.125]          # piston 0, tilt x/y, balanced defocus (fringe)
    wmap, _ = coefficients_to_map("fringe", coeffs, npix=128)
    path = tmp_path / "map.npy"
    np.save(path, wmap)
    by_map = run_json(wavefront.main, ["psf", "--map", str(path)])
    by_coeffs = run_json(wavefront.main, ["psf", "--scheme", "fringe", "--coeffs", "0,0,0,0.125"])
    assert by_map["results"]["rms_waves"] == pytest.approx(by_coeffs["results"]["rms_waves"], abs=2e-3)
    assert by_map["results"]["strehl"] == pytest.approx(by_coeffs["results"]["strehl"], abs=0.02)


def test_map_input_rejects_non_square(run, tmp_path):
    path = tmp_path / "bad.npy"
    np.save(path, np.zeros((64, 32)))
    code, _, err = run(wavefront.main, ["psf", "--map", str(path)])
    assert code == 2 and "square" in err
