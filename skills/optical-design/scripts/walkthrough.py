# /// script
# requires-python = ">=3.11"
# dependencies = ["optiland==0.6.2"]
# ///
"""Understand and refocus a bundled triplet; save a readable review in a new directory.

Run from your project: uv run <absolute-skill-root>/scripts/walkthrough.py --out my-first-lens
The teaching baseline deliberately moves the image plane 1 mm from the bundled model.
Only that final air gap is optimized; this demonstrates focus, not a new lens design.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from contextlib import redirect_stdout
from importlib.metadata import version
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli
from _lib.import_fidelity import load_assessed_model
from _lib.review_render import render_html, validate_summary

SKILL_ROOT = Path(__file__).resolve().parents[1]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _share_spot_limits(before_figure, after_figure) -> list[dict]:
    """Keep each field's before/after panels on identical scales without clipping data."""
    limits = []
    for before_axis, after_axis in zip(before_figure.axes, after_figure.axes, strict=True):
        x_bounds = (*before_axis.get_xlim(), *after_axis.get_xlim())
        y_bounds = (*before_axis.get_ylim(), *after_axis.get_ylim())
        x_limits = [float(min(x_bounds)), float(max(x_bounds))]
        y_limits = [float(min(y_bounds)), float(max(y_bounds))]
        for axis in (before_axis, after_axis):
            axis.set_xlim(x_limits)
            axis.set_ylim(y_limits)
        limits.append({"x": x_limits, "y": y_limits})
    return limits


