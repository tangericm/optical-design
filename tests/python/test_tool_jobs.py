"""Real subprocess fixtures exercise transport ownership without optical engines."""
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from _lib import tool_jobs


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def process_stopped(pid):
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x00100000, False, pid)
        if not handle:
            return True
        try:
            return kernel.WaitForSingleObject(handle, 5000) == 0
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        return True


@pytest.fixture
def jobs(tmp_path, monkeypatch):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    model = inputs / 'model.json'
    model.write_text('{}')
    spec = inputs / 'spec.json'
    spec.write_text('{}')
    script = tmp_path / 'fixture_cli.py'
    script.write_text('''import argparse, hashlib, json, pathlib, subprocess, sys, time
p = argparse.ArgumentParser()
p.add_argument('action')
for name in ('model', 'spec', 'out', 'backend', 'tolerances', 'variables'): p.add_argument('--'+name)
p.add_argument('--json', action='store_true')
a = p.parse_args()
out = pathlib.Path(a.out); out.mkdir()
cfg = json.loads(pathlib.Path(a.spec).read_text())
if cfg.get('child'):
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(90)'])
    (out / 'child.pid').write_text(str(child.pid))
if cfg.get('sleep'): time.sleep(90)
baseline = out / 'baseline.json'; baseline.write_text('{}')
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r = dict(schema='1', action=a.action, status=cfg.get('status', 'requirements_met'),
         source=dict(path=a.model, sha256=sha(a.model)), source_unchanged=True,
         baseline_restored=True, saved_candidate_verified=False,
         artifacts=dict(baseline_model=str(baseline), baseline_sha256=sha(baseline)))
r.update(cfg.get('override', {}))
if not cfg.get('no_report'): (out / 'report.json').write_text(json.dumps(r))
if cfg.get('failure'): (out / 'failure.json').write_text('{}')
if cfg.get('tamper'): baseline.write_text('tampered')
if not cfg.get('no_stdout'): print(json.dumps({} if cfg.get('mismatch') else r))
sys.exit(cfg.get('exit', 0))
''')
    monkeypatch.setattr(tool_jobs, 'DESIGN_SCRIPT', script)
    manager = tool_jobs.JobManager(tmp_path / 'workspace', [inputs])
    request = {'action': 'audit', 'backend': 'optiland', 'model': str(model),
                   'model_sha256': digest(model), 'spec': str(spec), 'spec_sha256': digest(spec)}
    yield manager, request, spec
    manager.close()


def wait(manager, identity):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        state = manager.status(identity)
        if state['state'] != 'running':
            return state
        time.sleep(.03)
    pytest.fail('owned fixture process did not finish')


def configure(request, spec, **config):
    spec.write_text(json.dumps(config))
    request['spec_sha256'] = digest(spec)


@pytest.mark.parametrize('field,value', [('action', 'shell'), ('backend', 'exec'),
    ('model_sha256', '0'*64), ('spec_sha256', '0'*64)])
def test_rejects_unallowed_operations_and_stale_inputs(jobs, field, value):
    manager, request, _ = jobs
    request[field] = value
    with pytest.raises(ValueError):
        manager.start(**request)
    assert list(manager.workspace.iterdir()) == []


def test_rejects_paths_outside_declared_roots(jobs, tmp_path):
    manager, request, _ = jobs
    outside = tmp_path / 'outside.json'
    outside.write_text('{}')
    request.update(model=str(outside), model_sha256=digest(outside))
    with pytest.raises(ValueError, match='root'):
        manager.start(**request)


def test_no_arbitrary_arguments_or_output_paths(jobs):
    manager, request, _ = jobs
    for extra in ({'argv': ['--help']}, {'out': '../escape'}, {'command': 'whoami'}):
        with pytest.raises(TypeError):
            manager.start(**request, **extra)


def test_job_identity_completion_and_owned_artifacts(jobs):
    manager, request, _ = jobs
    started = manager.start(**request)
    state = wait(manager, started['job_id'])
    assert state['state'] == 'completed'
    assert state['optical_accepted'] is True
    result = manager.results(started['job_id'])
    assert result['report']['source']['sha256'] == request['model_sha256']
    assert Path(result['output']).is_relative_to(manager.workspace)
    assert Path(result['logs']['stdout']).is_file()
    with pytest.raises(ValueError, match='unknown'):
        manager.status('../report.json')


@pytest.mark.parametrize('config', [{'exit': 4}, {'no_report': True}, {'no_stdout': True},
    {'mismatch': True}, {'failure': True}, {'tamper': True},
    {'override': {'baseline_restored': False}}, {'override': {'source_unchanged': False}},
    {'status': 'improved'}, {'status': 'completed'}])
