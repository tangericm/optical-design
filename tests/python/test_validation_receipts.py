"""Reassess complete validation evidence before exposing an accepted MCP result."""
import json

import pytest
from _lib.tool_jobs import JobManager
from test_optimization import run, setup
from test_optimization_validation import ValidationLens, validation
from test_tool_jobs import digest


@pytest.mark.parametrize('mutation', ['none', 'missing_baseline', 'wrong_candidate_vector',
                                    'wrong_baseline_vector', 'false_baseline_assessment'])
def test_validation_receipt_must_link_both_evaluations_to_original_and_saved_model(tmp_path, mutation):
    directory = tmp_path/'owned'
    inputs = directory/'inputs'
    inputs.mkdir(parents=True)
    model, raw, backend = setup(inputs, ValidationLens)
    separate = validation(.5)
    vpath = inputs/'validation.json'
    vpath.write_text(json.dumps(separate.data))
    report = run(model, raw, directory/'output', backend, validation_spec=separate)
    if mutation == 'missing_baseline':
        report['validation']['baseline'] = None
    elif mutation == 'wrong_candidate_vector':
        report['validation']['candidate']['parameters_mm'] = [999, 999]
    elif mutation == 'wrong_baseline_vector':
        report['validation']['baseline']['parameters_mm'] = [999, 999]
    elif mutation == 'false_baseline_assessment':
        report['validation']['baseline']['assessment']['passes'] = False
    for path in (directory/'output/report.json', directory/'stdout.log'):
        path.write_text(json.dumps(report))
    record = {'_directory': directory, 'output': str(directory/'output'), 'action': 'optimize',
              'returncode': 0, 'logs': {'stdout': str(directory/'stdout.log')},
              '_inputs': {'model': (model, digest(model), model.read_bytes()),
                          'validation_spec': (vpath, digest(vpath), vpath.read_bytes())},
              '_paths': {'model': model, 'validation_spec': vpath}}
    manager = JobManager(tmp_path, [inputs])
    if mutation == 'none':
        assert manager._validate(record)['status'] == 'improved'
    else:
        with pytest.raises(ValueError, match='validation'):
            manager._validate(record)
