# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib==3.10.8"]
# ///
"""Render the README comparison from a verified synthetic refocus receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--report", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/optical-design/scripts"))
from _lib.review_report import validate_review_receipt

verified = validate_review_receipt(args.report)
assert verified["accepted_candidate"] is True
report = json.loads(args.report.read_text(encoding="utf-8"))
assert report["action"] == "refocus" and report["status"] == "improved"
summary = {
    "example": "Bundled synthetic singlet; final air-gap refocus",
    "engine": report["baseline"]["inspection"]["engine"],
    "receipt_sha256": hashlib.sha256(args.report.read_bytes()).hexdigest(),
    "source": report["source"],
    "settings": report["spec"]["analysis"],
    "saved_candidate_verified": report["saved_candidate_verified"],
    "source_unchanged": report["source_unchanged"],
    "measurements": {},
}
# Public evidence needs file identity, not this machine's absolute source path.
summary["source"] = {key: value for key, value in summary["source"].items() if "path" not in key.lower()}
for side in ("baseline", "candidate"):
    summary[side + "_focus_mm"] = report[side]["inspection"]["focus_mm"]
    summary["measurements"][side] = [m for m in report[side]["measurements"] if m["metric"] in ("rms_spot_um", "mtf")]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False})
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, metric, title, limit, units in zip(axes, ("rms_spot_um", "mtf"),
        ("RMS spot radius", "MTF at 20 cycles/mm"), (30, 0.3), ("µm · lower is better", "contrast · higher is better")):
    vals = [next(m["value"] for m in summary["measurements"][side] if m["metric"] == metric) for side in ("baseline", "candidate")]
    ax.barh([1, 0], vals, color=["#73828C", "#087F8C"], height=0.43)
    ax.set_yticks([1, 0], ["Before", "After"])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, (max(vals) * 1.23 if metric == "rms_spot_um" else 0.65))
    ax.axvline(limit, color="#102A3A", linestyle="--", linewidth=1, label=f"Example requirement: {'≤' if metric == 'rms_spot_um' else '≥'} {limit}")
    for y, value in zip([1, 0], vals):
        ax.annotate(f"{value:.2f}" if metric == "rms_spot_um" else f"{value:.4f}", (value, y), xytext=(6, 0), textcoords="offset points", va="center", color="#102A3A")
    ax.set_title(title, loc="left", weight="bold", pad=18)
    ax.set_xlabel(units, loc="left", labelpad=8)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.01, -0.5), frameon=False, fontsize=9)
fig.suptitle("One bounded refocus. A saved, verified result.", x=0.03, ha="left", fontsize=16, weight="bold", color="#102A3A")
fig.text(0.03, 0.02, "Synthetic singlet · on-axis · 550 nm · Optiland 0.6.2 · geometric RMS radius / scalar tangential FFT MTF", fontsize=9, color="#526572")
fig.subplots_adjust(left=0.09, right=0.97, top=0.72, bottom=0.32, wspace=0.45)
args.out.mkdir(parents=True, exist_ok=True)
fig.savefig(args.out / "refocus-comparison.png", dpi=160, facecolor="white")
plt.close(fig)
(args.out / "refocus-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(args.out.resolve())
