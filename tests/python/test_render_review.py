"""render_review.py: no optical engine involved, pure HTML assembly from a summary.json."""
import json
import struct
import zlib

import pytest
import render_review


def _png(rgb=(10, 20, 30)):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00" + bytes(rgb))
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _write_summary(tmp_path, **overrides):
    (tmp_path / "figures").mkdir(exist_ok=True)
    (tmp_path / "figures" / "layout.png").write_bytes(_png((10, 20, 30)))
    (tmp_path / "figures" / "spot.png").write_bytes(_png((200, 50, 50)))
    summary = {
        "model": "assets/defocused-singlet.zmx",
        "sha256": "ec1fb8245314d8373aab2dc81d29b17bfb6c14e2d630a0ddf5bd46ea6d8ccbf7",
        "engine": {"name": "optiland", "version": "0.6.2"},
        "first_order": {
            "EFL": {"value": 49.051392869970283, "unit": "mm"},
            "F/#": {"value": 4.905139286997028, "unit": "1"},
        },
        "metrics": [
            {"name": "MTF", "field": 0.0, "wavelength": 0.55, "value": 0.4231, "unit": "1",
             "frequency": 20, "axis": "tangential", "requirement": {"min": 0.3}, "pass": True},
            {"name": "RMS spot", "field": 1.0, "wavelength": 0.55, "value": 12.345, "unit": "um",
             "requirement": {"max": 10}, "pass": False},
        ],
        "figures": {"mtf": "figures/missing.png", "layout": "figures/layout.png", "spot": "figures/spot.png"},
        "changes": [{"surface": 2, "parameter": "radius", "before": -50.0, "after": -48.234, "unit": "mm"}],
        "verdict": "The lens refocused cleanly. Spot size dropped under the Airy disk. MTF now clears requirement.",
        "diagnosis": "Residual astigmatism dominates at the edge field.",
        "settings": {"optimizer": "least_squares", "iterations": 12},
    }
    summary.update(overrides)
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(summary))
    return path


def test_section_order_and_content(run, tmp_path):
    summary = _write_summary(tmp_path)
    out = tmp_path / "review.html"
    code, stdout, err = run(render_review.main, ["--summary", str(summary), "--out", str(out), "--json"])
    assert code == 0, err
    html = out.read_text(encoding="utf-8")

    assert html.strip().startswith("<!doctype html>")
    title_pos = html.index("<title>")
    verdict_pos = html.index('<div class="verdict">')
    figures_pos = html.index("<h2>Figures</h2>")
    first_order_pos = html.index("<h2>First-order summary</h2>")
    metrics_pos = html.index("<h2>Metrics</h2>")
    changes_pos = html.index("<h2>Changes</h2>")
    details_pos = html.index("<details>")
    assert title_pos < verdict_pos < figures_pos < first_order_pos < metrics_pos < changes_pos < details_pos

    # model name and short hash in the title
    assert "defocused-singlet.zmx" in html
    assert "ec1fb824" in html

    data = json.loads(stdout)
    assert data["results"]["metrics_total"] == 2 and data["results"]["metrics_pass"] == 1


def test_rounding_never_prints_a_raw_float(run, tmp_path):
    summary = _write_summary(tmp_path)
    out = tmp_path / "review.html"
    run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    html = out.read_text(encoding="utf-8")
    assert "49.051392869970283" not in html
    assert "4.905139286997028" not in html
    assert "12.345" not in html
    assert ">49.1<" in html  # 3 sig figs
    assert ">0.42<" in html  # MTF: 2 decimals
    assert "12.3" in html  # RMS spot: 3 sig figs


def test_requirement_renders_as_human_text_not_json(run, tmp_path):
    summary = _write_summary(tmp_path)
    out = tmp_path / "review.html"
    run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    html = out.read_text(encoding="utf-8")
    assert "≥ 0.30 at 20 cyc/mm, tangential" in html
    assert '{"min"' not in html and "&quot;min&quot;" not in html


