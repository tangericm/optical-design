"""Keep native startup/shutdown text out of the CLI's machine-readable stdout."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RESULT_ENV = 'OPTICAL_DESIGN_WORKER_RESULT'


def in_worker():
    return RESULT_ENV in os.environ


def emit_report(report, *, as_json, summary):
    if in_worker():
        Path(os.environ[RESULT_ENV]).write_text(json.dumps(
            {'report': report, 'as_json': as_json, 'summary': summary}, allow_nan=False), encoding='utf-8')
    else:
        print(json.dumps(report, indent=2, allow_nan=False) if as_json else summary)


def _invalidate_artifact(argv, payload, reason):
    """Invalidate only the exact job receipt emitted by this child, never preexisting output."""
    output = None
    for i, arg in enumerate(argv):
        if arg == '--out' and i + 1 < len(argv):
            output = argv[i + 1]
        elif arg.startswith('--out='):
            output = arg[6:]
    if output is None or payload is None:
        return
    directory = Path(output).resolve()
    path = directory / 'report.json'
    if path.is_file():
        try:
            report = json.loads(path.read_text(encoding='utf-8'))
            if report != payload.get('report'):
                return
            report.update(status='failed', saved_candidate_verified=False, native_process_error=reason)
            if 'reference_validated' in report:
                report['reference_validated'] = False
            path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
            (directory / 'failure.json').write_text(json.dumps(
                {'status': 'failed', 'stage': 'native_process_shutdown', 'error': reason}, indent=2), encoding='utf-8')
            markdown = directory / 'report.md'
            if markdown.is_file():
                markdown.write_text('**INVALID RESULT: native process failed after analysis.**\n\n' +
                                    markdown.read_text(encoding='utf-8'), encoding='utf-8')
        except (OSError, ValueError) as exc:
            print(f'Could not invalidate native job receipt: {exc}', file=sys.stderr)


def run_worker(script, argv):
    """Same pinned interpreter, one owned native process, file result after full teardown."""
    with tempfile.TemporaryDirectory(prefix='optical-native-') as directory:
        result_path = Path(directory) / 'result.json'
        environment = dict(os.environ, **{RESULT_ENV: str(result_path)})
        result = subprocess.run([sys.executable, str(script), *argv], env=environment,
                                capture_output=True, text=True, errors='replace', check=False)
        if result.stdout:
            print(result.stdout, end='', file=sys.stderr)
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        if result_path.exists():
            payload = None
            try:
                payload = json.loads(result_path.read_text(encoding='utf-8'))
                if (not isinstance(payload, dict) or not isinstance(payload.get('report'), dict) or
                        type(payload.get('as_json')) is not bool or not isinstance(payload.get('summary'), str)):
                    raise ValueError('invalid native result structure')
                report = payload['report']
                if 'available' in report:
                    expected = 0 if report['available'] is True else 3
                else:
                    expected = {'improved': 0, 'requirements_met': 0, 'completed': 0,
                                'benchmark_passed': 0, 'benchmark_failed': 1,
                                'requirements_not_met': 1, 'no_acceptable_improvement': 1}.get(report.get('status'))
                if result.returncode != expected:
                    reason = f'native process exit {result.returncode} inconsistent with result; acceptance invalidated'
                    _invalidate_artifact(argv, payload, reason)
                    raise ValueError(reason)
            except (OSError, ValueError) as exc:
                print(f'Invalid native result: {exc}', file=sys.stderr)
                return 4
            print(json.dumps(payload['report'], indent=2, allow_nan=False) if payload['as_json'] else payload['summary'])
        elif result.returncode == 0:
            print('Native process exited without a result.', file=sys.stderr)
            return 4
        return result.returncode
