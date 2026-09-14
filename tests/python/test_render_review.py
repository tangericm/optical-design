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
