"""Independent scalar pupil-integral fixtures for the September numerical audit."""
import math

import numpy as np
import pytest
import wavefront
from _lib import fourier
from _lib.wfmap import fit_map, load_map


def disk(shape, center, radius, obstruction=0):
    yy, xx = np.indices(shape)
    r2 = (yy - center[0]) ** 2 + (xx - center[1]) ** 2
    return (r2 <= radius**2) & (r2 >= (radius * obstruction)**2)


def test_translation_preserves_psf_scale_energy_and_mtf():
    results = []
    for center in [(64, 64), (24, 64)]:
        mask = disk((128, 128), center, 16)
        results.append(fourier.psf_from_wavefront(np.zeros(mask.shape), mask, pad=4))
    a, b = results
    assert b["pixel_lambda_fnum"] == pytest.approx(32 / 512)
    assert b["fwhm_lambda_fnum"] == pytest.approx(1.029, abs=0.025)
    assert b["encircled_energy_airy"] == pytest.approx(0.8378, abs=0.005)
    np.testing.assert_allclose(a["psf"], b["psf"], atol=1e-15)
    for x, y in zip(fourier.mtf_from_psf(a["psf"], a["pixel_lambda_fnum"]),
                    fourier.mtf_from_psf(b["psf"], b["pixel_lambda_fnum"])):
        np.testing.assert_allclose(x, y, atol=1e-14)


def test_annulus_scale_and_mtf_against_independent_overlap_integral():
    # Incoherent OTF is overlap area / pupil area, evaluated in closed form
    # independently of the production FFT and grid generator.
    n = 128
    mask = disk((n, n), (63.5, 63.5), 64, obstruction=0.5)
    res = fourier.psf_from_wavefront(np.zeros(mask.shape), mask, pad=4)
    assert res["pixel_lambda_fnum"] == pytest.approx(0.25)
    nu, mx, _ = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    # Annulus overlap by inclusion/exclusion of two outer and two inner disks.
    def overlap(a, b, d):
        if d >= a + b:
            return 0.0
        if d <= abs(a - b):
            return math.pi * min(a, b)**2
        return (a*a*math.acos((d*d+a*a-b*b)/(2*d*a))
                + b*b*math.acos((d*d+b*b-a*a)/(2*d*b))
                - 0.5*math.sqrt((-d+a+b)*(d+a-b)*(d-a+b)*(d+a+b)))
    for f in [0.125, 0.25, 0.5, 0.75, 0.875]:
        expected = (overlap(1, 1, 2*f) - 2*overlap(1, 0.5, 2*f)
                    + overlap(0.5, 0.5, 2*f)) / (math.pi * 0.75)
        assert np.interp(f, nu, mx) == pytest.approx(expected, abs=0.006)


def test_explicit_diameter_controls_sampling():
    mask = disk((64, 64), (31.5, 31.5), 16)
    res = fourier.psf_from_wavefront(np.zeros(mask.shape), mask, pad=4, pupil_diameter_px=33)
    assert res["pixel_lambda_fnum"] == pytest.approx(33 / 256)


def test_exact_defocus_strehl_and_approximation_semantics(run_json):
    out = run_json(wavefront.main, ["psf", "--scheme", "noll", "--coeffs", "0,0,0,0.1"])
    phase = 2 * math.pi * math.sqrt(3) * 0.1
    assert out["results"]["strehl"] == pytest.approx((math.sin(phase)/phase)**2, abs=0.002)
    assert not any("check coefficient" in w for w in out["warnings"])
    assert out["results"]["strehl_reference"] == "sampled_peak_same_pupil_zero_phase"
    assert out["results"]["strehl_exponential_estimate"] == pytest.approx(math.exp(-(2*math.pi*0.1)**2))


def test_annular_cli_uses_matched_ideal_and_records_actual_sampling(run_json, tmp_path):
    mask = disk((96, 96), (47.5, 47.5), 48, obstruction=0.5)
    path = tmp_path / "annulus.npy"
    np.save(path, np.where(mask, 0.0, np.nan))
    out = run_json(wavefront.main, ["mtf", "--map", str(path), "--pad", "4",
                                  "--wavelength-um", "0.5", "--fnum", "4", "--freqs", "375,1000"])
    r = out["results"]
    assert r["mtf_at"]["375"]["ideal_x"] == pytest.approx(r["mtf_at"]["375"]["x"], abs=1e-14)
    assert r["mtf_at"]["375"]["x"] > r["mtf_at"]["375"]["diffraction_limit"] + 0.02
    assert r["mtf_at"]["1000"]["x"] == 0.0
    assert not any("exceeds" in w for w in out["warnings"])
    assert out["inputs"]["npix"] == 96
    assert out["inputs"]["pad"] == 4
    assert out["inputs"]["nan_semantics"] == "opaque_aperture"
    assert set(out["inputs"]["pupil"]) == {"center_px", "radius_px"}


