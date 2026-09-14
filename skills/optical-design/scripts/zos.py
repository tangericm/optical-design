# /// script
# requires-python = ">=3.11"
# dependencies = ["zospy==2.1.5", "pythonnet==3.1.0"]
# ///
"""Probe an owned standalone OpticStudio connection and close it immediately."""
import argparse
import sys
from pathlib import Path

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.native_worker import emit_report, in_worker, run_worker


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog='Example: uv run zos.py check --json')
    parser.add_argument('action', choices=['check'])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if not in_worker():
        return run_worker(Path(__file__).resolve(), sys.argv[1:] if argv is None else argv)
    try:
        from _lib.zos_backend import capability_check
        report = capability_check()
    except Exception as exc:  # noqa: BLE001 -- capability probe must report unavailable native environments
        report = {'available': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    emit_report(report, as_json=args.json, summary=str(report))
    return 0 if report['available'] else 3


if __name__ == '__main__':
    sys.exit(main())
