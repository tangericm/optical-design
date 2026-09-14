"""The beginner journey runs in a fresh consumer directory with real Optiland."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "optical-design" / "scripts"


@pytest.mark.tier1
def test_walkthrough_preserves_source_and_reloads_measured_candidate(tmp_path):
    pytest.importorskip("optiland")
    source = SCRIPTS.parent / "assets" / "forms" / "cooke-triplet.zmx"
    before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    out = tmp_path / "my-first-lens"
    proc = subprocess.run([sys.executable, str(SCRIPTS / "walkthrough.py"), "--out", str(out), "--json"],
                          cwd=tmp_path, capture_output=True, text=True, timeout=180, check=False)
    assert proc.returncode == 0, proc.stderr
    envelope = json.loads(proc.stdout)
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert envelope["results"]["review"] == str(out / "review.html")
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before_hash == summary["sha256"]
    assert summary["evidence"]["status"] == "reloaded"
    assert hashlib.sha256((out / "candidate.json").read_bytes()).hexdigest() == summary["evidence"]["candidate_sha256"]
    metrics = summary["metrics"]
    assert len(metrics) == 9
    checks = summary["evidence"]["checks"]
    by_condition = {(check["name"], check["field"], check["wavelength"]): check for check in checks}
    assert len(by_condition) == len(checks) == len(metrics)
    for metric in metrics:
        check = by_condition[(metric["name"], metric["field"], metric["wavelength"])]
        assert check["after_reload"] == metric["value"]
        assert check["unit"] == metric["unit"]
    assert max(m["value"] for m in metrics) < max(m["before"] for m in metrics) * 0.5
    assert len({m["field"] for m in metrics}) == 3
    from optiland.analysis import SpotDiagram
    from optiland.fileio import load_optiland_file
    lens = load_optiland_file(str(out / "candidate.json"))
    spot = SpotDiagram(lens, fields="all", wavelengths="all", reference="centroid", num_rings=6)
    measured = [float(value) * 1000 for row in spot.rms_spot_radius() for value in row]
    assert measured == pytest.approx([m["value"] for m in metrics], abs=1e-8)
    review = (out / "review.html").read_text(encoding="utf-8")
    assert "Reloaded:" in review and "deliberately" in review
    assert "Objective:" in review and "Next action:" in review
    assert "identical axis scales" in review
    assert review.count("data:image/png;base64,") == 3
    # Re-running cannot overwrite user work, even with identical input arguments.
    second = subprocess.run([sys.executable, str(SCRIPTS / "walkthrough.py"), "--out", str(out)],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30, check=False)
    assert second.returncode == 2 and "new directory" in second.stderr


def test_before_after_panels_share_union_of_axis_limits():
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import walkthrough
    before, before_axes = plt.subplots(1, 2)
    after, after_axes = plt.subplots(1, 2)
    try:
        before_axes[0].set(xlim=(-0.1, 0.1), ylim=(-0.2, 0.2))
        after_axes[0].set(xlim=(-0.03, 0.04), ylim=(-0.05, 0.06))
        before_axes[1].set(xlim=(-0.1, 0.1), ylim=(-0.2, 0.2))
        after_axes[1].set(xlim=(-0.2, 0.05), ylim=(-0.1, 0.3))
        walkthrough._share_spot_limits(before, after)
        assert before_axes[0].get_xlim() == after_axes[0].get_xlim() == (-0.1, 0.1)
        assert before_axes[0].get_ylim() == after_axes[0].get_ylim() == (-0.2, 0.2)
        assert before_axes[1].get_xlim() == after_axes[1].get_xlim() == (-0.2, 0.1)
        assert before_axes[1].get_ylim() == after_axes[1].get_ylim() == (-0.2, 0.3)
    finally:
        plt.close(before)
        plt.close(after)
