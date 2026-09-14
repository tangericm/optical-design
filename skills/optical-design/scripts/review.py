# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create an offline HTML/Markdown review from a local optical job receipt."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.review_report import render_review


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True, help='report.json or diagnostic failure.json')
    parser.add_argument('--out', required=True, help='new review directory')
    parser.add_argument('--json', action='store_true', help='print the provenance manifest as JSON')
    args = parser.parse_args(argv)
    try:
        manifest = render_review(args.report, args.out)
    except (ValueError, OSError) as exc:
        print(f'review: {exc}', file=sys.stderr)
        return 4
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(f"Review created: {Path(args.out).resolve() / 'report.html'} (recorded outcome: {manifest['status']})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
