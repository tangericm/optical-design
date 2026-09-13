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


def design_spec(**controls):
    return {'schema': '1', 'name': json.dumps(controls), 'fields': [1], 'wavelengths': [1],
            'requirements': [{'id': 'efl', 'metric': 'efl_mm', 'unit': 'mm', 'min': 40}],
            'objective': {'metric': 'efl_mm', 'direction': 'minimize'},
            'focus': {'min_mm': 1, 'max_mm': 100}}


def action_config(action):
    if action == 'optimize':
        return {'schema': '1', 'variables': [
            {'surface': 1, 'parameter': 'radius_mm', 'min_mm': 10, 'max_mm': 100}]}
    return {'schema': '1', 'samples': 2, 'seed': 1, 'perturbations': [
        {'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform', 'half_width_mm': .1}]}


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
    spec.write_text(json.dumps(design_spec()))
    script = tmp_path / 'fixture_cli.py'
    script.write_text('import sys\nsys.path.insert(0, ' + repr(str(tool_jobs.DESIGN_SCRIPT.parent)) + ')\n' + '''import argparse, hashlib, json, pathlib, subprocess, sys, time
from _lib.design_contract import DesignSpec, assess
from _lib.tolerancing import _validate as validate_tolerance
p = argparse.ArgumentParser()
p.add_argument('action')
for name in ('model', 'spec', 'out', 'backend', 'tolerances', 'variables', 'validation-spec'): p.add_argument('--'+name)
p.add_argument('--json', action='store_true')
a = p.parse_args()
out = pathlib.Path(a.out); out.mkdir()
spec = DesignSpec.from_dict(json.loads(pathlib.Path(a.spec).read_text()))
cfg = json.loads(spec.data['name'])
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
rows = [dict(metric='efl_mm', unit='mm', value=30 if r['status'] == 'requirements_not_met' else 50)]
r['baseline'] = dict(measurements=rows, assessment=assess(spec, rows))
r['spec'] = spec.data
spath = out / 'spec.json'; spath.write_text(json.dumps(spec.data))
r['spec_sha256'] = sha(spath)
for input_name, report_name in [('variables', 'variables'), ('tolerances', 'tolerance')]:
    filename = getattr(a, input_name)
    if filename:
        data = json.loads(pathlib.Path(filename).read_text())
        if report_name == 'tolerance': data = validate_tolerance(data, spec)
        if cfg.get('wrong_config'): data['unexpected'] = True
        cpath = out / (report_name + '.json'); cpath.write_text(json.dumps(data))
        r[report_name] = data
        r[report_name + '_sha256'] = sha(cpath)
if cfg.get('wrong_spec'):
    r['spec'] = dict(spec.data, requirements=[dict(id='efl', metric='efl_mm', unit='mm', min=-100)])
    spath.write_text(json.dumps(r['spec'])); r['spec_sha256'] = sha(spath)
    r['baseline']['assessment'] = assess(DesignSpec.from_dict(r['spec']), rows)
if a.action == 'tolerance':
    r['nominal'] = r.pop('baseline')
    if cfg.get('nominal_failure'):
        r['nominal'] = dict(status='analysis_failed', error='analysis unavailable', measurements=[],
                            assessment=dict(passes=False, requirements=[]))
    if cfg.get('legacy_hashes'):
        r.pop('spec_sha256'); r.pop('tolerance_sha256')
r.update(cfg.get('override', {}))
if a.validation_spec and not cfg.get('omit_validation'):
    validation_spec = json.loads(pathlib.Path(a.validation_spec).read_text())
    vpath = out / 'validation-spec.json'; vpath.write_text(json.dumps(validation_spec))
    r['validation'] = dict(spec=validation_spec, spec_sha256=sha(vpath), status='not_run_no_candidate')
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
    spec.write_text(json.dumps(design_spec(**config)))
    request['spec_sha256'] = digest(spec)


def test_optional_validation_input_is_allowlisted_hashed_and_preserved(jobs):
    from _lib.design_contract import DesignSpec
    from test_optimization_validation import validation
    manager, request, spec = jobs
    vpath = spec.parent/'validation.json'
    vpath.write_text(json.dumps(validation().data))
    variables = spec.parent / 'variables.json'
    variables.write_text(json.dumps(action_config('optimize')))
    request.update(action='optimize', variables=str(variables), variables_sha256=digest(variables),
                   validation_spec=str(vpath), validation_spec_sha256=digest(vpath))
    configure(request, spec, status='no_acceptable_improvement', exit=1)
    identity = manager.start(**request)['job_id']
    state = wait(manager, identity)
    assert state['state'] == 'completed' and not state['optical_accepted']
    report = manager.results(identity)['report']
    assert report['validation']['spec'] == DesignSpec.from_dict(validation().data).data
    vpath.write_text('{}')
    assert manager.results(identity)['state'] == 'failed'


def test_requested_validation_cannot_be_silently_dropped_from_receipt(jobs):
    from test_optimization_validation import validation
    manager, request, spec = jobs
    vpath = spec.parent/'validation.json'
    vpath.write_text(json.dumps(validation().data))
    variables = spec.parent / 'variables.json'
    variables.write_text(json.dumps(action_config('optimize')))
    request.update(action='optimize', variables=str(variables), variables_sha256=digest(variables),
                   validation_spec=str(vpath), validation_spec_sha256=digest(vpath))
    configure(request, spec, status='no_acceptable_improvement', exit=1, omit_validation=True)
    identity = manager.start(**request)['job_id']
    assert wait(manager, identity)['state'] == 'failed'


@pytest.mark.parametrize('change', ['wrong_action', 'missing_hash', 'missing_path', 'stale_hash'])
def test_validation_input_rejects_bad_contract_before_job_creation(jobs, change):
    manager, request, spec = jobs
    request.update(action='optimize', variables=str(spec), variables_sha256=digest(spec),
                   validation_spec=str(spec), validation_spec_sha256=digest(spec))
    if change == 'wrong_action':
        request['action'] = 'audit'
        del request['variables'], request['variables_sha256']
    elif change == 'missing_hash':
        del request['validation_spec_sha256']
    elif change == 'missing_path':
        del request['validation_spec']
    else:
        request['validation_spec_sha256'] = '0'*64
    with pytest.raises(ValueError):
        manager.start(**request)
    assert not list(manager.workspace.iterdir())


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


@pytest.mark.parametrize('override', [
    {'baseline': None}, {'baseline': {'assessment': {'passes': True, 'requirements': []}}},
    {'baseline': {'measurements': [{'metric': 'efl_mm', 'unit': 'mm', 'value': 0}],
                  'assessment': {'passes': True, 'requirements': []}}},
    {'spec': {}},
])
def test_matching_output_channels_cannot_forge_optical_acceptance(jobs, override):
    manager, request, spec = jobs
    configure(request, spec, override=override)
    identity = manager.start(**request)['job_id']
    result = wait(manager, identity)
    assert result['state'] == 'failed' and not result['optical_accepted']


@pytest.mark.parametrize('action,status,code', [('audit', 'requirements_not_met', 1),
    ('refocus', 'no_acceptable_improvement', 1), ('optimize', 'no_acceptable_improvement', 1),
    ('tolerance', 'completed', 0)])
def test_honest_negative_receipts_remain_completed(jobs, action, status, code):
    manager, request, spec = jobs
    request['action'] = action
    if action in {'optimize', 'tolerance'}:
        field = 'variables' if action == 'optimize' else 'tolerances'
        path = spec.parent / (field + '.json')
        path.write_text(json.dumps(action_config(action)))
        request.update({field: str(path), field + '_sha256': digest(path)})
    configure(request, spec, status=status, exit=code, legacy_hashes=action == 'tolerance')
    result = wait(manager, manager.start(**request)['job_id'])
    assert result['state'] == 'completed', result['error']
    assert not result['optical_accepted']


@pytest.mark.parametrize('action', ['audit', 'refocus', 'optimize', 'tolerance'])
def test_self_consistent_forged_spec_is_bound_to_original_requested_spec(jobs, action):
    manager, request, spec = jobs
    request['action'] = action
    if action in {'optimize', 'tolerance'}:
        field = 'variables' if action == 'optimize' else 'tolerances'
        path = spec.parent / (field + '.json')
        path.write_text(json.dumps(action_config(action)))
        request.update({field: str(path), field + '_sha256': digest(path)})
    status = {'audit': 'requirements_met', 'refocus': 'no_acceptable_improvement',
              'optimize': 'no_acceptable_improvement', 'tolerance': 'completed'}[action]
    configure(request, spec, status=status, exit=int(action in {'refocus', 'optimize'}), wrong_spec=True)
    result = wait(manager, manager.start(**request)['job_id'])
    assert result['state'] == 'failed' and 'spec' in result['error']


@pytest.mark.parametrize('action', ['optimize', 'tolerance'])
def test_matching_report_and_config_snapshot_cannot_change_requested_config(jobs, action):
    manager, request, spec = jobs
    request['action'] = action
    field = 'variables' if action == 'optimize' else 'tolerances'
    path = spec.parent / (field + '.json')
    path.write_text(json.dumps(action_config(action)))
    request.update({field: str(path), field + '_sha256': digest(path)})
    configure(request, spec, status='completed' if action == 'tolerance' else 'no_acceptable_improvement',
              exit=int(action == 'optimize'), wrong_config=True)
    result = wait(manager, manager.start(**request)['job_id'])
    assert result['state'] == 'failed' and 'snapshot' in result['error']


def test_tolerance_nominal_analysis_failure_remains_diagnostic_completion(jobs):
    manager, request, spec = jobs
    path = spec.parent / 'tolerances.json'
    path.write_text(json.dumps(action_config('tolerance')))
    request.update(action='tolerance', tolerances=str(path), tolerances_sha256=digest(path))
    configure(request, spec, status='completed', nominal_failure=True)
    result = wait(manager, manager.start(**request)['job_id'])
    assert result['state'] == 'completed' and not result['optical_accepted'], result['error']


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
