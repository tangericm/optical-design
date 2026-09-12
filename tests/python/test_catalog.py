import copy
import hashlib
import importlib
import json

import pytest


def entry(part, value=25, unit="mm"):
    return {"vendor": "Synthetic", "part": part, "source": "urn:synthetic:fixture",
            "retrieved_on": "2026-09-12", "model": "synthetic:"+part,
            "properties": {"efl": {"value": value, "unit": unit},
                           "diameter": {"value": 12, "unit": "mm"}}}


def query():
    return {"schema": 1, "constraints": [
        {"property": "efl", "unit": "mm", "min": 24, "max": 26, "target": 25, "scale": 1},
        {"property": "diameter", "unit": "mm", "min": 10}]}


def invoke(run_json, tmp_path, entries, q=None):
    catalog = importlib.import_module("catalog")
    index_path, query_path = tmp_path / "index.json", tmp_path / "query.json"
    index_path.write_text(json.dumps({"schema": 1, "entries": entries}), encoding="utf-8")
    query_path.write_text(json.dumps(query() if q is None else q), encoding="utf-8")
    result = run_json(catalog.main, ["match", "--index", str(index_path), "--query", str(query_path)])
    return result, index_path, query_path


def test_unit_conversion_target_ranking_ties_and_provenance(run_json, tmp_path):
    rows = [entry("Z", 25000, "um"), entry("B", 25.5), entry("A", 25), entry("outside", 30)]
    out, index_path, query_path = invoke(run_json, tmp_path, rows)
    assert [r["part"] for r in out["results"]["matches"]] == ["A", "Z", "B"]
    assert [r["score"] for r in out["results"]["matches"]] == pytest.approx([0, 0, .5])
    assert out["results"]["matches"][1]["evaluated"]["efl"] == {"value": 25, "unit": "mm"}
    for key, path in [("index", index_path), ("query", query_path)]:
        assert out["provenance"]["catalog_inputs"][key]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    reversed_out, _, _ = invoke(run_json, tmp_path, list(reversed(rows)))
    assert reversed_out["results"] == out["results"]


def test_missing_properties_and_incompatible_units_never_match(run_json, tmp_path):
    a, b = entry("missing"), entry("wrong-dimension", 25, "deg")
    del a["properties"]["diameter"]
    out, _, _ = invoke(run_json, tmp_path, [a, b])
    assert out["results"]["status"] == "no_matches"
    assert out["results"]["matches"] == []
    assert len(out["results"]["rejected"]) == 2


@pytest.mark.parametrize("bad", [
    {}, {"schema": 1, "constraints": []},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm"}]},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm", "min": 26, "max": 24}]},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm", "min": 24, "target": 25}]},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm", "min": True}]},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm", "min": float("nan")}]},
    {"schema": 1, "constraints": [{"property": "efl", "unit": "mm", "min": 24, "typo": 3}]},
])
def test_malformed_queries_raise_usage_error(run, tmp_path, bad):
    catalog = importlib.import_module("catalog")
    idx, q = tmp_path / "i.json", tmp_path / "q.json"
    idx.write_text(json.dumps({"schema": 1, "entries": [entry("a")]}))
    q.write_text(json.dumps(bad))
    code, _, err = run(catalog.main, ["match", "--index", str(idx), "--query", str(q)])
    assert code == 2, err


@pytest.mark.parametrize("change", ["date", "source", "duplicate", "nonfinite", "unit", "unknown"])
def test_invalid_catalog_rejected(run, tmp_path, change):
    catalog = importlib.import_module("catalog")
    rows = [entry("a")]
    if change == "date":
        rows[0]["retrieved_on"] = "2026-02-30"
    elif change == "source":
        del rows[0]["source"]
    elif change == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    elif change == "nonfinite":
        rows[0]["properties"]["efl"]["value"] = float("inf")
    elif change == "unit":
        rows[0]["properties"]["efl"]["unit"] = "furlong"
    else:
        rows[0]["propertiez"] = {}
    path = tmp_path / "index.json"
    path.write_text(json.dumps({"schema": 1, "entries": rows}))
    code, _, err = run(catalog.main, ["validate", "--index", str(path)])
    assert code == 2, err


def test_validates_without_claiming_vendor_verification(run_json, tmp_path):
    catalog = importlib.import_module("catalog")
    path = tmp_path / "index.json"
    path.write_text(json.dumps({"schema": 1, "entries": [entry("a")]}))
    out = run_json(catalog.main, ["validate", "--index", str(path)])
    assert out["results"] == {"status": "valid", "entry_count": 1, "source_verification": "declared_only"}
    assert any("availability" in w for w in out["warnings"])


def test_rank_weight_overflow_cannot_become_perfect_match(run, tmp_path):
    catalog = importlib.import_module("catalog")
    idx, path = tmp_path / "index.json", tmp_path / "query.json"
    idx.write_text(json.dumps({"schema": 1, "entries": [entry("a")]}))
    q = query()
    q["constraints"][0]["weight"] = 1e308
    q["constraints"][1].update({"target": 12, "scale": 1, "weight": 1e308})
    path.write_text(json.dumps(q))
    code, _, err = run(catalog.main, ["match", "--index", str(idx), "--query", str(path)])
    assert code == 2 and "overflow" in err


def test_unrepresentable_integer_is_usage_error(run, tmp_path):
    catalog = importlib.import_module("catalog")
    row = entry("a", 10**400)
    path = tmp_path / "index.json"
    path.write_text(json.dumps({"schema": 1, "entries": [row]}))
    code, _, err = run(catalog.main, ["validate", "--index", str(path)])
    assert code == 2 and "finite" in err


def test_limit_retains_total_match_count_and_input_identity(run_json, tmp_path):
    catalog = importlib.import_module("catalog")
    _, idx, q = invoke(run_json, tmp_path, [entry("A"), entry("B"), entry("C")])
    out = run_json(catalog.main, ["match", "--index", str(idx), "--query", str(q), "--limit", "1"])
    assert len(out["results"]["matches"]) == 1
    assert out["results"]["total_matches"] == 3
    assert out["inputs"]["limit"] == 1


def test_duplicate_json_key_is_rejected(run, tmp_path):
    catalog = importlib.import_module("catalog")
    path = tmp_path / "index.json"
    path.write_text('{"schema": 1, "schema": 1, "entries": []}')
    code, _, err = run(catalog.main, ["validate", "--index", str(path)])
    assert code == 2 and "duplicate JSON key" in err
