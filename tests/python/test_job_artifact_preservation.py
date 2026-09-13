"""Artifacts and input semantics must remain those actually evaluated before teardown."""
import copy
import json

import pytest
from _lib.design_contract import DesignSpec
from _lib.design_jobs import run_job
from _lib.optimization import run_optimization_job
from _lib.tolerancing import run_tolerance_job
from test_design_contract import base_spec
from test_design_jobs import AnalyticFocus
from test_optimization import CoupledLens, config, setup
from test_optimization_validation import ValidationLens, validation
from test_tolerancing import AffineBackend


def _tamper(directory, name):
    paths = list(directory.glob(name))
    if paths:
        paths[0].write_bytes(paths[0].read_bytes() + b'\nTAMPERED')


def _failure(out):
    failure = json.loads((out / 'failure.json').read_text())
    assert failure.get('error')
    if (out / 'report.json').exists():
        report = json.loads((out / 'report.json').read_text())
        assert report['status'] == 'failed' and not report['saved_candidate_verified']


@pytest.mark.parametrize('name', ['baseline-model.*', 'candidate-model.*', 'source_snapshot.*',
                                 'baseline.json', 'spec.json', 'variables.json', 'validation-spec.json'])
def test_optimize_rejects_teardown_artifact_changes(tmp_path, name):
    out = tmp_path / 'out'
    class Corrupt(ValidationLens):
        def __exit__(self, *args):
            super().__exit__(*args)
            _tamper(out, name)
    model, raw, backend = setup(tmp_path, Corrupt)
    with pytest.raises(RuntimeError, match='changed|artifact'):
        run_optimization_job(model, DesignSpec.from_dict(raw), out, lambda _: backend,
                             config(), validation_spec=validation(.5))
    _failure(out)


@pytest.mark.parametrize('action,name', [
    ('audit', 'baseline-model.*'), ('audit', 'source_snapshot.*'), ('audit', 'spec.json'),
    ('refocus', 'baseline-model.*'), ('refocus', 'candidate-model.*'),
    ('refocus', 'source_snapshot.*'), ('refocus', 'spec.json'), ('refocus', 'source'),
    ('audit', 'report.json'), ('refocus', 'baseline.json')])
def test_audit_refocus_check_evidence_after_teardown(tmp_path, action, name):
    out, source = tmp_path / 'out', tmp_path / 'source.lens'
    source.write_text('60')
    class Corrupt(AnalyticFocus):
        def __exit__(self, *args):
            super().__exit__(*args)
            if name == 'source':
                source.write_text('47')
            else:
                _tamper(out, name)
    with pytest.raises(RuntimeError, match='changed|artifact'):
        run_job(source, DesignSpec.from_dict(base_spec()), out, Corrupt, action=action)
    _failure(out)


def _tolerance(tmp_path):
    source = tmp_path / 'source.json'
    source.write_text('{"radius_mm":10,"thickness_mm":2}')
    spec = DesignSpec.from_dict({'schema': '1', 'fields': [1], 'wavelengths': [1],
        'requirements': [{'id': 'efl', 'metric': 'efl_mm', 'unit': 'mm', 'max': 10.5}]})
    tolerance = {'schema': '1', 'samples': 2, 'seed': 0, 'perturbations': [
        {'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform', 'half_width_mm': 1}]}
    return source, spec, tolerance


@pytest.mark.parametrize('name', ['baseline.*', 'source_snapshot.*', 'spec.json', 'tolerance.json'])
def test_tolerance_rejects_teardown_artifact_changes(tmp_path, name):
    source, spec, tolerance = _tolerance(tmp_path)
    out = tmp_path / 'out'
    class Corrupt(AffineBackend):
        def __exit__(self, *args):
            super().__exit__(*args)
            _tamper(out, name)
    with pytest.raises(RuntimeError, match='changed|artifact'):
        run_tolerance_job(source, spec, out, Corrupt, tolerance)
    _failure(out)


@pytest.mark.parametrize('action', ['audit', 'refocus', 'optimize', 'tolerance'])
def test_backend_cannot_mutate_declared_requirements(tmp_path, action):
    out = tmp_path / 'out'
    def mutate(spec):
        spec.data['requirements'][0]['min'] = -1e9
        spec.data['requirements'][0]['max'] = 1e9
    if action in {'audit', 'refocus'}:
        class Mutates(AnalyticFocus):
            def evaluate(self, spec):
                mutate(spec)
                return super().evaluate(spec)
        source = tmp_path / 'source.lens'
        source.write_text('60')
        runner = lambda: run_job(source, DesignSpec.from_dict(base_spec()), out, Mutates, action=action)
    elif action == 'optimize':
        class Mutates(CoupledLens):
            def evaluate(self, spec):
                mutate(spec)
                return super().evaluate(spec)
        source, raw, backend = setup(tmp_path, Mutates)
        runner = lambda: run_optimization_job(source, DesignSpec.from_dict(raw), out, lambda _: backend, config())
    else:
        class Mutates(AffineBackend):
            def evaluate(self, spec):
                mutate(spec)
                return super().evaluate(spec)
        source, spec, tolerance = _tolerance(tmp_path)
        runner = lambda: run_tolerance_job(source, spec, out, Mutates, tolerance)
    with pytest.raises(RuntimeError, match='specification changed'):
        runner()
    _failure(out)


@pytest.mark.parametrize('action', ['refocus', 'optimize', 'tolerance'])
def test_reused_measurement_buffer_does_not_rewrite_prior_evidence(tmp_path, action):
    saved_first = []
    def reuse(backend, rows):
        if not hasattr(backend, 'buffer'):
            backend.buffer = rows
            saved_first.extend(copy.deepcopy(rows))
        else:
            backend.buffer[:] = rows
        return backend.buffer
    if action == 'refocus':
        class Buffer(AnalyticFocus):
            def evaluate(self, spec):
                return reuse(self, super().evaluate(spec))
        source = tmp_path / 'source.lens'
        source.write_text('60')
        result = run_job(source, DesignSpec.from_dict(base_spec()), tmp_path / 'out', Buffer, action=action)
        actual = result['baseline']['measurements']
    elif action == 'optimize':
        class Buffer(CoupledLens):
            def evaluate(self, spec):
                return reuse(self, super().evaluate(spec))
        source, raw, backend = setup(tmp_path, Buffer)
        result = run_optimization_job(source, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, config())
        actual = result['baseline']['measurements']
    else:
        class Buffer(AffineBackend):
            def evaluate(self, spec):
                return reuse(self, super().evaluate(spec))
        source, spec, tolerance = _tolerance(tmp_path)
        result = run_tolerance_job(source, spec, tmp_path / 'out', Buffer, tolerance)
        actual = result['nominal']['measurements']
    assert actual == saved_first
