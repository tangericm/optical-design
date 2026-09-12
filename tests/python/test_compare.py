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


def _envelope(tmp_path, name, results, **metadata):
    path = tmp_path / name
    path.write_text(json.dumps({"results": results, **metadata}), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("a_results,b_results", [
    ({"strehl": 0.8}, {"rms_waves": 0.1}),
    ({}, {}),
    ({"label": "no data"}, {"label": "no data"}),
    ({"strehl": 0.8, "rms": 0.1}, {"strehl": 0.8}),
    ({"strehl": 0.8}, {"strehl": 0.8, "rms": 0.1}),
    ({"strehl": 0.8}, {"strehl": "0.8"}),
])
def test_strict_requires_complete_nonempty_numeric_coverage(run, tmp_path, a_results, b_results):
    a = _envelope(tmp_path, "a.json", a_results)
    b = _envelope(tmp_path, "b.json", b_results)
    code, out, _ = run(compare.main, [a, b, "--json"])
    assert code == 1
    result = json.loads(out)["results"]
    assert result["status"] == "incomparable"
    assert result["all_within_tolerance"] is False
    assert result["equivalent"] is False


@pytest.mark.parametrize("b_value,b_unit,code", [
    (1000, "um", 0), (1000, "µm", 0), (1000, "μm", 0),
    (1, "um", 1), (1, "waves", 1), (1, None, 1),
])
def test_units_are_converted_or_rejected(run, tmp_path, b_value, b_unit, code):
    a = _envelope(tmp_path, "a.json", {"spot": 1}, units={"spot": "mm"})
    b = _envelope(tmp_path, "b.json", {"spot": b_value}, units={"spot": b_unit} if b_unit else {})
    actual, out, _ = run(compare.main, [a, b, "--json", "--rtol", "0"])
    assert actual == code
    result = json.loads(out)["results"]
    if code == 0:
        assert result["diffs"]["results.spot"]["b"] == pytest.approx(1)
        assert result["diffs"]["results.spot"]["unit"] == "mm"
    else:
        assert result["equivalent"] is False


def test_nested_array_units_inherit_from_metric(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"spot": [1, 2]}, units={"spot": "mm"})
    b = _envelope(tmp_path, "b.json", {"spot": [1000, 2000]}, units={"spot": "um"})
    code, _, _ = run(compare.main, [a, b, "--json", "--rtol", "0"])
    assert code == 0


@pytest.mark.parametrize("key,left,right", [
    ("field", 0, 1), ("wavelength_nm", 550, 551),
    ("configuration", "nominal", "hot"),
    ("pupil", {"obscuration": 0}, {"obscuration": 0.5}),
    ("analysis_settings", {"grid": 64}, {"grid": 128}),
    ("metadata", {"field_id": "axis"}, {"field_id": "edge"}),
])
@pytest.mark.parametrize("location", ["top", "inputs", "results"])
def test_strict_rejects_changed_analysis_identity(run, tmp_path, key, left, right, location):
    docs = []
    for name, value in [("a.json", left), ("b.json", right)]:
        result = {"strehl": 0.8}
        metadata = {}
        if location == "results":
            result[key] = value
        elif location == "inputs":
            metadata["inputs"] = {key: value}
        else:
            metadata[key] = value
        docs.append(_envelope(tmp_path, name, result, **metadata))
    code, out, _ = run(compare.main, [*docs, "--rtol", "100", "--atol", "100", "--json"])
    assert code == 1
    assert json.loads(out)["results"]["status"] == "incomparable"


def test_missing_identity_cannot_be_verified(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8}, inputs={"wavelength_nm": 550})
    b = _envelope(tmp_path, "b.json", {"strehl": 0.8})
    code, out, _ = run(compare.main, [a, b, "--json"])
    assert code == 1
    assert json.loads(out)["results"]["status"] == "incomparable"


def test_changed_curve_coordinates_are_incomparable_even_with_loose_tolerance(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"mtf": [{"frequency": 10, "value": 0.8}]})
    b = _envelope(tmp_path, "b.json", {"mtf": [{"frequency": 11, "value": 0.8}]})
    code, out, _ = run(compare.main, [a, b, "--atol", "10", "--json"])
    assert code == 1
    assert json.loads(out)["results"]["status"] == "incomparable"


def test_shared_only_is_explicitly_exploratory(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8, "extra": 1})
    b = _envelope(tmp_path, "b.json", {"strehl": 0.8})
    code, out, _ = run(compare.main, [a, b, "--shared-only", "--json"])
    assert code == 0
    result = json.loads(out)["results"]
    assert result["status"] == "exploratory"
    assert result["equivalent"] is None
    assert result["only_in_a"] == ["results.extra"]


