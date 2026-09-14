# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Paraxial first-order summary and gate for a .zmx or Optiland-native .json model.

Run this first, before any optimization. EFL, magnification and total track are
coupled by the paraxial relations -- a spec that fixes all three at once is often
already inconsistent, and a starting point that "looks right" surface-by-surface can
still trace to the wrong focal length. Frontier language models reasoning about a
prescription without a paraxial check have been measured 35-55% off on EFL (the
OptiAgent study, arXiv:2602.23761); this is the check that catches that before an
optimizer spends its budget chasing the wrong target.

Reports EFL, back focal length, current image distance, F/#, paraxial NA estimate, EPD,
entrance/exit pupil position and diameter,
magnification (finite conjugates only), total track, the Lagrange invariant, EFL at
each declared wavelength plus the chromatic focal shift, and, at the maximum field, the
image-space chief ray angle (telecentricity error) and chief ray height.

    uv run --python 3.11 --with optiland==0.6.2 first_order.py --model lens.zmx --json

With --spec, also gates the results against a small JSON object and exits 1 on failure:

    uv run --python 3.11 --with optiland==0.6.2 \\
        first_order.py --model lens.zmx --spec gate.json --json

gate.json:
    {"efl_mm": {"target": 50, "tol_pct": 1}, "f_number": {"max": 5.6},
     "total_track_mm": {"max": 80}, "telecentricity_deg": {"max": 0.5},
     "chromatic_shift_um": {"max": 100}}

Each rule may combine "min", "max", and/or "target" with "tol_pct" (percent tolerance
around target); every declared field must hold for that key to pass. Valid keys:
efl_mm, back_focal_length_mm, image_distance_mm, bfl_mm (corrected BFL alias),
f_number, na_image_paraxial, na_image (paraxial alias), epd_mm, total_track_mm,
chief_ray_angle_paraxial_deg, telecentricity_deg (paraxial alias), efl_spread_um,
chromatic_shift_um, chief_ray_height_mm, magnification, lagrange_invariant.

Exit codes: 0 pass (or no --spec given), 1 gate failed, 2 usage, 3 optiland missing,
4 could not load or trace the model.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100

TOOL = "first_order"
EXIT_GATE_FAILED = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="first_order.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="example: uv run --with optiland==0.6.2 first_order.py --model lens.zmx --json")
    parser.add_argument("--model", required=True, help=".zmx or Optiland-native .json prescription")
    parser.add_argument("--spec", help="JSON gate spec; see --help for the schema")
    parser.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cli.require("optiland", "install with: uv run --with optiland==0.6.2 first_order.py ...")
    from _lib import first_order as fo

    try:
        optic = fo.load_optic(args.model)
    except ValueError as e:
        cli.fail(f"could not load model: {e}", cli.EXIT_ANALYSIS)
    except OSError as e:
        cli.fail(f"could not read model: {e}", cli.EXIT_ANALYSIS)

    try:
        summary = fo.compute(optic)
    except (ValueError, ZeroDivisionError, IndexError) as e:
        cli.fail(f"could not trace paraxial model: {e}", cli.EXIT_ANALYSIS)

    results, units, warnings = summary["results"], summary["units"], list(summary["warnings"])
    gate = None
    if args.spec:
        try:
            spec = json.loads(Path(args.spec).read_text(encoding="utf-8-sig"))
            gate = fo.evaluate_gate(results, spec)
        except json.JSONDecodeError as e:
            cli.fail(f"could not parse JSON spec: {e}", cli.EXIT_ANALYSIS)
        except OSError as e:
            cli.fail(f"could not read spec: {e}", cli.EXIT_ANALYSIS)
        except ValueError as e:
            parser.error(str(e))
        results = {**results, "gate": gate}

    env = cli.Envelope(
        TOOL, "check", 1,
        inputs={"model": args.model, "spec": args.spec},
        results=results, units=units, warnings=warnings,
        method="Optiland 0.6.2 Paraxial module (marginal/chief ray traces, f1/f2/FNO/EPD/XPL/EPL, "
               "Lagrange invariant); BFL = last-vertex/image gap + F2 (image-relative back focus); "
               "NA = 1/(2 F#) is a paraxial estimate; telecentricity is the paraxial image-space chief ray angle "
               "at the field scaled to the system's declared maximum field; chromatic shift is "
               "max(EFL) - min(EFL) over the declared wavelengths, not a best-focus shift.",
    )
    cli.emit(env, as_json=args.json)
    if gate is not None and not gate["pass"]:
        return EXIT_GATE_FAILED
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