def test_figures_are_embedded_as_data_uris_and_missing_ones_are_skipped(run, tmp_path):
    summary = _write_summary(tmp_path)
    out = tmp_path / "review.html"
    code, stdout, err = run(render_review.main, ["--summary", str(summary), "--out", str(out), "--json"])
    assert code == 0, err
    html = out.read_text(encoding="utf-8")
    assert html.count("data:image/png;base64,") == 2
    data = json.loads(stdout)
    assert sorted(data["results"]["figures_embedded"]) == ["layout", "spot"]
    assert data["results"]["figures_missing"] == ["mtf"]
    assert any("mtf" in w for w in data["warnings"])


def test_missing_verdict_falls_back_to_placeholder_line(run, tmp_path):
    summary = _write_summary(tmp_path)
    data = json.loads(summary.read_text())
    del data["verdict"]
    summary.write_text(json.dumps(data))
    out = tmp_path / "review.html"
    run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    html = out.read_text(encoding="utf-8")
    assert "No verdict was written." in html


def test_missing_changes_is_not_an_error(run, tmp_path):
    summary = _write_summary(tmp_path)
    data = json.loads(summary.read_text())
    del data["changes"]
    summary.write_text(json.dumps(data))
    out = tmp_path / "review.html"
    code, _, err = run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    assert code == 0, err


@pytest.mark.parametrize("mutate", [
    lambda d: d.pop("metrics"),
    lambda d: d.__setitem__("metrics", "not a list"),
    lambda d: d.pop("engine"),
    lambda d: d.__setitem__("first_order", []),
])
def test_malformed_summary_exits_four(run, tmp_path, mutate):
    summary = _write_summary(tmp_path)
    data = json.loads(summary.read_text())
    mutate(data)
    summary.write_text(json.dumps(data))
    out = tmp_path / "review.html"
    code, _, err = run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    assert code == 4 and err
    assert not out.exists()


def test_not_json_at_all_exits_four(run, tmp_path):
    summary = tmp_path / "summary.json"
    summary.write_text("{not json")
    out = tmp_path / "review.html"
    code, _, err = run(render_review.main, ["--summary", str(summary), "--out", str(out)])
    assert code == 4 and err


@pytest.mark.parametrize("metric", [
    {"value": 12, "requirement": {"max": 10}, "pass": True},
    {"value": 9, "requirement": {"max": 10}, "pass": False},
    {"value": float("nan"), "requirement": {"max": 10}},
    {"value": True},
    {"value": 9, "requirement": {"max": float("inf")}},
    {"value": 9, "requirement": {"min": 10, "max": 5}},
    {"value": 9, "requirement": {}},
    {"value": 9, "pass": "false"},
])
def test_rejects_unreliable_metric_claims(run, tmp_path, metric):
    summary = _write_summary(tmp_path, metrics=[{"name": "RMS spot", **metric}])
    code, _, err = run(render_review.main, ["--summary", str(summary), "--out", str(tmp_path / "r.html")])
    assert code == 4, err


def test_versioned_report_computes_threshold_and_explains_evidence(run, tmp_path):
    summary = _write_summary(tmp_path, schema_version=1, sha256_kind="source_file",
        evidence={"status": "measured", "method": "SpotDiagram centroid reference"},
        metrics=[{"name": "RMS spot", "field": "0,1 normalized", "wavelength": 0.55,
                  "value": 12, "before": 20, "unit": "um", "requirement": {"max": 10}}],
        captions={"spot": "Smaller spots mean less geometric blur; inspect the edge field."})
    out = tmp_path / "r.html"
    code, stdout, err = run(render_review.main, ["--summary", str(summary), "--out", str(out), "--json"])
    assert code == 0, err
    doc = out.read_text(encoding="utf-8")
    assert "Measured" in doc and "Authored interpretation" in doc
    assert "1 requirement failed" in doc and "FAIL" in doc
    assert "Before" in doc and "Smaller spots" in doc
    assert json.loads(stdout)["results"]["metrics_pass"] == 0


def test_reload_status_requires_matching_metric_evidence(run, tmp_path):
    summary = _write_summary(tmp_path, schema_version=1, evidence={"status": "reloaded"})
    code, _, _ = run(render_review.main, ["--summary", str(summary), "--out", str(tmp_path / "r.html")])
    assert code == 4


