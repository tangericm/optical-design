"""Public boundary regressions; optical expectations are independently specified."""
import hashlib
import platform

import interfero
import numpy as np
import pytest
import resolve
import zernike


@pytest.mark.parametrize("value", ["-0.1", "nan", "inf", "-inf"])
def test_rms_rejects_impossible_values(run, value):
    code, out, err = run(zernike.main, ["strehl", f"--rms-waves={value}", "--json"])
    assert code == 2 and not out and "Traceback" not in err


@pytest.mark.parametrize("main,argv", [
    (resolve.main, ["airy", "--wavelength-um", "inf", "--fnum", "4"]),
    (resolve.main, ["airy", "--wavelength-um", ".5", "--fnum", "4", "--na", ".5"]),
    (resolve.main, ["airy", "--wavelength-um", ".5", "--na", "1.1"]),
    (resolve.main, ["gaussian", "--wavelength-um", "1", "--w0-um", "10", "--m2", "0"]),
    (resolve.main, ["gaussian", "--wavelength-um", "1", "--w0-um", "10", "--m2", ".5"]),
    (resolve.main, ["gaussian", "--wavelength-um", "1", "--w0-um", "10", "--z-mm", "nan"]),
    (resolve.main, ["oct-axial", "--center-wavelength-um", "1", "--bandwidth-nm", "10", "--n", "0"]),
    (resolve.main, ["micro", "--wavelength-um", ".5", "--na", "1.5", "--n", "1.3"]),
    (resolve.main, ["micro", "--wavelength-um", ".5", "--na", ".5", "--magnification", "0"]),
    (resolve.main, ["dof", "--wavelength-um", ".5", "--fnum", "4", "--coc-um", "-1"]),
    (zernike.main, ["convert", "--from", "noll", "--to", "noll", "--coeffs", "0", "--nterms", "0"]),
    (zernike.main, ["rms", "--scheme", "noll", "--coeffs", "0,0,0,nan"]),
    (zernike.main, ["convert", "--from", "noll", "--to", "noll", "--coeffs", ""]),
    (interfero.main, ["cavity", "--gap-mm", "1", "--wavelength-um", ".5", "--linewidth-nm", "0"]),
    (interfero.main, ["cavity", "--gap-mm", "1", "--wavelength-um", ".5", "--tilt-arcsec", "inf"]),
])
def test_invalid_physical_parameters_are_usage_errors(run, main, argv):
    code, out, err = run(main, [*argv, "--json"])
    assert code == 2 and not out and "Traceback" not in err


@pytest.mark.parametrize("option,value", [("--passes", "0"), ("--passes", "-1"), ("--nterms", "-1")])
def test_invalid_measurement_counts(run, tmp_path, option, value):
    path = tmp_path / "phase.npy"
    np.save(path, np.zeros((16, 16)))
    code, out, _err = run(interfero.main, ["fringe-to-wfe", "--phase", str(path), option, value, "--json"])
    assert code == 2 and not out


def test_zero_tilt_is_no_finite_fringe_spacing(run_json):
    r = run_json(interfero.main, ["cavity", "--gap-mm", "1", "--wavelength-um", ".5", "--tilt-arcsec", "0"])["results"]
    assert r["fringe_spacing_mm"] is None
    assert r["fringes_across_100mm"] == 0
    assert r["tilt_fringe_status"] == "no_tilt_fringes"


def test_signed_tilt_preserves_positive_spacing(run_json):
    r = run_json(interfero.main, ["cavity", "--gap-mm", "1", "--wavelength-um", ".6328", "--tilt-arcsec=-10"])["results"]
    assert r["fringe_spacing_mm"] == pytest.approx(6.527, rel=1e-3)


@pytest.mark.parametrize("measurement,extra,factor", [
    ("measured-opd", [], 1.0),
    ("single-pass", ["--passes", "2"], 2.0),
    ("surface-height", ["--incidence-deg", "60"], 1.0),
])
def test_measurement_quantity_and_raw_opd(run_json, tmp_path, measurement, extra, factor):
    # A two-level 0/one-wave OPD fixture: PV=1 wave, RMS=0.5 wave.
    phase = np.zeros((16, 16))
    phase[:, 8:] = 2 * np.pi
    path, output = tmp_path / "phase.npy", tmp_path / "converted.npy"
    np.save(path, phase)
    r = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(path), "--measurement", measurement,
                                "--nterms", "0", "--out", str(output), *extra])["results"]
    assert r["measurement"] == measurement
    assert r["measured_opd_pv_waves"] == pytest.approx(1)
    assert r["measured_opd_rms_waves"] == pytest.approx(.5)
    assert r["pv_waves"] == pytest.approx(1 / factor)
    assert r["rms_map_waves"] == pytest.approx(.5 / factor)
    assert np.load(output)[8, 12] == pytest.approx(1 / factor)


def test_legacy_measurement_is_explicit_and_retains_division_by_two(run_json, tmp_path):
    path = tmp_path / "phase.npy"
    np.save(path, np.tile(np.arange(16), (16, 1)) * 2 * np.pi)
    out = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(path), "--nterms", "0"])
    assert out["results"]["measurement"] == "single-pass"
    assert out["results"]["opd_conversion_divisor"] == 2
    assert any("assum" in w.lower() for w in out["warnings"])