def run_walkthrough(out: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from optiland.analysis import SpotDiagram
    from optiland.fileio import load_optiland_file, save_optiland_file
    from optiland.optimization import LeastSquares, OptimizationProblem

    started = time.perf_counter()
    source = SKILL_ROOT / "assets" / "forms" / "cooke-triplet.zmx"
    source_hash = _hash(source)
    print("1/4 Load the bundled triplet and measure a deliberately defocused copy.", file=sys.stderr)
    lens, assessment = load_assessed_model(source)
    surface = len(lens.surfaces.surfaces) - 2
    original_gap = float(lens.surfaces.get_thickness(surface)[0])
    initial_gap = original_gap + 1.0
    lens.updater.set_thickness(initial_gap, surface)
    save_optiland_file(lens, str(out / "baseline.json"))

    def measure(optic):
        spot = SpotDiagram(optic, fields="all", wavelengths="all", reference="centroid", num_rings=6)
        rms = spot.rms_spot_radius()
        rows = [{"name": "RMS spot radius", "field": str(field.coord), "wavelength": float(w.value),
                 "value": float(rms[i][j]) * 1000.0, "unit": "um"}
                for i, field in enumerate(spot.fields) for j, w in enumerate(spot.wavelengths)]
        return spot, rows

    before_spot, before = measure(lens)
    # Freeze an illustrative acceptance threshold before optimization: halve the worst blur.
    threshold = max(row["value"] for row in before) / 2.0
    before_figure = before_spot.view(show=False, add_airy_disk=True)[0]
    print("2/4 Optimize only the final air gap within +/-1.5 mm; include the full-field edge.", file=sys.stderr)
    problem = OptimizationProblem()
    for hy in (0.0, 0.7, 1.0):
        for wavelength in lens.wavelengths.get_wavelengths():
            problem.add_operand("rms_spot_size", target=0.0, weight=1.0,
                input_data={"optic": lens, "surface_number": surface + 1,
                            "Hx": 0.0, "Hy": hy, "num_rays": 6, "wavelength": wavelength})
    problem.add_variable(lens, "thickness", surface_number=surface,
                         min_val=initial_gap - 1.5, max_val=initial_gap + 1.5)
    result = LeastSquares(problem).optimize(maxiter=30, method_choice="trf", tol=1e-8)
    _, pre_save = measure(lens)
    candidate = out / "candidate.json"
    save_optiland_file(lens, str(candidate))
    print("3/4 Reload candidate.json and compare every field/wavelength metric.", file=sys.stderr)
    reloaded = load_optiland_file(str(candidate))
    after_spot, after = measure(reloaded)
    checks = [{"name": row["name"], "field": row["field"], "wavelength": row["wavelength"], "unit": "um",
               "before_save": a["value"], "after_reload": row["value"], "tolerance": 1e-8}
              for a, row in zip(pre_save, after, strict=True)]
    for old, row in zip(before, after, strict=True):
        row.update(before=old["value"], requirement={"max": threshold})
    final_gap = float(reloaded.surfaces.get_thickness(surface)[0])
    if not initial_gap - 1.5 <= final_gap <= initial_gap + 1.5:
        raise ValueError("optimizer returned a final air gap outside the declared bounds")
    if _hash(source) != source_hash:
        raise ValueError("source hash changed during walkthrough")
    after_figure = after_spot.view(show=False, add_airy_disk=True)[0]
    plot_limits = _share_spot_limits(before_figure, after_figure)
    before_figure.savefig(out / "spot-before.png", dpi=130, bbox_inches="tight")
    after_figure.savefig(out / "spot-after.png", dpi=130, bbox_inches="tight")
    plt.close(before_figure)
    plt.close(after_figure)
    fig = reloaded.draw(fields="all", wavelengths="all", num_rays=5)[0]
    fig.savefig(out / "layout.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    worst_before = max(row["value"] for row in before)
    worst_after = max(row["value"] for row in after)
    summary = {
        "schema_version": 1, "model": str(source), "sha256": source_hash, "sha256_kind": "source_file",
        "engine": {"name": "optiland", "version": version("optiland")},
        "import_assessment": assessment,
        "evidence": {"status": "reloaded", "method": "SpotDiagram centroid RMS; hexapolar pupil with 6 rings; all configured fields and wavelengths",
                     "candidate": "candidate.json", "candidate_sha256": _hash(candidate), "checks": checks},
        "first_order": {
            "EFL": {"value": float(reloaded.paraxial.f2()), "unit": "mm"},
            "F/#": {"value": float(reloaded.paraxial.FNO()), "unit": "1"},
            "Image distance": {"value": final_gap, "unit": "mm"},
            "Back focal length": {"value": final_gap + float(reloaded.paraxial.F2()), "unit": "mm"}},
        "metrics": after,
        "changes": [{"surface": surface, "parameter": "final air gap (image-plane position)",
                     "before": initial_gap, "after": final_gap, "unit": "mm"}],
        "diagnosis": ("Objective: recover from deliberate defocus by reducing the worst sampled RMS radius by at least half, "
                      "varying only the final air gap within +/-1.5 mm of the baseline. "
                      "The teaching baseline deliberately moves the image plane 1 mm beyond the bundled starting form. "
                      "This defocus spreads rays into larger spots. Moving the image plane can reduce that blur, "
                      "but cannot remove all chromatic and off-axis aberrations. The baseline is saved as baseline.json; "
                      "the original bundled source is unchanged."),
        "verdict": (f"Worst sampled geometric RMS radius changed from {worst_before:.3g} to {worst_after:.3g} um. "
                    f"The illustrative requirement, frozen before optimization, is at most {threshold:.3g} um at each field and wavelength. "
                    "This demonstrates recovery from deliberate defocus; it does not establish diffraction-limited performance or manufacturing readiness. "
                    "Next action: define blur and contrast requirements for your intended application, then evaluate the saved candidate across the full field before releasing more design variables."),
        "figures": {"layout": "layout.png", "spot_before": "spot-before.png", "spot_after": "spot-after.png"},
        "captions": {"layout": "Reloaded candidate: rays travel through three glass elements to the adjusted image plane.",
                     "spot_before": "Before: deliberately defocused baseline. Each panel is a field; colors identify wavelengths. Corresponding before/after panels use identical axis scales.",
                     "spot_after": "After: saved and reloaded candidate, on the same axis scales as before. Smaller spots show reduced geometric blur; the Airy circles are diffraction references."},
        "settings": {"baseline_defocus_mm": 1.0, "source_image_distance_mm": original_gap,
                     "focus_bounds_mm": [initial_gap - 1.5, initial_gap + 1.5],
                     "optimizer": "Optiland LeastSquares trf", "evaluation_budget": 30,
                     "optimizer_success": bool(result.success), "optimizer_message": str(result.message),
                     "evaluations": int(result.nfev), "acceptance": "all 3 configured fields (including full field) x all 3 wavelengths",
                     "spot_plot_limits_mm": plot_limits,
                     "threshold_policy": "50% of worst baseline centroid RMS; frozen before optimization"},
    }
    if not result.success:
        summary["diagnosis"] += " The optimizer stopped without declaring convergence: " + str(result.message)
    validate_summary(summary)
    print("4/4 Render the before/after figures and saved-file evidence into review.html.", file=sys.stderr)
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    # Read the written contract just as the standalone renderer does.
    document, _ = render_html(json.loads(summary_path.read_text(encoding="utf-8")), out)
    review = out / "review.html"
    review.write_text(document, encoding="utf-8")
    return {"out": str(out), "review": str(review), "summary": str(summary_path), "candidate": str(candidate),
            "source_preserved": True, "worst_before_um": worst_before, "worst_after_um": worst_after,
            "requirements_pass": all(row["value"] <= threshold for row in after),
            "elapsed_seconds": round(time.perf_counter() - started, 2)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="new user-owned output directory outside the installed skill")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    out = Path(args.out).resolve()
    if out == SKILL_ROOT or SKILL_ROOT in out.parents:
        parser.error("--out must be outside the installed skill directory")
    if out.exists():
        parser.error("--out must name a new directory; existing user work is never overwritten")
    try:
        out.mkdir(parents=True, exist_ok=False)
        # Keep stdout a parseable envelope even if the optical engine prints diagnostics.
        with redirect_stdout(sys.stderr):
            results = run_walkthrough(out)
    except (OSError, ValueError, ImportError) as exc:
        cli.fail(str(exc))
    cli.emit(cli.Envelope("walkthrough", "focus", 1, {"out": args.out}, results,
             {"worst_before_um": "um", "worst_after_um": "um", "elapsed_seconds": "s"},
             "Real Optiland bounded image-plane focus, full-field/wavelength measurement, native save/reload and HTML review."), args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
