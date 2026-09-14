"""Paraxial first-order summary and gate; optiland==0.6.2 runs in an isolated uv env."""
import hashlib
import json
from pathlib import Path

import pytest

pytest.importorskip("optiland", reason="run with --with optiland==0.6.2")

import first_order

ASSETS = Path(__file__).resolve().parents[2] / "skills" / "optical-design" / "assets"
ZMX_MODEL = ASSETS / "defocused-singlet.zmx"
JSON_MODEL = ASSETS / "portable-singlet.json"


@pytest.mark.tier1
@pytest.mark.parametrize("model", [ZMX_MODEL, JSON_MODEL], ids=["zmx", "json"])
def test_first_order_reports_efl_and_fnumber(run_json, model):
    out = run_json(first_order.main, ["--model", str(model)])
    assert out["tool"] == "first_order" and out["tier"] == 1
    r = out["results"]
    assert r["efl_mm"] == pytest.approx(49.05139286997028, rel=1e-6)
    assert r["f_number"] == pytest.approx(4.905139286997028, rel=1e-6)
    assert r["epd_mm"] == pytest.approx(10.0)
    assert r["na_image"] == pytest.approx(1.0 / (2 * r["f_number"]))
    assert r["total_track_mm"] == pytest.approx(65.0)
    assert r["image_distance_mm"] == pytest.approx(60.0)
    assert r["bfl_mm"] == r["back_focal_length_mm"]
    assert r["na_image_paraxial"] == r["na_image"]
    assert out["units"]["efl_mm"] == "mm"
    assert out["units"]["f_number"] == "1"
    # Object is at infinity for this singlet; magnification is not meaningfully defined.
    assert "magnification" not in r


@pytest.mark.tier1
def test_chromatic_shift_is_zero_for_a_single_wavelength(run_json):
    out = run_json(first_order.main, ["--model", str(ZMX_MODEL)])
    r = out["results"]
    assert r["chromatic_shift_um"] == pytest.approx(0.0)
    assert set(r["per_wavelength_efl_mm"]) == {"0.55"}
    assert r["per_wavelength_efl_mm"]["0.55"] == pytest.approx(r["efl_mm"], rel=1e-6)


