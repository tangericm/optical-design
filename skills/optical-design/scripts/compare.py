# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check equivalence of two JSON envelopes with tolerances (Tier 0).

Strict by default: require complete nonempty numeric coverage, compatible declared
units and identical supplied analysis identity. Curves require identical coordinates
and ordering; no interpolation. This checks equivalence, not design improvement.
Exit 0 on pass, 1 on differences/incomparability; 2 usage, 4 invalid input.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100
from _lib.comparison import compare_documents, flatten  # noqa: E402, F401, RUF100

TOOL = "compare"


def tolerance(text: str) -> float:
    value = float(text)
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError("tolerance must be finite and nonnegative")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compare.py", description=__doc__, parents=[cli.common_parser()],
                                     epilog="example: uv run compare.py before.json after.json --rtol 0.02")
    parser.add_argument("a")
    parser.add_argument("b")
    parser.add_argument("--rtol", type=tolerance, default=0.01)
    parser.add_argument("--atol", type=tolerance, default=0.0, help="absolute tolerance in each A metric's units")
    parser.add_argument("--section", default="results", help="top-level key to compare (default results; use '' for all)")
    parser.add_argument("--shared-only", action="store_true", help="exploratory shared numeric leaves only; ignores units/identity and never certifies equivalence")
    parser.add_argument("--require", action="append", default=[], metavar="METRIC", help="require a numeric leaf on both sides (repeatable; e.g. strehl or results.strehl)")
    args = parser.parse_args(argv)

    try:
        da = json.loads(Path(args.a).read_text(encoding="utf-8"))
        db = json.loads(Path(args.b).read_text(encoding="utf-8"))
        results = compare_documents(da, db, rtol=args.rtol, atol=args.atol, section=args.section,
                                    shared_only=args.shared_only, required=args.require)
    except json.JSONDecodeError as e:
        cli.fail(f"could not parse JSON input: {e}", cli.EXIT_ANALYSIS)
    except OSError as e:
        cli.fail(f"could not read input: {e}", cli.EXIT_ANALYSIS)
    except (ValueError, OverflowError) as e:
        cli.fail(f"invalid comparison input: {e}", cli.EXIT_ANALYSIS)
    warnings = list(results["incomparable_reasons"])
    if results["exceeded"]:
        warnings.append(f"{len(results['exceeded'])} value(s) exceed tolerance")
    if args.shared_only:
        warnings.append("Exploratory comparison ignores units and analysis identity; it does not certify equivalence.")
    env = cli.Envelope(TOOL, "compare", 0,
                       inputs={"a": args.a, "b": args.b, "rtol": args.rtol, "atol": args.atol, "section": args.section,
                               "shared_only": args.shared_only, "required": args.require},
                       results=results, units={},
                       method="|a−b| ≤ atol + rtol·|a| after converting b to a's declared units in strict mode; "
                              "rel is null when undefined or unrepresentable; no interpolation",
                       warnings=warnings)
    cli.emit(env, as_json=args.json)
    return 0 if results["all_within_tolerance"] else 1


if __name__ == "__main__":
    sys.exit(main())
