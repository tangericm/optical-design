# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Audit, refocus, optimize, or tolerance a copied sequential model against explicit requirements.

Install a pinned optional engine using uv --with: optiland==0.6.2, or
zospy==2.1.5 and pythonnet==3.1.0 on licensed Windows. See references/design-workflow.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.design_contract import DesignSpec
from _lib.design_jobs import run_job
from _lib.native_worker import emit_report, in_worker, run_worker


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog='Example: uv run --with optiland==0.6.2 design.py audit --backend optiland --model lens.json --spec spec.json --out audit --json')
    parser.add_argument('action', choices=['inspect', 'edit', 'audit', 'refocus', 'optimize', 'tolerance', 'sensitivity'])
    parser.add_argument('--model', required=True)
    parser.add_argument('--spec', help='design specification; required except for inspect')
    parser.add_argument('--out', required=True, help='new or empty output directory')
    parser.add_argument('--backend', choices=['zos', 'optiland'], required=True)
    parser.add_argument('--tolerances', help='tolerance JSON; required for tolerance action')
    parser.add_argument('--variables', help='bounded variable JSON; required for optimize action')
    parser.add_argument('--changes', help='explicit expected/value cell changes; edit only')
    parser.add_argument('--perturbations', help='finite sensitivity steps; sensitivity only')
    parser.add_argument('--validation-spec', help='separate requirements checked after optimization; optimize only')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if (args.action != 'inspect') != (args.spec is not None):
        parser.error('--spec is required for every action except inspect')
    for name, action in [('changes', 'edit'), ('perturbations', 'sensitivity')]:
        if (args.action == action) != (getattr(args, name) is not None):
            parser.error(f'--{name} is required only with {action} action')
    if (args.action == 'tolerance') != (args.tolerances is not None):
        parser.error('--tolerances is required only with tolerance action')
    if (args.action == 'optimize') != (args.variables is not None):
        parser.error('--variables is required only with optimize action')
    if args.validation_spec is not None and args.action != 'optimize':
        parser.error('--validation-spec is supported only with optimize action')
    if args.backend == 'zos' and not in_worker():
        return run_worker(Path(__file__).resolve(), sys.argv[1:] if argv is None else argv)
    try:
        spec = (DesignSpec.from_dict(json.loads(Path(args.spec).read_text(encoding='utf-8-sig')))
                if args.spec else None)
        if args.backend == 'zos':
            from _lib.zos_backend import ZOSBackend
            factory = ZOSBackend
        else:
            from _lib.optiland_backend import OptilandBackend
            factory = OptilandBackend
        if args.action == 'inspect':
            from _lib.model_actions import run_inspect_job
            report = run_inspect_job(args.model, args.out, factory)
        elif args.action == 'edit':
            from _lib.model_actions import run_edit_job
            changes = json.loads(Path(args.changes).read_text(encoding='utf-8-sig'))
            report = run_edit_job(args.model, spec, args.out, factory, changes)
        elif args.action == 'sensitivity':
            from _lib.sensitivity import run_sensitivity_job
            perturbations = json.loads(Path(args.perturbations).read_text(encoding='utf-8-sig'))
            report = run_sensitivity_job(args.model, spec, args.out, factory, perturbations)
        elif args.action == 'tolerance':
            from _lib.tolerancing import run_tolerance_job
            tolerance = json.loads(Path(args.tolerances).read_text(encoding='utf-8-sig'))
            report = run_tolerance_job(args.model, spec, args.out, factory, tolerance)
        elif args.action == 'optimize':
            from _lib.optimization import run_optimization_job
            variables = json.loads(Path(args.variables).read_text(encoding='utf-8-sig'))
            validation = (DesignSpec.from_dict(json.loads(Path(args.validation_spec).read_text(encoding='utf-8-sig')))
                          if args.validation_spec else None)
            report = run_optimization_job(args.model, spec, args.out, factory, variables, validation_spec=validation)
        else:
            report = run_job(args.model, spec, args.out, factory, action=args.action)
        emit_report(report, as_json=args.json,
                    summary=f"{report['status']}: {Path(args.out).resolve() / 'report.json'}")
        return 0 if report['status'] in {'requirements_met', 'improved', 'inspected', 'applied', 'completed'} else 1
    except ImportError as exc:
        print(f'Missing optional backend dependency: {exc}. Use uv run --with optiland==0.6.2, or --with zospy==2.1.5 --with pythonnet==3.1.0.', file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print('Job interrupted; inspect failure.json for restoration evidence.', file=sys.stderr)
        return 4
    except Exception as exc:  # noqa: BLE001 -- native engines expose backend-specific exceptions at CLI boundary
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 4


if __name__ == '__main__':
    sys.exit(main())
