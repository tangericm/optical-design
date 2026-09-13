"""New job contracts at real CLI and owned-process boundaries."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
from _lib.tool_jobs import JobManager

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'skills/optical-design/assets'
CLI = ROOT / 'skills/optical-design/scripts/design.py'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.mark.parametrize('action,extra', [('audit', {}), ('inspect', {'spec': 'missing'}),
    ('edit', {}), ('sensitivity', {})])
def test_action_inputs_fail_before_job_creation(tmp_path, action, extra):
    model = tmp_path / 'model.json'
    model.write_text('{}')
    with JobContext(tmp_path) as manager:
        with pytest.raises(ValueError):
            manager.start(action=action, backend='optiland', model=str(model),
                          model_sha256=digest(model), **extra)
        assert not list(manager.workspace.iterdir())


class JobContext:
    def __init__(self, root):
        self.manager = JobManager(root/'jobs', [root, ASSETS])

    def __enter__(self):
        return self.manager

    def __exit__(self, *_):
        self.manager.close()


def test_inspection_cli_needs_no_design_spec(tmp_path):
    pytest.importorskip('optiland')
    result = subprocess.run([sys.executable, str(CLI), 'inspect', '--backend', 'optiland',
        '--model', str(ASSETS/'portable-singlet.json'), '--out', str(tmp_path/'out'), '--json'],
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['status'] == 'inspected'
    assert report['baseline']['inspection']['surfaces']
    assert report['source_unchanged'] and report['baseline_restored']


def test_sensitivity_owned_job_cannot_drop_config(tmp_path):
    pytest.importorskip('optiland')
    config = tmp_path/'perturbations.json'
    config.write_text(json.dumps({'schema': '1', 'parameters': [
        {'surface': 1, 'parameter': 'radius_mm', 'step_mm': .01}]}))
    with JobContext(tmp_path) as manager:
        request = {'action': 'sensitivity', 'backend': 'optiland'}
        for name, path in [('model', ASSETS/'portable-singlet.json'),
                           ('spec', ASSETS/'refocus-spec.json'), ('perturbations', config)]:
            request[name], request[name+'_sha256'] = str(path), digest(path)
        identity = manager.start(**request)['job_id']
        deadline = time.monotonic() + 30
        while manager.status(identity)['state'] == 'running' and time.monotonic() < deadline:
            time.sleep(.05)
        result = manager.results(identity)
        assert result['state'] == 'completed', result
        assert not result['optical_accepted']
        assert result['report']['sensitivities']
        # Tampering both channels cannot bypass config binding.
        report = result['report']
        report['perturbations']['parameters'][0]['step_mm'] = .02
        payload = json.dumps(report)
        (Path(result['output'])/'report.json').write_text(payload)
        Path(result['logs']['stdout']).write_text(payload)
        assert manager.results(identity)['state'] == 'failed'
