import interfero
import numpy as np
import pytest
from _lib import zernike as Z
from _lib.wfmap import coefficients_to_map


def _frames(phase, steps):
    return np.stack([1.0 + 0.8 * np.cos(phase + s) for s in steps])


@pytest.mark.parametrize("algorithm,steps", [
    ("4step", [0, np.pi / 2, np.pi, 3 * np.pi / 2]),
    ("3step", [0, 2 * np.pi / 3, 4 * np.pi / 3]),
    ("5step", [-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi]),
])
def test_psi_recovers_wrapped_phase(algorithm, steps):
    rho, _theta, mask = Z.unit_disk(64)
    phase = 2 * np.pi * 0.3 * (2 * rho**2 - 1)
    rec = interfero.psi_phase(_frames(phase, steps), algorithm)
    diff = np.angle(np.exp(1j * (rec - phase)))
    assert np.max(np.abs(diff[mask])) < 1e-6


def test_psi_cli_writes_phase(run_json, tmp_path):
    rho, _theta, _mask = Z.unit_disk(32)
    frames = _frames(0.5 * rho, [0, np.pi / 2, np.pi, 3 * np.pi / 2])
    fp = tmp_path / "frames.npy"
    np.save(fp, frames)
    out = run_json(interfero.main, ["psi", "--frames", str(fp), "--algorithm", "4step", "--out", str(tmp_path / "phase.npy")])
    assert out["results"]["shape"] == [32, 32]
    assert np.load(tmp_path / "phase.npy").shape == (32, 32)


def test_unwrap_recovers_multi_wave_ramp(run_json, tmp_path):
    x = np.linspace(0, 6 * np.pi, 64)
    phase = np.tile(x, (64, 1))
    wrapped = np.angle(np.exp(1j * phase))
    fp = tmp_path / "wrapped.npy"
    np.save(fp, wrapped)
    out = run_json(interfero.main, ["unwrap", "--phase", str(fp), "--out", str(tmp_path / "unwrapped.npy")])
    un = np.load(tmp_path / "unwrapped.npy")
    assert np.ptp(un) == pytest.approx(6 * np.pi, rel=1e-3)
    assert out["results"]["pv_waves"] == pytest.approx(3.0, rel=1e-3)


def test_fringe_to_wfe_double_pass_and_zernike(run_json, tmp_path):
    truth = [0, 0, 0, 0.1, 0, 0, 0, 0, 0.05]
    wmap, _mask = coefficients_to_map("fringe", truth, npix=96)
    phase = 2 * np.pi * 2 * wmap  # double pass (Fizeau on a mirror)
    fp = tmp_path / "phase.npy"
    np.save(fp, phase)
    out = run_json(interfero.main, ["fringe-to-wfe", "--phase", str(fp), "--passes", "2", "--scheme", "fringe", "--nterms", "9"])
    r = out["results"]
    np.testing.assert_allclose(r["coefficients"], truth, atol=1e-6)
    assert r["rms_waves"] == pytest.approx(np.sqrt((0.1 / np.sqrt(3))**2 + (0.05 / np.sqrt(5))**2), rel=1e-3)
    assert r["passes"] == 2


def test_fringe_to_wfe_full_square_matches_nan_masked_pupil(run_json, tmp_path):
    # Interferograms often arrive as a full square with zeros (not NaN) outside the pupil.
    # PV and map RMS must come from the pupil circle either way, not from the whole canvas.
    truth = [0, 0, 0, 0.1, 0, 0, 0, 0, 0.05]
    wmap, _mask = coefficients_to_map("fringe", truth, npix=96)
    phase = 2 * np.pi * 2 * wmap
    nan_path, zero_path = tmp_path / "nan.npy", tmp_path / "zero.npy"
    np.save(nan_path, phase)
    np.save(zero_path, np.nan_to_num(phase, nan=0.0))
    argv = ["fringe-to-wfe", "--passes", "2", "--scheme", "fringe", "--nterms", "9", "--phase"]
    masked = run_json(interfero.main, [*argv, str(nan_path)])["results"]
    square = run_json(interfero.main, [*argv, str(zero_path)])["results"]
    assert square["rms_map_waves"] == pytest.approx(masked["rms_map_waves"], abs=2e-3)
    assert square["pv_waves"] == pytest.approx(masked["pv_waves"], abs=2e-3)
    np.testing.assert_allclose(square["coefficients"], masked["coefficients"], atol=2e-3)


def test_cavity(run_json):
    out = run_json(interfero.main, ["cavity", "--gap-mm", "5", "--wavelength-um", "0.6328", "--tilt-arcsec", "10", "--linewidth-nm", "0.001"])
    r = out["results"]
    # fringe spacing for double-pass tilt: λ / (2 tan θ), θ = 10 arcsec = 4.848e-5 rad -> 6.53 mm
    assert r["fringe_spacing_mm"] == pytest.approx(6.527, rel=1e-3)
    assert r["coherence_length_mm"] == pytest.approx(400.4, rel=1e-3)   # λ²/Δλ = 0.4004 µm² / 1e-6 µm = 400.4 mm
    assert r["opd_mm"] == pytest.approx(10.0)
    assert out["warnings"] == []
    assert "oct-axial" in out["method"]      # names the other coherence-length convention


def test_fringe_to_wfe_missing_phase_exits_4(run, tmp_path):
    code, _, err = run(interfero.main, ["fringe-to-wfe", "--phase", str(tmp_path / "nosuch.npy")])
    assert code == 4 and err.startswith("error:")


def test_cavity_rejects_nonpositive_gap(run):
    code, _, err = run(interfero.main, ["cavity", "--gap-mm", "0", "--wavelength-um", "0.6328"])
    assert code == 2 and "gap" in err.lower()
