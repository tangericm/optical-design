import json

import compare
import pytest


def _write(tmp_path, name, results):
    p = tmp_path / name
    p.write_text(json.dumps({"schema": "1", "tool": "t", "subcommand": "s", "tier": 0, "inputs": {},
                             "results": results, "units": {}, "method": "", "warnings": []}))
    return str(p)


def test_flatten_numeric_leaves():
    flat = compare.flatten({"a": 1, "b": {"c": 2.5, "d": "x"}, "e": [1, 2]})
    assert flat == {"a": 1.0, "b.c": 2.5, "e.0": 1.0, "e.1": 2.0}


def test_within_tolerance_exits_0(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80, "rms": 0.07})
    b = _write(tmp_path, "b.json", {"strehl": 0.805, "rms": 0.0701})
    code, out, _ = run(compare.main, [a, b, "--rtol", "0.01", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["results"]["all_within_tolerance"] is True
    assert data["results"]["diffs"]["results.strehl"]["rel"] == pytest.approx(0.00625)


def test_outside_tolerance_exits_1_and_lists(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80})
    b = _write(tmp_path, "b.json", {"strehl": 0.70})
    code, out, _ = run(compare.main, [a, b, "--rtol", "0.05", "--json"])
    assert code == 1
    assert "results.strehl" in json.loads(out)["results"]["exceeded"]


def test_missing_keys_are_reported(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.80, "only_a": 1})
    b = _write(tmp_path, "b.json", {"strehl": 0.80, "only_b": 2})
    _code, out, _ = run(compare.main, [a, b, "--json"])
    data = json.loads(out)
    assert set(data["results"]["only_in_a"]) == {"results.only_a"} and set(data["results"]["only_in_b"]) == {"results.only_b"}


def test_missing_file_exits_4(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.8})
    code, _, err = run(compare.main, [a, str(tmp_path / "nosuch.json")])
    assert code == 4 and err.startswith("error:")


def test_invalid_json_exits_4(run, tmp_path):
    a = _write(tmp_path, "a.json", {"strehl": 0.8})
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    code, _, err = run(compare.main, [a, str(bad)])
    assert code == 4 and err.startswith("error:")


def test_zero_reference_keeps_the_json_valid(run, tmp_path):
    # |a| = 0 has no relative difference: report null, never Infinity, which no JSON parser
    # is required to accept.
    a = _write(tmp_path, "a.json", {"tilt": 0.0, "piston": 0.0})
    b = _write(tmp_path, "b.json", {"tilt": 0.5, "piston": 0.0})
    code, out, _ = run(compare.main, [a, b, "--json"])
    assert code == 1
    diffs = json.loads(out)["results"]["diffs"]
    assert diffs["results.tilt"]["rel"] is None
    assert diffs["results.piston"]["rel"] == 0.0
    assert "Infinity" not in out and "NaN" not in out
