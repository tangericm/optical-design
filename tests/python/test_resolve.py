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


def test_help_for_every_subcommand(run):
    for sub in ["airy", "rayleigh", "dof", "telescope"]:
        code, out, _ = run(resolve.main, [sub, "--help"])
        assert code == 0 and "example" in out.lower(), sub