def test_shared_only_still_rejects_empty_intersection(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8})
    b = _envelope(tmp_path, "b.json", {"rms": 0.1})
    code, out, _ = run(compare.main, [a, b, "--shared-only", "--json"])
    assert code == 1
    assert json.loads(out)["results"]["all_within_tolerance"] is False


def test_explicit_required_metric_must_exist_on_both_sides(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8})
    code, out, _ = run(compare.main, [a, a, "--require", "rms", "--json"])
    assert code == 1
    assert json.loads(out)["results"]["missing_required"] == ["results.rms"]


@pytest.mark.parametrize("flag", ["--rtol", "--atol"])
@pytest.mark.parametrize("value", ["-1", "nan", "inf"])
def test_tolerances_must_be_finite_nonnegative(run, tmp_path, flag, value):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8})
    code, _, err = run(compare.main, [a, a, f"{flag}={value}", "--json"])
    assert code == 2
    assert "finite" in err or "nonnegative" in err


@pytest.mark.parametrize("raw", ["[]", "null", "42", '{"results": 1}',
                                  '{"results": {"x": NaN}}', '{"results": {"x": 1e999}}'])
def test_malformed_or_nonfinite_inputs_fail_cleanly(run, tmp_path, raw):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8})
    bad = tmp_path / "bad.json"
    bad.write_text(raw, encoding="utf-8")
    code, _, err = run(compare.main, [a, str(bad), "--json"])
    assert code == 4
    assert err.startswith("error:")


def test_results_arrays_are_supported(run, tmp_path):
    a = _envelope(tmp_path, "a.json", [0.8, 0.9])
    code, _, _ = run(compare.main, [a, a, "--json"])
    assert code == 0


@pytest.mark.parametrize("key,left,right", [
    ("npix", 128, 256), ("pad", 4, 8), ("scheme", "noll", "fringe"),
    ("removed_terms", [], ["piston"]), ("nan_semantics", "opaque", "missing"),
    ("wavelengths_nm", [550], [551]),
])
def test_native_cli_analysis_settings_define_identity(run, tmp_path, key, left, right):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8}, inputs={key: left})
    b = _envelope(tmp_path, "b.json", {"strehl": 0.8}, inputs={key: right})
    code, out, _ = run(compare.main, [a, b, "--json"])
    assert code == 1
    assert json.loads(out)["results"]["status"] == "incomparable"


def test_identity_metadata_alone_does_not_count_as_numeric_evidence(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"field": 1, "wavelength_nm": 550})
    code, out, _ = run(compare.main, [a, a, "--json"])
    assert code == 1
    assert json.loads(out)["results"]["numeric_coverage"]["shared"] == 0


@pytest.mark.parametrize("a_value,b_value,rtol", [(1e308, -1e308, "0.01"), (1e308, 1e308, "10")])
def test_arithmetic_overflow_never_certifies_equivalence(run, tmp_path, a_value, b_value, rtol):
    a = _envelope(tmp_path, "a.json", {"spot": a_value})
    b = _envelope(tmp_path, "b.json", {"spot": b_value})
    code, out, _ = run(compare.main, [a, b, "--rtol", rtol, "--json"])
    assert code == 1
    assert json.loads(out)["results"]["status"] == "incomparable"
    assert "Infinity" not in out


def test_unit_conversion_respects_absolute_reference_units(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"spot": 1}, units={"spot": "mm"})
    b = _envelope(tmp_path, "b.json", {"spot": 1010}, units={"spot": "um"})
    code, out, _ = run(compare.main, [a, b, "--rtol", "0", "--atol", "0.02", "--json"])
    assert code == 0
    assert json.loads(out)["results"]["diffs"]["results.spot"]["abs"] == pytest.approx(0.01)


def test_shared_only_cannot_certify_equivalence_despite_ignoring_units(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"spot": 1}, units={"spot": "mm"})
    b = _envelope(tmp_path, "b.json", {"spot": 1}, units={"spot": "waves"})
    code, out, _ = run(compare.main, [a, b, "--shared-only", "--json"])
    assert code == 0
    assert json.loads(out)["results"]["equivalent"] is None


def test_required_metric_accepts_unqualified_and_qualified_paths(run, tmp_path):
    a = _envelope(tmp_path, "a.json", {"strehl": 0.8, "rms": 0.1})
    code, _, _ = run(compare.main, [a, a, "--require", "strehl", "--require", "results.rms", "--json"])
    assert code == 0