def test_legacy_supplied_flags_do_not_create_acceptance(run, tmp_path):
    summary = _write_summary(tmp_path, metrics=[{"name": "RMS spot", "value": 20,
                            "wavelength": "d line", "unit": "um", "pass": True}])
    out = tmp_path / "r.html"
    code, stdout, err = run(render_review.main, ["--summary", str(summary), "--out", str(out), "--json"])
    assert code == 0, err
    assert json.loads(stdout)["results"]["metrics_pass"] == 0
    doc = out.read_text(encoding="utf-8")
    assert "Supplied data" in doc and "No acceptance requirements" in doc


def test_unit_blocked_import_cannot_acquire_passing_report(run, tmp_path):
    summary = _write_summary(tmp_path, schema_version=1,
        import_assessment={"status": "partial", "source_units": "IN", "numerical_analysis_allowed": False})
    code, _, err = run(render_review.main, ["--summary", str(summary), "--out", str(tmp_path / "r.html")])
    assert code == 4 and "convert source units" in err


@pytest.mark.parametrize("after,tolerance", [(2, 1e-8), (1, -1), (1, float("inf"))])
def test_reload_claim_rejects_disagreement_and_invalid_tolerance(run, tmp_path, after, tolerance):
    summary = _write_summary(tmp_path, metrics=[{"name": "RMS spot", "value": after, "unit": "um"}],
        evidence={"status": "reloaded", "method": "RMS",
        "candidate": "candidate.json", "candidate_sha256": "a" * 64,
        "checks": [{"name": "RMS spot", "unit": "um", "before_save": 1,
                    "after_reload": after, "tolerance": tolerance}]})
    code, _, _ = run(render_review.main, ["--summary", str(summary), "--out", str(tmp_path / "r.html")])
    assert code == 4


def _write_reloaded_summary(tmp_path):
    path = _write_summary(tmp_path, schema_version=1)
    data = json.loads(path.read_text())
    data["evidence"] = {"status": "reloaded", "method": "Per-condition optical measurements",
        "candidate": "candidate.json", "candidate_sha256": "a" * 64,
        "checks": [{**{key: row[key] for key in ("name", "field", "wavelength", "frequency", "axis", "unit") if key in row},
                    "before_save": row["value"], "after_reload": row["value"], "tolerance": 1e-8}
                   for row in data["metrics"]]}
    path.write_text(json.dumps(data))
    return path, data


def test_reload_measurements_must_equal_reported_metric_values(run, tmp_path):
    path, data = _write_reloaded_summary(tmp_path)
    data["metrics"][1]["value"] = 99
    data["evidence"]["checks"][1].update(before_save=1, after_reload=1)
    path.write_text(json.dumps(data))
    code, _, err = run(render_review.main, ["--summary", str(path), "--out", str(tmp_path / "r.html")])
    assert code == 4 and "reported metric value" in err


@pytest.mark.parametrize("mutate", [
    lambda d: d["evidence"]["checks"].pop(),
    lambda d: d["evidence"]["checks"].append(d["evidence"]["checks"][0].copy()),
    lambda d: d["metrics"].append(d["metrics"][0].copy()),
    lambda d: d["evidence"]["checks"][0].pop("name"),
    lambda d: d["evidence"]["checks"][0].__setitem__("field", 0.7),
    lambda d: d["evidence"]["checks"][0].__setitem__("wavelength", 0.65),
    lambda d: d["evidence"]["checks"][0].__setitem__("frequency", 40),
    lambda d: d["evidence"]["checks"][0].__setitem__("axis", "sagittal"),
    lambda d: d["evidence"]["checks"][1].__setitem__("unit", "mm"),
])
def test_reload_requires_unique_complete_matching_metric_evidence(run, tmp_path, mutate):
    path, data = _write_reloaded_summary(tmp_path)
    mutate(data)
    path.write_text(json.dumps(data))
    code, _, err = run(render_review.main, ["--summary", str(path), "--out", str(tmp_path / "r.html")])
    assert code == 4 and "reload" in err


def test_complete_reload_evidence_is_matched_by_identity_not_row_order(run, tmp_path):
    path, data = _write_reloaded_summary(tmp_path)
    data["evidence"]["checks"].reverse()
    path.write_text(json.dumps(data))
    out = tmp_path / "r.html"
    code, _, err = run(render_review.main, ["--summary", str(path), "--out", str(out)])
    assert code == 0, err
    assert "Reloaded:" in out.read_text(encoding="utf-8")