def test_provenance_tracks_actual_environment_and_input_content(run_json, tmp_path):
    path = tmp_path / "coeffs.json"
    path.write_text("[0,0,0,0.1]", encoding="utf-8")
    out = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", str(path)])
    p = out["provenance"]
    assert p["python_version"] == platform.python_version()
    assert p["dependencies"]["numpy"] == np.__version__
    assert p["input_files"]["coeffs"]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    path.write_text("[0,0,0,0.2]", encoding="utf-8")
    changed = run_json(zernike.main, ["rms", "--scheme", "noll", "--coeffs", str(path)])
    assert changed["provenance"]["input_files"]["coeffs"]["sha256"] != p["input_files"]["coeffs"]["sha256"]


@pytest.mark.parametrize("data", [np.zeros((4,)), np.zeros((4, 8)), np.zeros((4, 0, 8)),
                                  np.full((4, 8, 8), np.inf), np.zeros((4, 8, 8), dtype=complex)])
def test_psi_rejects_invalid_frame_arrays_before_writing(run, tmp_path, data):
    source, output = tmp_path / "frames.npy", tmp_path / "phase.npy"
    np.save(source, data)
    code, text, _err = run(interfero.main, ["psi", "--frames", str(source), "--out", str(output), "--json"])
    assert code == 2 and not text and not output.exists()


@pytest.mark.parametrize("extra", [["--measurement", "measured-opd", "--passes", "2"],
                                  ["--measurement", "surface-height", "--incidence-deg", "90"],
                                  ["--measurement", "single-pass", "--incidence-deg", "30"]])
def test_measurement_rejects_conflicting_geometry(run, tmp_path, extra):
    source, output = tmp_path / "phase.npy", tmp_path / "out.npy"
    np.save(source, np.zeros((8, 8)))
    code, text, _err = run(interfero.main, ["fringe-to-wfe", "--phase", str(source), "--out", str(output), *extra, "--json"])
    assert code == 2 and not text and not output.exists()


@pytest.mark.parametrize("serialized", ['[null]', '[[1]]', '[true]', '{"coefficient": 0.1}'])
def test_invalid_coefficient_file_values_are_usage_errors(run, tmp_path, serialized):
    path = tmp_path / "coeffs.json"
    path.write_text(serialized, encoding="utf-8")
    code, out, _err = run(zernike.main, ["rms", "--scheme", "noll", "--coeffs", str(path), "--json"])
    assert code == 2 and not out


def test_compatible_apertures_and_zero_rms_remain_valid(run_json):
    out = run_json(resolve.main, ["airy", "--wavelength-um", ".5", "--fnum", "4", "--na", ".125"])
    assert out["results"]["airy_radius_um"] == pytest.approx(2.44)
    assert run_json(zernike.main, ["strehl", "--rms-waves", "0"])["results"]["strehl_extended"] == 1


def test_no_fit_preserves_offset_measured_pupil(run_json, tmp_path):
    phase = np.full((64, 64), np.nan)
    # Valid measurement near the corner, entirely outside the inscribed canvas circle.
    phase[1:4, 1:4] = 0
    phase[1:4, 4:7] = 2 * np.pi
    path = tmp_path / "offset.npy"
    np.save(path, phase)
    r = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(path), "--measurement", "measured-opd", "--nterms", "0"])["results"]
    assert r["measured_opd_pv_waves"] == pytest.approx(1)
    assert r["measured_opd_rms_waves"] == pytest.approx(.5)


def test_piston_only_fit_reports_only_piston_removed(run_json, tmp_path):
    phase = np.zeros((16, 16))
    path = tmp_path / "phase.npy"
    np.save(path, phase)
    r = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(path), "--nterms", "1"])["results"]
    assert r["removed_terms"] == ["piston"]


@pytest.mark.parametrize("main,sub,option,scale", [(zernike.main, "fit", "--map", 1),
                                                (interfero.main, "fringe-to-wfe", "--phase", 4 * np.pi)])
def test_fit_reports_distinct_mask_and_full_disk_rms(run_json, tmp_path, main, sub, option, scale):
    # Analytic linear tilt x on a full inscribed pupil. A three-term fit reconstructs it;
    # full-disk coefficient RMS excludes tilt, while reconstructed-mask RMS retains it.
    x = (np.arange(32) - 15.5) / 16
    data = np.tile(x, (32, 1))
    path = tmp_path / "tilt.npy"
    np.save(path, data * scale)
    r = run_json(main, [sub, option, str(path), "--scheme", "fringe", "--nterms", "3"])["results"]
    assert r["coefficient_full_disk_rms_waves"] == pytest.approx(0, abs=1e-12)
    assert r["fit_rms_on_mask_waves"] == pytest.approx(.5, abs=.005)
    assert r["fit_diagnostics"]["rank"] == 3
    assert r["fit_diagnostics"]["valid_samples"] > 700
    assert r["fit_diagnostics"]["condition_number"] >= 1
