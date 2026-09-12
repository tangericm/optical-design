# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare two JSON envelopes (tier vs tier, before vs after) with tolerances (Tier 0).

Exit 0 when every shared numeric value is within tolerance, 1 otherwise; 2 usage,
4 when an input file cannot be read or parsed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100

TOOL = "compare"


def flatten(d, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}{k}."))
    elif isinstance(d, (list, tuple)):
        for i, v in enumerate(d):
            out.update(flatten(v, f"{prefix}{i}."))
    elif isinstance(d, bool):
        return out
    elif isinstance(d, (int, float)):
        out[prefix[:-1]] = float(d)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compare.py", description=__doc__, parents=[cli.common_parser()],
                                     epilog="example: uv run compare.py before.json after.json --rtol 0.02")
    parser.add_argument("a")
    parser.add_argument("b")
    parser.add_argument("--rtol", type=float, default=0.01)
    parser.add_argument("--atol", type=float, default=0.0)
    parser.add_argument("--section", default="results", help="top-level key to compare (default results; use '' for all)")
    args = parser.parse_args(argv)

    try:
        da = json.loads(Path(args.a).read_text(encoding="utf-8"))
        db = json.loads(Path(args.b).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        cli.fail(f"could not parse JSON input: {e}", cli.EXIT_ANALYSIS)
    except OSError as e:
        cli.fail(f"could not read input: {e}", cli.EXIT_ANALYSIS)
    if args.section:
        da, db = {args.section: da.get(args.section, {})}, {args.section: db.get(args.section, {})}
    fa, fb = flatten(da), flatten(db)
    shared = sorted(set(fa) & set(fb))
    diffs, exceeded = {}, []
    for k in shared:
        x, y = fa[k], fb[k]
        absd = abs(x - y)
        rel = absd / abs(x) if x != 0 else (0.0 if absd == 0 else float("inf"))
        ok = absd <= args.atol + args.rtol * abs(x)
        diffs[k] = {"a": x, "b": y, "abs": absd, "rel": rel, "ok": ok}
        if not ok:
            exceeded.append(k)
    env = cli.Envelope(TOOL, "compare", 0,
                       inputs={"a": args.a, "b": args.b, "rtol": args.rtol, "atol": args.atol, "section": args.section},
                       results={"all_within_tolerance": not exceeded, "exceeded": exceeded, "diffs": diffs,
                                "only_in_a": sorted(set(fa) - set(fb)), "only_in_b": sorted(set(fb) - set(fa))},
                       units={}, method="|a−b| ≤ atol + rtol·|a| per shared numeric leaf",
                       warnings=[f"{len(exceeded)} value(s) exceed tolerance"] if exceeded else [])
    cli.emit(env, as_json=args.json)
    return 0 if not exceeded else 1


if __name__ == "__main__":
    sys.exit(main())