def test_partial_or_disagreeing_evidence_never_accepted(jobs, config):
    manager, request, spec = jobs
    configure(request, spec, **config)
    identity = manager.start(**request)['job_id']
    state = wait(manager, identity)
    assert state['state'] == 'failed'
    assert state['optical_accepted'] is False
    assert manager.results(identity)['report'] is None


def test_completed_negative_optical_result_is_not_process_failure(jobs):
    manager, request, spec = jobs
    configure(request, spec, status='requirements_not_met', exit=1)
    identity = manager.start(**request)['job_id']
    state = wait(manager, identity)
    assert state['state'] == 'completed'
    assert state['optical_accepted'] is False


def test_serialized_jobs_cancel_and_shutdown_retain_logs(jobs):
    manager, request, spec = jobs
    configure(request, spec, sleep=True)
    identity = manager.start(**request)['job_id']
    with pytest.raises(RuntimeError, match='active'):
        manager.start(**request)
    assert manager.results(identity)['report'] is None
    assert manager.cancel(identity)['state'] == 'cancelled'
    assert manager.cancel(identity)['state'] == 'cancelled'
    second = manager.start(**request)['job_id']
    manager.close()
    assert manager.status(second)['state'] == 'cancelled'
    assert Path(manager.results(second)['logs']['stderr']).is_file()


def test_cancel_kills_only_owned_tree(jobs):
    manager, request, spec = jobs
    configure(request, spec, child=True, sleep=True)
    unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(90)'])
    try:
        identity = manager.start(**request)['job_id']
        output = Path(manager.results(identity)['output'])
        deadline = time.monotonic() + 10
        while not (output / 'child.pid').exists() and time.monotonic() < deadline:
            time.sleep(.03)
        child_pid = int((output / 'child.pid').read_text())
        manager.cancel(identity)
        assert unrelated.poll() is None
        assert process_stopped(child_pid)
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_changed_original_invalidates_finished_result(jobs):
    manager, request, _ = jobs
    identity = manager.start(**request)['job_id']
    assert wait(manager, identity)['state'] == 'completed'
    Path(request['model']).write_text('changed')
    result = manager.results(identity)
    assert result['state'] == 'failed'
    assert result['report'] is None


def test_input_symlink_cannot_escape_root(jobs, tmp_path):
    manager, request, _ = jobs
    outside = tmp_path / 'outside.json'
    outside.write_text('{}')
    link = Path(request['model']).parent / 'link.json'
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip('host cannot create symlinks')
    request['model'] = str(link)
    with pytest.raises(ValueError, match='root'):
        manager.start(**request)


def test_artifact_receipt_cannot_point_outside_output(jobs, tmp_path):
    manager, request, spec = jobs
    outside = tmp_path / 'outside.json'
    outside.write_text('{}')
    configure(request, spec, override={'artifacts': {'baseline_model': str(outside),
                                                   'baseline_sha256': digest(outside)}})
    identity = manager.start(**request)['job_id']
    assert wait(manager, identity)['state'] == 'failed'


@pytest.mark.parametrize('override', [{'source': []}, {'source': {'path': 'wrong', 'sha256': '0'*64}},
                                     {'schema': 'unexpected'}])
def test_malformed_receipt_fails_closed(jobs, override):
    manager, request, spec = jobs
    configure(request, spec, override=override)
    identity = manager.start(**request)['job_id']
    assert wait(manager, identity)['state'] == 'failed'


@pytest.mark.parametrize('action,field', [('tolerance', 'tolerances'), ('optimize', 'variables')])
def test_action_specific_inputs_are_required_and_hashed(jobs, action, field):
    manager, request, spec = jobs
    request['action'] = action
    with pytest.raises(ValueError):
        manager.start(**request)
    request[field] = str(spec)
    request[field + '_sha256'] = '0'*64
    with pytest.raises(ValueError, match='stale'):
        manager.start(**request)
    request[field + '_sha256'] = digest(spec)
    identity = manager.start(**request)['job_id']
    assert identity


def test_concurrent_start_cannot_bypass_single_active_job(jobs):
    manager, request, spec = jobs
    configure(request, spec, sleep=True)
    def attempt():
        try:
            return manager.start(**request)['job_id']
        except RuntimeError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))
    assert sum(identity is not None for identity in results) == 1


def test_changed_output_receipt_invalidates_previously_completed_result(jobs):
    manager, request, _ = jobs
    identity = manager.start(**request)['job_id']
    state = wait(manager, identity)
    assert state['state'] == 'completed'
    (Path(state['output']) / 'baseline.json').write_text('changed after completion')
    assert manager.results(identity)['state'] == 'failed'
