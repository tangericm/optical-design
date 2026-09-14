# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "zospy==2.1.5", "pythonnet==3.1.0"]
# ///
"""Benchmark explicit Huygens/POP profiles on hashed copies of native models.

Example: uv run benchmark.py --manifest benchmark.json --out benchmark-run --json
Reference-free runs complete without claiming numerical validation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.native_worker import emit_report, in_worker, run_worker
from _lib.profile_benchmark import run_benchmark


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, help='strict schema_version 1 manifest; paths relative to this file')
    parser.add_argument('--out', required=True, help='new or empty output directory')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if not in_worker():
        return run_worker(Path(__file__).resolve(), sys.argv[1:] if argv is None else argv)
    try:
        report = run_benchmark(args.manifest, args.out)
        emit_report(report, as_json=args.json, summary=f"{report['status']}: {Path(args.out).resolve() / 'report.json'}")
        return 1 if report['status'] == 'benchmark_failed' else 0
    except ImportError as exc:
        print(f'Missing native dependency: {exc}. Use uv run benchmark.py with its pinned script dependencies.', file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f'Invalid benchmark input/result: {exc}', file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('Benchmark interrupted; inspect failure.json for restoration evidence.', file=sys.stderr)
        return 4
    except Exception as exc:  # noqa: BLE001 -- native engine failures have backend-specific types.
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 4


if __name__ == '__main__':
    sys.exit(main())
