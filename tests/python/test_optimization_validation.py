"""A search optimum can fail a separately declared validation field."""
import copy
import json
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec
from test_optimization import CoupledLens, run, setup


def validation(minimum=.6):
    return DesignSpec.from_dict({'schema': '1', 'fields': [2], 'wavelengths': [1],
        'frequencies_cyc_per_mm': [50], 'requirements': [
            {'id': 'unseen-field', 'metric': 'mtf', 'field': 2, 'wavelength': 1,
             'frequency': 50, 'axis': 'tangential', 'unit': '1', 'min': minimum}],
        'analysis': {'sampling': 128}})


class ValidationLens(CoupledLens):
    def __init__(self, model):
        super().__init__(model)
        self.analysis_fields = []

    def evaluate(self, spec):
        self.analysis_fields.append(copy.deepcopy(spec.data['fields']))
        if spec.data['fields'] == [2]:
            self.calls += 1
            return [{'metric': 'mtf', 'field': 2, 'wavelength': 1, 'frequency': 50,
                     'axis': 'tangential', 'unit': '1', 'value': .9-self.state['x']/200}]
        return super().evaluate(spec)


@pytest.mark.parametrize('minimum,accepted', [(.5, True), (.6, False)])
def test_saved_search_winner_is_gated_by_validation_without_adaptive_research(tmp_path, minimum, accepted):
    model, raw, backend = setup(tmp_path, ValidationLens)
    result = run(model, raw, tmp_path/'out', backend, validation_spec=validation(minimum))
    assert result['status'] == ('improved' if accepted else 'validation_failed')
    assert result['saved_candidate_verified'] is accepted
    assert result['validation']['status'] == ('passed' if accepted else 'requirements_not_met')
    assert result['validation']['baseline']['assessment']['passes']
    assert result['validation']['candidate']['assessment']['passes'] is accepted
    assert backend.analysis_fields[-2:] == [[2], [2]]
    assert all(fields == [1] for fields in backend.analysis_fields[:-2])
    assert result['evaluations'] == backend.calls <= raw['budget']['max_evaluations']
    assert result['validation']['evaluations'] == 2
    assert result['baseline_restored'] and result['source_unchanged']
    if accepted:
        assert result['candidate'] and 'candidate_model' in result['artifacts']
    else:
        assert result['candidate'] is None
        assert result['rejected_candidate']['assessment']['passes']
        assert 'candidate_model' not in result['artifacts']
        assert Path(result['artifacts']['rejected_candidate_model']).is_file()
        assert not (tmp_path/'out/candidate-model.json').exists()


def test_validation_does_not_replace_search_objective_and_budget_is_shared(tmp_path):
    model, raw, backend = setup(tmp_path, ValidationLens, budget=7)
    result = run(model, raw, tmp_path/'out', backend, validation_spec=validation(.1))
    assert result['evaluations'] == backend.calls == 7
    assert result['search']['verification_evaluations_reserved'] == 4
    assert result['candidate']['objective_value'] > result['baseline']['objective_value']


def test_no_search_improvement_does_not_claim_validation(tmp_path):
    model, raw, backend = setup(tmp_path, ValidationLens)
    raw['minimum_gain'] = 100
    result = run(model, raw, tmp_path/'out', backend, validation_spec=validation())
    assert result['status'] == 'no_acceptable_improvement'
    assert result['validation']['status'] == 'not_run_no_candidate'
    assert result['validation']['evaluations'] == 0
    assert [2] not in backend.analysis_fields


@pytest.mark.parametrize('failure', ['raise', 'mutate', 'missing'])
def test_failed_validation_cannot_accept_candidate_and_restores_source(tmp_path, failure):
    class Broken(ValidationLens):
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            if spec.data['fields'] == [2] and self.state['x'] > 60:
                if failure == 'raise':
                    raise RuntimeError('held-out analysis failed')
                if failure == 'mutate':
                    self.state['aperture'] = 999
                if failure == 'missing':
                    return []
            return rows
    model, raw, backend = setup(tmp_path, Broken)
    if failure == 'missing':
        result = run(model, raw, tmp_path/'out', backend, validation_spec=validation(.1))
        assert result['status'] == 'validation_failed'
    else:
        with pytest.raises(RuntimeError):
            run(model, raw, tmp_path/'out', backend, validation_spec=validation(.1))
        receipt = json.loads((tmp_path/'out/failure.json').read_text())
        assert receipt['baseline_restored'] and receipt['source_unchanged']
        assert receipt['validation']['status'] == 'analysis_failed'
        assert not (tmp_path/'out/report.json').exists()
    assert backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}


