# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate and rank a local declared optical catalog; no network or model imports."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import catalog, cli  # noqa: E402, RUF100

WARNING = "Catalog metadata is user-declared; vendor accuracy, model compatibility and current availability are unverified"


def command(parser, args):
    index, index_hash = catalog.load_json(args.index)
    catalog.validate_index(index)
    hashes = {"index": index_hash}
    inputs = {"index": args.index}
    if args.subcommand == "validate":
        results = {"status": "valid", "entry_count": len(index["entries"]), "source_verification": "declared_only"}
    else:
        query, query_hash = catalog.load_json(args.query)
        hashes["query"] = query_hash
        inputs.update({"query": args.query, "constraints": query.get("constraints") if isinstance(query, dict) else None,
                       "limit": args.limit})
        results = catalog.match(index, query, limit=args.limit)
    return cli.Envelope("catalog", args.subcommand, 0, inputs=inputs, results=results,
                        units={"score": "dimensionless"}, warnings=[WARNING],
                        method="Inclusive hard bounds after explicit dimensional conversion; score = sum(weight*abs(value-target)/scale)/sum(weight) for targeted constraints, else zero. Lower score first, then vendor/part. No optical performance inference.",
                        provenance={"catalog_schema": 1, "catalog_inputs": hashes})


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)
    for name in ("validate", "match"):
        sub = subs.add_parser(name, parents=[cli.common_parser()],
                              epilog="Example: uv run catalog.py match --index catalog.json --query query.json --json")
        sub.add_argument("--index", required=True, help="local schema-1 catalog JSON")
        if name == "match":
            sub.add_argument("--query", required=True, help="local explicit-unit constraints JSON")
            sub.add_argument("--limit", type=cli.positive_int, default=10)
        sub.set_defaults(func=command, sub=sub)
    return parser


def main(argv=None):
    return cli.run(build_parser, argv)


if __name__ == "__main__":
    sys.exit(main())