@pytest.mark.parametrize("args", [
    ["--npix", "0"], ["--npix", "1"], ["--pad", "0"], ["--pad", "1"],
    ["--wavelength-um", "0.5"], ["--fnum", "4"],
])
def test_invalid_sampling_and_partial_physical_inputs_are_usage_errors(run, args):
    code, _, _ = run(wavefront.main, ["psf", "--scheme", "noll", "--coeffs", "0", *args])
    assert code == 2


def test_conflicting_sources_and_map_npix_are_rejected(run, tmp_path):
    path = tmp_path / "map.npy"
    np.save(path, np.zeros((32, 32)))
    for extra in [["--npix", "64"], ["--scheme", "noll", "--coeffs", "0"]]:
        code, _, _ = run(wavefront.main, ["psf", "--map", str(path), *extra])
        assert code == 2


def test_explicit_map_circle_is_retained(run_json, tmp_path):
    mask = disk((64, 64), (24, 32), 16)
    path = tmp_path / "map.npy"
    np.save(path, np.where(mask, 0, np.nan))
    out = run_json(wavefront.main, ["psf", "--map", str(path), "--pupil-center-px", "24,32",
                                  "--pupil-radius-px", "16", "--pad", "4"])
    assert out["results"]["pixel_lambda_fnum"] == pytest.approx(32 / 256)
    assert out["inputs"]["pupil_geometry_source"] == "explicit"


@pytest.mark.parametrize("bad", ["empty", "nan_inside", "shape", "pad"])
def test_fourier_invalid_arrays_are_rejected(bad):
    mask = disk((16, 16), (7.5, 7.5), 8)
    w = np.zeros(mask.shape)
    pad = 4
    if bad == "empty":
        mask[:] = False
    elif bad == "nan_inside":
        w[8, 8] = np.nan
    elif bad == "shape":
        w = w[:8]
    else:
        pad = 0
    with pytest.raises(ValueError):
        fourier.psf_from_wavefront(w, mask, pad=pad)


def test_peak_at_fft_boundary_retains_encircled_energy_and_width():
    mask = disk((32, 32), (15.5, 15.5), 16)
    _, x = np.indices(mask.shape)
    ideal = fourier.psf_from_wavefront(np.zeros(mask.shape), mask, pad=4)
    tilted = fourier.psf_from_wavefront(-0.5*x, mask, pad=4)
    assert tilted["encircled_energy_airy"] == pytest.approx(ideal["encircled_energy_airy"], abs=1e-13)
    assert tilted["fwhm_lambda_fnum"] == pytest.approx(ideal["fwhm_lambda_fnum"], abs=1e-13)


def test_fit_diagnostics_distinguish_mask_rms_from_disk_coefficients():
    yy, xx = np.indices((64, 64))
    mask = disk((64, 64), (31.5, 31.5), 32, obstruction=0.5)
    # Plane fixtures need no production Zernike generator. Fringe tilts are x/R,y/R.
    values = 0.3 + 0.1*(xx-31.5)/32 - 0.2*(yy-31.5)/32
    coeffs, residual, pupil = fit_map(np.where(mask, values, np.nan), "fringe", 3)
    assert coeffs == pytest.approx([0.3, 0.1, -0.2], abs=1e-14)
    assert residual < 1e-14
    assert pupil["rank"] == 3
    assert pupil["valid_samples"] == int(mask.sum())
    assert pupil["valid_coverage_fraction"] == pytest.approx(mask.sum() / disk(mask.shape, (31.5, 31.5), 32).sum())
    assert pupil["fit_rms_on_mask"] == pytest.approx(np.std(values[mask]), abs=1e-14)
    assert 1 <= pupil["condition_number"] < 3


def test_rank_deficient_fit_is_a_usage_error():
    w = np.full((8, 8), np.nan)
    w[4, 2:6] = 0  # A line cannot determine both tilt components.
    with pytest.raises(ValueError, match="rank"):
        fit_map(w, "fringe", 3)


@pytest.mark.parametrize("pitch", [0, -1, float("nan"), float("inf")])
def test_mtf_rejects_invalid_pitch(pitch):
    with pytest.raises(ValueError):
        fourier.mtf_from_psf(np.ones((8, 8)), pitch)


@pytest.mark.parametrize("values", [np.ones((8, 8), complex)*(1+1j), np.full((8, 8), np.inf)])
def test_map_loader_rejects_complex_and_infinite_data(tmp_path, values):
    path = tmp_path / "invalid.npy"
    np.save(path, values)
    with pytest.raises(ValueError, match="real|infinity"):
        load_map(str(path))


def test_undersampling_warning_does_not_claim_scene_aliasing(run_json):
    out = run_json(wavefront.main, ["sample-check", "--wavelength-um", "0.5", "--fnum", "4", "--pixel-um", "5"])
    assert any("aliasing risk" in w for w in out["warnings"])
    assert not any("the image aliases" in w for w in out["warnings"])


def test_full_finite_map_uses_exact_inscribed_circle_even_on_coarse_grid():
    _, x = np.indices((4, 4))
    coeffs, _, pupil = fit_map(0.1*(x-1.5)/2, "fringe", 3)
    assert pupil["radius_px"] == 2
    assert coeffs[1] == pytest.approx(0.1)