@pytest.mark.tier1
def test_on_axis_field_has_zero_telecentricity_error(run_json):
    out = run_json(first_order.main, ["--model", str(ZMX_MODEL)])
    r = out["results"]
    assert r["telecentricity_deg"] == pytest.approx(0.0, abs=1e-9)
    assert r["chief_ray_height_mm"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.tier1
def test_gate_passes_when_within_target_tolerance(run, tmp_path):
    spec = tmp_path / "gate.json"
    spec.write_text(json.dumps({
        "efl_mm": {"target": 49.05, "tol_pct": 1},
        "f_number": {"max": 5.6},
        "total_track_mm": {"max": 80},
    }))
    code, out, err = run(first_order.main, ["--model", str(ZMX_MODEL), "--spec", str(spec), "--json"])
    assert code == 0, err
    data = json.loads(out)
    gate = data["results"]["gate"]
    assert gate["pass"] is True
    assert all(check["pass"] for check in gate["checks"])


@pytest.mark.tier1
def test_gate_fails_and_exits_one(run, tmp_path):
    spec = tmp_path / "gate.json"
    spec.write_text(json.dumps({"efl_mm": {"target": 10, "tol_pct": 1}}))
    code, out, err = run(first_order.main, ["--model", str(ZMX_MODEL), "--spec", str(spec), "--json"])
    assert code == 1, err
    data = json.loads(out)
    gate = data["results"]["gate"]
    assert gate["pass"] is False
    assert gate["checks"][0]["key"] == "efl_mm"
    assert gate["checks"][0]["pass"] is False


@pytest.mark.tier1
def test_gate_unknown_key_is_a_usage_error(run, tmp_path):
    spec = tmp_path / "gate.json"
    spec.write_text(json.dumps({"not_a_real_key": {"max": 1}}))
    code, _, err = run(first_order.main, ["--model", str(ZMX_MODEL), "--spec", str(spec)])
    assert code == 2 and "not_a_real_key" in err


@pytest.mark.tier1
def test_missing_model_extension_is_an_analysis_failure(run):
    code, _, err = run(first_order.main, ["--model", "nope.txt"])
    assert code == 4 and "extension" in err


@pytest.mark.tier1
def test_input_file_bytes_are_unchanged_after_a_run(run):
    before = hashlib.sha256(ZMX_MODEL.read_bytes()).hexdigest()
    code, _, err = run(first_order.main, ["--model", str(ZMX_MODEL), "--json"])
    assert code == 0, err
    after = hashlib.sha256(ZMX_MODEL.read_bytes()).hexdigest()
    assert before == after


def test_back_focus_is_independent_of_detector_position():
    from _lib import first_order as fo
    optic = fo.load_optic(str(ZMX_MODEL))
    initial = fo.compute(optic)["results"]
    # An independent parallel input ray crosses the axis at the back focal point.
    y, u = optic.paraxial.trace_generic(1.0, 0.0, optic.surfaces.positions[1] - 1,
                                        optic.primary_wavelength)
    expected_bfl = float((-y[-2] / u[-2]).item())
    optic.updater.set_thickness(10.0 + optic.surfaces.surfaces[-2].thickness, -2)
    shifted = fo.compute(optic)["results"]
    assert initial["back_focal_length_mm"] == pytest.approx(expected_bfl)
    assert shifted["back_focal_length_mm"] == pytest.approx(expected_bfl)
    assert shifted["image_distance_mm"] == pytest.approx(initial["image_distance_mm"] + 10)


@pytest.mark.parametrize("rule", [
    {"tol_pct": 1}, {"max": float("nan")}, {"target": float("inf")},
    {"min": True}, {"target": 50, "tol_pct": -1}, {"min": 60, "max": 40},
])
def test_invalid_gate_rule_is_rejected(rule):
    from _lib.first_order import evaluate_gate
    with pytest.raises(ValueError):
        evaluate_gate({"efl_mm": 50}, {"efl_mm": rule})


@pytest.mark.parametrize("value,target,tol_pct,expected", [
    (0, 1e308, 2, False),
    (-1e308, 1e308, 199, False),
    (-1e308, 1e308, 200, True),
    (51, 50, 2, True),
    (51.0001, 50, 2, False),
    (0, 0, 1e308, True),
    (1e-308, 0, 1e308, False),
])
def test_target_gate_avoids_overflow_and_keeps_inclusive_boundaries(value, target, tol_pct, expected):
    from _lib.first_order import evaluate_gate
    gate = evaluate_gate({"efl_mm": value}, {"efl_mm": {"target": target, "tol_pct": tol_pct}})
    assert gate["pass"] is expected


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "50", None])
def test_nonfinite_or_nonnumeric_measurement_cannot_pass(value):
    from _lib.first_order import evaluate_gate
    assert evaluate_gate({"efl_mm": value}, {"efl_mm": {"max": 100}})["pass"] is False


def test_non_mm_model_cannot_pass_gate(run, tmp_path):
    model = tmp_path / "inch.zmx"
    model.write_text(ZMX_MODEL.read_text(encoding="utf-16").replace("UNIT MM", "UNIT IN"))
    spec = tmp_path / "gate.json"
    spec.write_text(json.dumps({"efl_mm": {"max": 100}}))
    code, _, err = run(first_order.main, ["--model", str(model), "--spec", str(spec), "--json"])
    assert code == 4
    assert "convert" in err.lower() and "UNIT IN" in err


def test_fidelity_warnings_survive_first_order(run_json, tmp_path):
    import inspect_zmx
    model = tmp_path / "unknown.zmx"
    model.write_text(ZMX_MODEL.read_text(encoding="utf-16") + "\nMYSTERYOPTIC 42\n")
    inspected = run_json(inspect_zmx.main, ["--model", str(model)])
    summary = run_json(first_order.main, ["--model", str(model)])
    assert summary["results"]["import_fidelity"] == inspected["results"]["import_fidelity"]
    assert set(inspected["warnings"]).issubset(summary["warnings"])
    assert any("MYSTERYOPTIC" in warning for warning in summary["warnings"])


@pytest.mark.parametrize("rule", [{"max": float("nan")}, {"min": True}, {"tol_pct": 1}])
def test_invalid_json_gate_is_a_usage_error(run, tmp_path, rule):
    spec = tmp_path / "gate.json"
    spec.write_text(json.dumps({"efl_mm": rule}))
    code, _, err = run(first_order.main, ["--model", str(ZMX_MODEL), "--spec", str(spec)])
    assert code == 2
    assert "gate rule" in err
