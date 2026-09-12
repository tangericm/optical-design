import pytest
import resolve


def test_airy_json(run_json):
    out = run_json(resolve.main, ["airy", "--wavelength-um", "0.55", "--fnum", "4"])
    assert out["tool"] == "resolve" and out["tier"] == 0
    assert out["results"]["airy_radius_um"] == pytest.approx(2.684)
    assert out["units"]["airy_radius_um"] == "um"
    assert out["results"]["na"] == pytest.approx(0.125)


def test_airy_requires_fnum_or_na(run):
    code, _, err = run(resolve.main, ["airy", "--wavelength-um", "0.55"])
    assert code == 2 and "fnum" in err.lower()


def test_nonpositive_aperture_is_a_usage_error(run):
    code, _, err = run(resolve.main, ["airy", "--wavelength-um", "0.55", "--na", "0"])
    assert code == 2 and "na" in err.lower()


def test_rayleigh_reports_three_criteria(run_json):
    out = run_json(resolve.main, ["rayleigh", "--wavelength-um", "0.5", "--na", "0.5"])
    r = out["results"]
    assert r["rayleigh_um"] == pytest.approx(0.61)
    assert r["abbe_um"] == pytest.approx(0.5)
    assert r["sparrow_um"] == pytest.approx(0.47)


def test_dof_reports_half_and_full_range(run_json):
    out = run_json(resolve.main, ["dof", "--wavelength-um", "0.55", "--fnum", "4"])
    r = out["results"]
    assert r["diffraction_half_range_um"] == pytest.approx(17.6)
    assert r["diffraction_full_range_um"] == pytest.approx(35.2)


def test_dof_with_coc_adds_geometric(run_json):
    out = run_json(resolve.main, ["dof", "--wavelength-um", "0.55", "--fnum", "4", "--coc-um", "10"])
    assert out["results"]["geometric_half_range_um"] == pytest.approx(40.0)


def test_telescope(run_json):
    out = run_json(resolve.main, ["telescope", "--diameter-mm", "100", "--wavelength-um", "0.55"])
    assert out["results"]["dawes_arcsec"] == pytest.approx(1.16)
    assert out["results"]["rayleigh_arcsec"] == pytest.approx(1.384, rel=1e-3)


def test_gaussian_from_waist(run_json):
    out = run_json(resolve.main, ["gaussian", "--wavelength-um", "1.0", "--w0-um", "10", "--z-mm", "0.3141593"])
    r = out["results"]
    assert r["rayleigh_range_mm"] == pytest.approx(0.3141593, rel=1e-5)   # π w0²/λ = π·100/1 µm = 314.16 µm
    assert r["divergence_half_angle_mrad"] == pytest.approx(31.831, rel=1e-4)  # λ/(π w0)
    assert r["beam_radius_at_z_um"] == pytest.approx(10 * 2**0.5, rel=1e-4)


def test_gaussian_focused_by_lens(run_json):
    out = run_json(resolve.main, ["gaussian", "--wavelength-um", "0.85", "--input-w-mm", "1.0", "--focal-mm", "50"])
    # w0 = λ f / (π w_in) = 0.85e-3 mm · 50 / (π · 1) = 13.53 µm
    assert out["results"]["focused_waist_um"] == pytest.approx(13.528, rel=1e-3)
    assert out["results"]["focused_rayleigh_range_mm"] == pytest.approx(0.6764, rel=1e-3)


def test_oct_axial(run_json):
    out = run_json(resolve.main, ["oct-axial", "--center-wavelength-um", "0.84", "--bandwidth-nm", "50"])
    # (2 ln2/π) λ0²/Δλ = 0.4413 · 0.7056 µm² / 0.05 µm = 6.23 µm
    assert out["results"]["axial_resolution_um"] == pytest.approx(6.227, rel=1e-3)
    out_t = run_json(resolve.main, ["oct-axial", "--center-wavelength-um", "0.84", "--bandwidth-nm", "50", "--n", "1.38"])
    assert out_t["results"]["axial_resolution_um"] == pytest.approx(6.227 / 1.38, rel=1e-3)


def test_oct_axial_coherence_length_is_the_gaussian_definition(run_json):
    out = run_json(resolve.main, ["oct-axial", "--center-wavelength-um", "0.84", "--bandwidth-nm", "50", "--n", "1.38"])
    r = out["results"]
    dz = r["axial_resolution_um"]
    # Gaussian-spectrum FWHM coherence length is the axial resolution in the medium;
    # the round-trip OPD that resolution corresponds to is twice it.
    assert r["coherence_length_um"] == pytest.approx(dz * 1.38, rel=1e-12)
    assert r["round_trip_opd_um"] == pytest.approx(2 * dz * 1.38, rel=1e-12)
    assert "Gaussian" in out["method"] and "cavity" in out["method"]


def test_oct_lateral(run_json):
    out = run_json(resolve.main, ["oct-lateral", "--wavelength-um", "0.84", "--focal-mm", "36", "--beam-diameter-mm", "3"])
    # 4 λ f / (π D) = 4·0.84e-3·36/(π·3) mm = 12.83 µm ; b = π Δx²/(2λ) = 0.3079 mm
    assert out["results"]["spot_diameter_um"] == pytest.approx(12.83, rel=1e-3)
    assert out["results"]["confocal_parameter_mm"] == pytest.approx(0.3079, rel=1e-3)


def test_micro_with_pixel(run_json):
    out = run_json(resolve.main, ["micro", "--wavelength-um", "0.52", "--na", "0.8", "--magnification", "40", "--pixel-um", "6.5"])
    r = out["results"]
    assert r["rayleigh_um"] == pytest.approx(0.3965)
    assert r["abbe_um"] == pytest.approx(0.325)
    assert r["axial_um"] == pytest.approx(1.625)
    assert r["nyquist_pixel_um"] == pytest.approx(6.5)         # 40 · 0.325 / 2
    assert r["sampling_ratio"] == pytest.approx(1.0)           # nyquist_pixel / pixel
    assert out["warnings"] == []
    under = run_json(resolve.main, ["micro", "--wavelength-um", "0.52", "--na", "0.8", "--magnification", "20", "--pixel-um", "6.5"])
    assert any("undersampled" in w for w in under["warnings"])


def test_help_for_every_subcommand(run):
    for sub in ["airy", "rayleigh", "dof", "telescope", "gaussian", "oct-axial", "oct-lateral", "micro"]:
        code, out, _ = run(resolve.main, [sub, "--help"])
        assert code == 0 and "example" in out.lower(), sub
