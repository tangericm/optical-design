"""ZMX/Optiland-JSON inspection; optiland==0.6.2 runs in an isolated uv env."""
import hashlib
import json
from pathlib import Path

import pytest

pytest.importorskip("optiland", reason="run with --with optiland==0.6.2")

import inspect_zmx

ASSETS = Path(__file__).resolve().parents[2] / "skills" / "optical-design" / "assets"
ZMX_MODEL = ASSETS / "defocused-singlet.zmx"
JSON_MODEL = ASSETS / "portable-singlet.json"


@pytest.mark.tier1
def test_inspects_a_real_optic_studio_export(run_json):
    out = run_json(inspect_zmx.main, ["--model", str(ZMX_MODEL)])
    assert out["tool"] == "inspect_zmx" and out["tier"] == 1
    r = out["results"]
    assert r["format"] == "Zemax sequential text"
    assert r["units"] == "mm"
    assert r["aperture_type"] == "EPD"
    assert r["aperture_value"] == pytest.approx(10.0)
    assert r["element_count"] == 1
    materials = {s["material"] for s in r["surfaces"]}
    assert "N-BK7" in materials
    stops = [s for s in r["surfaces"] if s["is_stop"]]
    assert len(stops) == 1 and stops[0]["index"] == 1
    assert r["wavelengths"]["values_um"] == [pytest.approx(0.55)]


@pytest.mark.tier1
def test_sha256_matches_input_bytes(run_json):
    out = run_json(inspect_zmx.main, ["--model", str(ZMX_MODEL)])
    expected = hashlib.sha256(ZMX_MODEL.read_bytes()).hexdigest()
    assert out["results"]["sha256"] == expected


@pytest.mark.tier1
def test_directives_include_auth_marked_ignored(run_json):
    out = run_json(inspect_zmx.main, ["--model", str(ZMX_MODEL)])
    directives = {d["key"]: d["used"] for d in out["results"]["directives"]}
    assert "AUTH" in directives
    assert directives["AUTH"] is False
    # A handful of directives that do shape the traced model should be marked used.
    for key in ("SURF", "TYPE", "CURV", "DISZ", "GLAS", "STOP"):
        assert directives.get(key) is True, key


@pytest.mark.tier1
def test_ordinary_singlet_has_no_multiconfig_or_nsc_warning(run_json):
    out = run_json(inspect_zmx.main, ["--model", str(ZMX_MODEL)])
    text = " ".join(out["warnings"]).lower()
    assert "configuration" not in text
    assert "non-sequential" not in text


@pytest.mark.tier1
def test_json_model_has_no_directives_block(run_json):
    out = run_json(inspect_zmx.main, ["--model", str(JSON_MODEL)])
    assert out["results"]["format"] == "Optiland JSON"
    assert "directives" not in out["results"]
    assert out["results"]["element_count"] == 1


@pytest.mark.tier1
def test_input_file_bytes_are_unchanged_after_a_run(run):
    before = hashlib.sha256(ZMX_MODEL.read_bytes()).hexdigest()
    code, _, err = run(inspect_zmx.main, ["--model", str(ZMX_MODEL), "--json"])
    assert code == 0, err
    after = hashlib.sha256(ZMX_MODEL.read_bytes()).hexdigest()
    assert before == after


@pytest.mark.tier1
def test_unsupported_extension_is_an_analysis_failure(run, tmp_path):
    bogus = tmp_path / "nope.step"
    bogus.write_bytes(b"not a lens file")
    code, _, err = run(inspect_zmx.main, ["--model", str(bogus)])
    assert code == 4 and "extension" in err


def test_directive_classification_is_json_serializable():
    """No engine needed: the classifier itself is pure and total."""
    for key in ("AUTH", "NAME", "VDXN", "VCYN", "VANN", "TOL1", "MOFF", "SURF", "GCAT", "UNKNOWNTOKEN"):
        assert inspect_zmx._classify(key) in ("used", "ignored")
    assert json.dumps([inspect_zmx._classify("AUTH")])
