"""Allowlisted, serialized CLI jobs. The MCP transport never owns an optical engine."""
from __future__ import annotations

import ctypes
import hashlib
import importlib.metadata
import json
import math
import os
import signal
import subprocess
import sys
import threading
import uuid
from pathlib import Path

DESIGN_SCRIPT = Path(__file__).resolve().parents[1] / 'design.py'
ACTIONS = {'audit', 'refocus', 'tolerance', 'optimize'}
BACKENDS = {'optiland', 'zos'}
EXPECTED = {'audit': {'requirements_met': 0, 'requirements_not_met': 1},
            'refocus': {'improved': 0, 'no_acceptable_improvement': 1},
            'optimize': {'improved': 0, 'no_acceptable_improvement': 1, 'validation_failed': 1},
            'tolerance': {'completed': 0}}
# Gate the owned child until it belongs to our Windows job object. No user code/argv.
_GATE = "import runpy,sys; token=sys.stdin.buffer.read(1); assert token==b'G'; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(path, root):
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError('path escapes declared root')
    return resolved


class _WindowsJob:
    """Kernel ownership includes descendants and survives original child exit."""
    def __init__(self, pid):
        from ctypes import wintypes as w

        class Basic(ctypes.Structure):
            _fields_ = [('user', ctypes.c_int64), ('process', ctypes.c_int64),
                        ('flags', w.DWORD), ('min_ws', ctypes.c_size_t),
                        ('max_ws', ctypes.c_size_t), ('active', w.DWORD),
                        ('affinity', ctypes.c_size_t), ('priority', w.DWORD),
                        ('scheduling', w.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in
                        ('read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]

        class Extended(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', ctypes.c_size_t),
                        ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t),
                        ('peak_job', ctypes.c_size_t)]

        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {'CreateJobObjectW': ([ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
                      'SetInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
                      'OpenProcess': ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
                      'AssignProcessToJobObject': ([w.HANDLE, w.HANDLE], w.BOOL),
                      'CloseHandle': ([w.HANDLE], w.BOOL)}
        for name, (args, result) in signatures.items():
            function = getattr(kernel, name)
            function.argtypes, function.restype = args, result
        self.kernel, self.handle = kernel, kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            info = Extended()
            info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            process = kernel.OpenProcess(0x0101, False, pid)  # SET_QUOTA | TERMINATE
            if not process:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                if not kernel.AssignProcessToJobObject(self.handle, process):
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                kernel.CloseHandle(process)
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


class JobManager:
    """One host-owned workspace and declared read roots for one server session.

    The operator must keep these directories private from untrusted local writers.
    This is a tool/API confinement boundary, not an OS sandbox for engine plugins.
    """
    def __init__(self, workspace, input_roots):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.input_roots = [Path(root).resolve(strict=True) for root in input_roots]
        if not self.input_roots or not all(root.is_dir() for root in self.input_roots):
            raise ValueError('at least one input directory root is required')
        self._jobs = {}
        self._lock = threading.RLock()
        self._closed = False

    def capabilities(self):
        versions = {}
        for name in ('mcp', 'numpy', 'optiland', 'zospy', 'pythonnet'):
            try:
                versions[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                versions[name] = None
        return {'actions': sorted(ACTIONS), 'backends': sorted(BACKENDS),
                'workspace': str(self.workspace), 'input_roots': list(map(str, self.input_roots)),
                'max_active_jobs': 1, 'transport': 'stdio', 'dependency_versions': versions,
                'engine_policy': 'same interpreter; install pinned optional engine at server launch',
                'acceptance_policy': 'complete matching CLI receipt, exit, source and artifact hashes'}

    def _input(self, path, expected):
        resolved = Path(path).resolve(strict=True)
        if not any(resolved.is_relative_to(root) for root in self.input_roots):
            raise ValueError('input path escapes declared root')
        if not resolved.is_file():
            raise ValueError('input must be a regular file')
        if (not isinstance(expected, str) or len(expected) != 64 or
                any(c not in '0123456789abcdef' for c in expected)):
            raise ValueError('expected SHA256 must be 64 lowercase hexadecimal characters')
        data = resolved.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('stale input SHA256; refresh the input before starting')
        return resolved, expected, data

    def start(self, *, action, backend, model, model_sha256, spec, spec_sha256,
              tolerances=None, tolerances_sha256=None, variables=None, variables_sha256=None,
              validation_spec=None, validation_spec_sha256=None):
        with self._lock:
            if self._closed:
                raise RuntimeError('server has closed')
            if action not in ACTIONS or backend not in BACKENDS:
                raise ValueError('operation or backend is not allowlisted')
            for identity in self._jobs:
                if self.status(identity)['state'] == 'running':
                    raise RuntimeError('one job is already active')
            inputs = {'model': self._input(model, model_sha256),
                      'spec': self._input(spec, spec_sha256)}
            for name, path, sha, required in (
                    ('tolerances', tolerances, tolerances_sha256, action == 'tolerance'),
                    ('variables', variables, variables_sha256, action == 'optimize')):
                if required != (path is not None and sha is not None) or (
                        not required and (path is not None or sha is not None)):
                    raise ValueError(f'{name} path and hash required only for its action')
                if required:
                    inputs[name] = self._input(path, sha)
            if validation_spec is not None or validation_spec_sha256 is not None:
                if action != 'optimize' or validation_spec is None or validation_spec_sha256 is None:
                    raise ValueError('validation_spec path and hash are supported together only for optimize')
                inputs['validation_spec'] = self._input(validation_spec, validation_spec_sha256)
            # Inputs are copied from the exact verified bytes; CLI never loads a live source.
            identity = uuid.uuid4().hex
            directory = self.workspace / identity
            directory.mkdir()
            _inside(directory, self.workspace)
            snapshots = directory / 'inputs'
            snapshots.mkdir()
            output = directory / 'output'
            argv = [sys.executable, '-u', '-c', _GATE, str(DESIGN_SCRIPT), action,
                    '--backend', backend, '--out', str(output), '--json']
            paths = {}
            for name, (source, sha, data) in inputs.items():
                target = snapshots / (name + source.suffix)
                target.write_bytes(data)
                paths[name] = target
                argv.extend(['--' + name.replace('_', '-'), str(target)])
            stdout_path, stderr_path = directory / 'stdout.log', directory / 'stderr.log'
            record = {'job_id': identity, 'state': 'running', 'action': action, 'backend': backend,
                      'output': str(output), 'logs': {'stdout': str(stdout_path), 'stderr': str(stderr_path)},
                      'optical_accepted': False, 'returncode': None, 'error': None,
                      'report': None, '_inputs': inputs, '_paths': paths, '_directory': directory,
                      '_process': None, '_tree': None}
            self._jobs[identity] = record
            try:
                environment = dict(os.environ)
                environment.pop('OPTICAL_DESIGN_WORKER_RESULT', None)
                # Native scratch stays in the owned workspace too.
                scratch = directory / 'temp'
                scratch.mkdir()
                environment.update(TEMP=str(scratch), TMP=str(scratch), TMPDIR=str(scratch))
                with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
                    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                               cwd=directory, env=environment, shell=False,
                                               start_new_session=os.name != 'nt',
                                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                record['_process'] = process
                if os.name == 'nt':
                    record['_tree'] = _WindowsJob(process.pid)
                process.stdin.write(b'G')
                process.stdin.close()
            except BaseException:
                self._stop(record)
                record.update(state='failed', error='could not start owned CLI process')
                raise
            return self._public(record)

    def _record(self, identity):
        if identity not in self._jobs:
            raise ValueError('unknown job identity for this server session')
        return self._jobs[identity]

    def _stop(self, record):
        process = record['_process']
        if record['_tree'] is not None:
            record['_tree'].close()
        elif process is not None and os.name != 'nt':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process is not None:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            if process.stdin and not process.stdin.closed:
                process.stdin.close()

    def _validate(self, record):
        directory = _inside(record['_directory'], self.workspace)
        output = _inside(record['output'], directory)
        if (output / 'failure.json').exists():
            raise ValueError('failure receipt exists; partial result rejected')
        report_path = _inside(output / 'report.json', output)
        report = json.loads(report_path.read_text(encoding='utf-8'))
        stdout = _inside(record['logs']['stdout'], directory)
        emitted = json.loads(stdout.read_text(encoding='utf-8'))
        if report != emitted:
            raise ValueError('CLI stdout and report receipt disagree')
        if (not isinstance(report, dict) or report.get('schema') != '1' or
                report.get('action') != record['action']):
            raise ValueError('report schema or action does not match owned job')
        expected_exit = EXPECTED[record['action']].get(report.get('status'))
        if expected_exit is None or record['returncode'] != expected_exit:
            raise ValueError('CLI exit and report status disagree')
        if report.get('source_unchanged') is not True or report.get('baseline_restored') is not True:
            raise ValueError('source preservation or restoration not verified')
        for name, (source, sha, _) in record['_inputs'].items():
            if not any(source.resolve(strict=True).is_relative_to(root) for root in self.input_roots):
                raise ValueError('input escaped root after job launch')
            if _hash(source) != sha or _hash(_inside(record['_paths'][name], directory)) != sha:
                raise ValueError('input changed after job launch; result invalidated')
        source = report.get('source', {})
        if (not isinstance(source, dict) or source.get('path') != str(record['_paths']['model']) or
                source.get('sha256') != record['_inputs']['model'][1]):
            raise ValueError('report source does not match owned snapshot')
        artifacts = report.get('artifacts', {})
        if not isinstance(artifacts, dict) or 'baseline_model' not in artifacts:
            raise ValueError('missing baseline artifact')
        for name, path in artifacts.items():
            if name.endswith('_model'):
                actual = _inside(path, output)
                if _hash(actual) != artifacts.get(name[:-6] + '_sha256'):
                    raise ValueError('artifact hash does not match receipt')
        if report['status'] == 'improved' and (
                report.get('saved_candidate_verified') is not True or 'candidate_model' not in artifacts):
            raise ValueError('saved improvement is not verified')
        if 'validation_spec' in record['_inputs']:
            from _lib.design_contract import DesignSpec, assess, finite
            expected = DesignSpec.from_dict(json.loads(record['_inputs']['validation_spec'][2].decode('utf-8-sig')))
            validation = report.get('validation')
            if not isinstance(validation, dict) or validation.get('spec') != expected.data:
                raise ValueError('requested validation specification missing or changed in receipt')
            vpath = _inside(output / 'validation-spec.json', output)
            if (_hash(vpath) != validation.get('spec_sha256') or
                    json.loads(vpath.read_text(encoding='utf-8')) != expected.data):
                raise ValueError('validation snapshot does not match receipt and input')
            required = {'improved': 'passed', 'validation_failed': 'requirements_not_met',
                        'no_acceptable_improvement': 'not_run_no_candidate'}[report['status']]
            if validation.get('status') != required:
                raise ValueError('validation outcome inconsistent with optical acceptance')
            if required != 'not_run_no_candidate':
                for name, selected in [('baseline', report.get('baseline')),
                                       ('candidate', report.get('candidate') if required == 'passed'
                                        else report.get('rejected_candidate'))]:
                    measured = validation.get(name)
                    if (not isinstance(measured, dict) or not isinstance(selected, dict) or
                            not isinstance(measured.get('measurements'), list)):
                        raise ValueError(f'validation {name} measurements or model evidence missing')  # noqa: TRY004 -- malformed serialized receipt
                    actual, wanted = measured.get('parameters_mm'), selected.get('parameters_mm')
                    if (not isinstance(actual, list) or not isinstance(wanted, list) or
                            not actual or len(actual) != len(wanted) or any(not math.isclose(
                                finite(a, 'validation parameter'), finite(b, 'model parameter'),
                                rel_tol=1e-12, abs_tol=1e-12) for a, b in zip(actual, wanted))):
                        raise ValueError(f'validation {name} vector differs from model evidence')
                    assessment = assess(expected, measured['measurements'])
                    if measured.get('assessment') != assessment:
                        raise ValueError(f'validation {name} assessment does not match measurements')
                if assessment['passes'] != (required == 'passed') or validation.get('evaluations') != 2:
                    raise ValueError('validation measurements do not substantiate claimed result')
            if required == 'requirements_not_met' and (
                    report.get('candidate') is not None or report.get('saved_candidate_verified') is not False
                    or 'candidate_model' in artifacts or 'rejected_candidate_model' not in artifacts):
                raise ValueError('rejected validation candidate is not quarantined')
        # Reject NaN/Infinity even if a permissive JSON parser accepted it.
        json.dumps(report, allow_nan=False)
        return report

    @staticmethod
    def _public(record):
        return {key: value for key, value in record.items() if not key.startswith('_') and key != 'report'}

    def status(self, job_id):
        with self._lock:
            record = self._record(job_id)
            if record['state'] == 'running':
                process = record['_process']
                code = process.poll()
                if code is not None:
                    record['returncode'] = code
                    self._stop(record)  # release tree, including surviving descendants
                    record['state'] = 'completed'
            if record['state'] == 'completed':
                try:
                    record['report'] = self._validate(record)
                    record['optical_accepted'] = record['report']['status'] in {'requirements_met', 'improved'}
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    record.update(state='failed', report=None, optical_accepted=False, error=str(exc))
            return self._public(record)

    def results(self, job_id):
        with self._lock:
            result = self.status(job_id)
            return dict(result, report=self._record(job_id)['report'])

    def cancel(self, job_id):
        with self._lock:
            record = self._record(job_id)
            self.status(job_id)
            if record['state'] == 'running':
                self._stop(record)
                record.update(state='cancelled', report=None, optical_accepted=False,
                              returncode=record['_process'].returncode,
                              error='owned process tree cancelled; partial artifacts are diagnostic only')
            return self._public(record)

    def close(self):
        with self._lock:
            for identity in self._jobs:
                self.cancel(identity)
            self._closed = True
