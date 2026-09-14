# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a folder of analysis results into one self-contained HTML review page.

Needs no optical engine -- it only lays out numbers and PNGs someone else already
computed (inspect_zmx.py, first_order.py, an Optiland analyze/optimize run, ...).

Input contract: --summary points at a JSON file (typically named summary.json; other
paths referenced below are resolved relative to *its* directory, not the CWD):

    {
      "schema_version": 1,
      "model": "path/to/lens.zmx",
      "sha256": "<source model hash>",
      "sha256_kind": "source_file",
      "engine": {"name": "optiland", "version": "0.6.2"},
      "evidence": {"status": "measured", "method": "analysis method and sampling"},
      "first_order": {"EFL": {"value": 49.05, "unit": "mm"}, ...},
      "metrics": [
        {"name": "MTF", "field": 0.0, "wavelength": 0.55, "value": 0.42, "unit": "1",
         "frequency": 20, "axis": "tangential",
         "requirement": {"min": 0.3}, "pass": true},
        ...
      ],
      "figures": {"layout": "figures/layout.png", "spot": "figures/spot.png", ...},
      "changes": [{"surface": 2, "parameter": "radius", "before": -50.0, "after": -48.2, "unit": "mm"}],
      "verdict": "2 to 4 sentences of plain language.",
      "diagnosis": "optional plain-language aberration diagnosis",
      "settings": {"...": "..."}
    }

Only "model", "sha256", "engine", "first_order", "metrics" and "figures" are required.
Version 1 preserves the legacy shape; omission of schema_version is accepted for
legacy packages. sha256_kind is source_file, saved_candidate, or in_memory_json.
Each metric's value and optional before are finite numbers or null (unavailable).
Wavelength is in micrometres; field should include its coordinate convention.
Requirements must have finite min/max bounds; status is computed from those bounds.
An optional boolean pass must agree with them. Without bounds no pass is inferred.
An optional captions object maps figure roles to explanatory text.

Evidence defaults to {"status": "supplied"}. "measured" requires a method string.
"reloaded" additionally requires candidate, candidate_sha256 and nonempty checks:
[{"name": "RMS spot", "field": 0, "wavelength": 0.55, "unit": "um",
  "before_save": 1.23, "after_reload": 1.23, "tolerance": 1e-8}]. Checks must cover
every metric exactly once by name and all supplied field/wavelength/frequency/axis
conditions. Units must match; after_reload must equal that metric's reported value.
Check values and nonnegative tolerance must be finite and agree. The producer supplies
this evidence: rendering checks consistency, not file hashes or optical truth.
verdict and diagnosis remain authored interpretation, never automatic validation.
Optional import_assessment carries the shared import-fidelity result and warnings;
numerical_analysis_allowed=false prevents acceptance requirements from rendering.
Figure roles are laid out in the order layout, spot, ray_fan, opd_fan, field_curvature,
distortion, mtf, then any other roles in the order supplied; a role naming a PNG that
does not exist under the summary's directory is skipped, not an error. A metric's
"requirement" may give "min" and/or "max"; add optional "frequency" (cyc/mm) and "axis"
fields to a metric row for MTF-like conditions and they are folded into its requirement
text, e.g. "≥ 0.30 at 20 cyc/mm, tangential". A missing "verdict" renders as the line
"No verdict was written."

    uv run render_review.py --summary out/summary.json --out out/review.html --json

Exit codes: 0 ok, 2 usage, 4 the summary was missing, unreadable or malformed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100
from _lib.review_render import render_html, validate_summary  # noqa: E402, RUF100

TOOL = "render_review"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="render_review.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="example: uv run render_review.py --summary out/summary.json --out out/review.html --json")
    parser.add_argument("--summary", required=True, help="path to summary.json (see the schema above)")
    parser.add_argument("--out", required=True, help="path to write the rendered review .html")
    parser.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary_path = Path(args.summary)
    try:
        raw = summary_path.read_text(encoding="utf-8-sig")
    except OSError as e:
        cli.fail(f"could not read summary: {e}", cli.EXIT_ANALYSIS)
    try:
        data = json.loads(raw)
        validate_summary(data)
    except json.JSONDecodeError as e:
        cli.fail(f"could not parse summary JSON: {e}", cli.EXIT_ANALYSIS)
    except (ValueError, TypeError) as e:
        cli.fail(f"malformed summary: {e}", cli.EXIT_ANALYSIS)

    doc, stats = render_html(data, summary_path.resolve().parent)

    out_path = Path(args.out)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(doc, encoding="utf-8")
    except OSError as e:
        cli.fail(f"could not write output: {e}", cli.EXIT_ANALYSIS)

    env = cli.Envelope(
        TOOL, "render", 0,
        inputs={"summary": args.summary, "out": args.out},
        results={"out": str(out_path), "bytes": len(doc.encode("utf-8")), **stats},
        units={"bytes": "byte"},
        warnings=[f"figure(s) not found and skipped: {stats['figures_missing']}"] if stats["figures_missing"] else [],
        method="Static HTML render of a caller-supplied summary.json; no optical analysis is performed here.",
    )
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