def test_validation_spec_is_frozen_before_backend_execution(tmp_path):
    frozen = validation(.1)
    class ChangesExternalSpec(ValidationLens):
        def __enter__(self):
            frozen.data['requirements'][0]['min'] = 1
            return super().__enter__()
    model, raw, backend = setup(tmp_path, ChangesExternalSpec)
    result = run(model, raw, tmp_path/'out', backend, validation_spec=frozen)
    assert result['status'] == 'improved'
    assert result['validation']['spec']['requirements'][0]['min'] == .1
    assert json.loads((tmp_path/'out/validation-spec.json').read_text()) == result['validation']['spec']


def test_validation_objective_and_focus_are_rejected_before_output(tmp_path):
    model, raw, backend = setup(tmp_path, ValidationLens)
    for key, value in [('objective', raw['objective']), ('focus', {'min_mm': 1, 'max_mm': 2})]:
        candidate = validation().data
        # Use a field-valid metric identity when adding an objective.
        if key == 'objective':
            value = dict(value, field=2)
        candidate[key] = value
        with pytest.raises(ValueError, match='validation'):
            run(model, raw, tmp_path/'out', backend, validation_spec=DesignSpec.from_dict(candidate))
    assert not (tmp_path/'out').exists()


def test_cli_validation_is_only_supported_for_optimize(run):
    import design
    for action in ('audit', 'refocus', 'tolerance'):
        args = [action, '--model', 'x', '--spec', 'x', '--out', 'x', '--backend', 'optiland',
                '--validation-spec', 'x']
        if action == 'tolerance':
            args += ['--tolerances', 'x']
        code, _, error = run(design.main, args)
        assert code == 2 and 'only' in error and 'validation' in error


def test_backend_cannot_relax_frozen_validation_requirements(tmp_path):
    class Relaxer(ValidationLens):
        def evaluate(self, spec):
            if spec.data['fields'] == [2]:
                spec.data['requirements'][0]['min'] = 0
            return super().evaluate(spec)
    model, raw, backend = setup(tmp_path, Relaxer)
    with pytest.raises(RuntimeError, match='validation specification'):
        run(model, raw, tmp_path/'out', backend, validation_spec=validation())
    failure = json.loads((tmp_path/'out/failure.json').read_text())
    assert failure['validation']['spec']['requirements'][0]['min'] == .6
    assert failure['baseline_restored'] and failure['source_unchanged']


@pytest.mark.parametrize('mode', ['timeout', 'cancel'])
def test_late_validation_is_rejected_and_cleanup_runs_outside_budget(tmp_path, monkeypatch, mode):
    import _lib.optimization as optimizer
    clock, stop = [0], [False]
    monkeypatch.setattr(optimizer.time, 'monotonic', lambda: clock[0])
    class Late(ValidationLens):
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            if spec.data['fields'] == [2]:
                clock[0] += 2
                stop[0] = mode == 'cancel'
            return rows
    model, raw, backend = setup(tmp_path, Late)
    separate = validation(.1)
    separate.data['budget']['timeout_s'] = 1 if mode == 'timeout' else 60
    with pytest.raises((TimeoutError, InterruptedError)):
        run(model, raw, tmp_path/'out', backend, validation_spec=separate, cancelled=lambda: stop[0])
    failure = json.loads((tmp_path/'out/failure.json').read_text())
    assert failure['baseline_restored'] and failure['source_unchanged']
    assert failure['validation']['status'] == 'analysis_failed'
    assert failure['validation']['evaluations'] == 1
    assert failure['evaluations'] == backend.calls
