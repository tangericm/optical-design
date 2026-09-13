"""Analytic anchors and fail-closed sensitivity evidence."""
import copy
import json
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec
from test_optimization import CoupledLens, setup


def config():
    return {'schema': '1', 'parameters': [
        {'surface': 1, 'parameter': 'radius_mm', 'step_mm': .2},
        {'surface': 2, 'parameter': 'thickness_mm', 'step_mm': .01}]}


def test_extreme_finite_differences_preserve_nonlinearity_ratio():
    from _lib.sensitivity import _difference
    assert _difference(0., -8e307, 1e308, 2.)['nonlinearity_indicator'] == pytest.approx(1/9)


def test_composite_sensitivity_retains_each_merit_term(tmp_path):
    model, raw, backend = setup(tmp_path, AnalyticLens)
    raw['objective'] = {'direction': 'minimize', 'aggregation': 'weighted_rms', 'terms': [
        {'metric': 'total_track_mm', 'unit': 'mm', 'target': 40, 'scale': 2, 'weight': 1}]}
    result = run(model, raw, tmp_path/'out', backend)
    for entry in [result['baseline'], *result['trials']]:
        evidence = entry['objective_breakdown']
        assert evidence['unit'] == '1' and len(evidence['terms']) == 1
        assert evidence['value'] == entry['objective_value']


class AnalyticLens(CoupledLens):
    def evaluate(self, spec):
        self.calls += 1
        x, y = self.state['x'], self.state['y']
        return [{'metric': 'mtf', 'field': 1, 'wavelength': 1, 'frequency': 50,
                 'axis': 'tangential', 'unit': '1', 'value': x*x + 3*y,
                 'analysis': {'method': 'analytic'}},
                {'metric': 'total_track_mm', 'unit': 'mm', 'value': 2*x + y}]


def run(model, raw, out, backend, parameters=None, **kwargs):
    from _lib.sensitivity import run_sensitivity_job
    return run_sensitivity_job(model, DesignSpec.from_dict(raw), out, lambda _: backend,
                               config() if parameters is None else parameters, **kwargs)


def test_analytic_derivatives_nonlinearity_rankings_and_exact_trials(tmp_path):
    model, raw, backend = setup(tmp_path, AnalyticLens)
    original = model.read_bytes()
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['action'] == 'sensitivity' and result['status'] == 'completed'
    assert result['evaluations'] == backend.calls == 5
    assert result['source_unchanged'] and result['baseline_restored'] and backend.closed
    assert model.read_bytes() == original
    assert backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}
    assert len(result['history']) == 5 and len(result['trials']) == 4
    assert [r['parameters_mm'] for r in result['trials']] == [
        [19.8, 1.8], [20.2, 1.8], [20, 1.79], [20, 1.81]]
    first, second = result['sensitivities']
    mtf = first['metrics'][0]
    assert mtf['derivative_per_mm'] == pytest.approx(40)
    assert mtf['declared_step_effect'] == pytest.approx(8)
    assert mtf['second_difference'] == pytest.approx(.08)
    assert mtf['second_derivative_per_mm2'] == pytest.approx(2)
    assert mtf['nonlinearity_indicator'] == pytest.approx(.005)
    assert second['metrics'][0]['derivative_per_mm'] == pytest.approx(3)
    assert second['metrics'][0]['second_difference'] == pytest.approx(0, abs=1e-12)
    assert first['objective']['derivative_per_mm'] == pytest.approx(40)
    assert len(result['rankings']) == 2
    for ranking in result['rankings']:
        assert len(ranking['parameters']) == 2
        assert all(r['metric_key'] == ranking['metric_key'] and r['unit'] == ranking['unit']
                   for r in ranking['parameters'])
    assert result['candidate'] is None
    assert Path(result['artifacts']['baseline_model']).is_file()
    assert result['artifacts']['baseline_sha256']


def test_optional_objective_and_failed_requirement_still_complete(tmp_path):
    model, raw, backend = setup(tmp_path, AnalyticLens)
    raw.pop('objective')
    raw['requirements'][0]['min'] = 1e9
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'completed' and not result['baseline']['assessment']['passes']
    assert all('objective' not in r for r in result['sensitivities'])


@pytest.mark.parametrize('step', [0, -1, True, float('nan'), float('inf'), '1'])
def test_invalid_steps_precede_artifacts(tmp_path, step):
    model, raw, backend = setup(tmp_path)
    parameters = config()
    parameters['parameters'][0]['step_mm'] = step
    with pytest.raises(ValueError):
        run(model, raw, tmp_path / 'out', backend, parameters)
    assert backend.calls == 0 and not (tmp_path / 'out').exists()


@pytest.mark.parametrize('mode', ['radius_zero', 'radius_crossing', 'thickness_zero', 'underflow', 'image', 'duplicate'])
def test_invalid_domain_or_cells_fail(tmp_path, mode):
    model, raw, backend = setup(tmp_path, AnalyticLens)
    parameters = config()
    if mode in {'radius_zero', 'radius_crossing'}:
        parameters['parameters'][0]['step_mm'] = 20 if mode == 'radius_zero' else 21
    if mode == 'thickness_zero':
        parameters['parameters'][1]['step_mm'] = 1.8
    if mode == 'underflow':
        parameters['parameters'][0]['step_mm'] = 1e-30
    if mode == 'image':
        parameters['parameters'][0]['surface'] = 3
    if mode == 'duplicate':
        parameters['parameters'][1] = copy.deepcopy(parameters['parameters'][0])
    with pytest.raises(ValueError):
        run(model, raw, tmp_path / 'out', backend, parameters)
    assert backend.calls == 0
    if mode != 'duplicate':
        assert backend.closed


@pytest.mark.parametrize('mutation', ['ignored', 'coupled', 'fixed', 'evaluation_fixed',
                                     'missing', 'unit', 'metadata', 'duplicate', 'nonfinite', 'spec'])
def test_untrustworthy_trials_fail_and_restore(tmp_path, mutation):
    class Broken(AnalyticLens):
        def set_parameter(self, surface, name, value):
            if mutation != 'ignored':
                super().set_parameter(surface, name, value)
            if mutation == 'coupled':
                self.state['y'] += .1
            if mutation == 'fixed':
                self.state['aperture'] += 1

        def evaluate(self, spec):
            rows = super().evaluate(spec)
            if self.calls > 1:
                if mutation == 'evaluation_fixed': self.state['aperture'] += 1
                if mutation == 'missing': rows.pop(0)
                if mutation == 'unit': rows[0]['unit'] = 'mm'
                if mutation == 'metadata': rows[0]['analysis']['method'] = 'different'
                if mutation == 'duplicate': rows.append(copy.deepcopy(rows[0]))
                if mutation == 'nonfinite': rows[0]['value'] = float('nan')
                if mutation == 'spec': spec.data['analysis']['sampling'] = 256
            return rows

    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises((RuntimeError, ValueError)):
        run(model, raw, tmp_path / 'out', backend)
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['baseline_restored'] and failure['source_unchanged'] and backend.closed
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('mode', ['deadline', 'cancel', 'analysis', 'save', 'reload', 'close', 'cleanup'])
def test_failed_calls_count_attempts_restore_and_teardown(tmp_path, monkeypatch, mode):
    import _lib.sensitivity as module
    clock = [0]
    monkeypatch.setattr(module.time, 'monotonic', lambda: clock[0])

    class Broken(AnalyticLens):
        def evaluate(self, spec):
            if mode == 'analysis':
                self.calls += 1
                raise RuntimeError('analysis failed')
            rows = super().evaluate(spec)
            if mode == 'deadline': clock[0] += 1000
            return rows

        def save(self, path):
            if mode == 'save': raise RuntimeError('save failed')
            super().save(path)

        def load(self, path):
            if mode == 'cleanup' and self.calls >= 5: raise RuntimeError('restore failed')
            super().load(path)
            if mode == 'reload': self.state['x'] += 1

        def __exit__(self, *args):
            super().__exit__(*args)
            if mode == 'close': raise RuntimeError('close failed')

    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises((RuntimeError, InterruptedError, TimeoutError)):
        run(model, raw, tmp_path / 'out', backend, cancelled=lambda: mode == 'cancel')
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['evaluations'] == backend.calls
    assert failure['baseline_restored'] == (mode not in {'reload', 'cleanup'})
    assert backend.closed and not (tmp_path / 'out/report.json').exists()


def test_evaluation_budget_counts_baseline_and_both_sides(tmp_path):
    model, raw, backend = setup(tmp_path, AnalyticLens, budget=7)
    parameters = config()
    # Four unique cells exist; extend the test engine's available parameter map.
    parameters['parameters'] += [
        {'surface': 1, 'parameter': 'thickness_mm', 'step_mm': .1},
        {'surface': 2, 'parameter': 'radius_mm', 'step_mm': .1}]
    with pytest.raises(ValueError, match='budget'):
        run(model, raw, tmp_path / 'out', backend, parameters)
    assert backend.calls == 0


def test_no_metric_in_baseline_fails_instead_of_omission(tmp_path):
    class Empty(AnalyticLens):
        def evaluate(self, spec):
            self.calls += 1
            return []
    model, raw, backend = setup(tmp_path, Empty)
    with pytest.raises(ValueError, match='metric|measurement'):
        run(model, raw, tmp_path / 'out', backend)
    assert backend.closed and backend.calls == 1


@pytest.mark.parametrize('filename', ['spec.json', 'perturbations.json', 'source_snapshot.json', 'baseline-model.json'])
def test_artifact_mutation_cannot_get_success_receipt(tmp_path, filename):
    class Tamper(AnalyticLens):
        def __exit__(self, *args):
            super().__exit__(*args)
            path = tmp_path / 'out' / filename
            path.write_text(path.read_text() + ' ')
    model, raw, backend = setup(tmp_path, Tamper)
    with pytest.raises(RuntimeError, match='changed'):
        run(model, raw, tmp_path / 'out', backend)
    assert not (tmp_path / 'out/report.json').exists()


def test_late_cancellation_keeps_prior_trials_and_attempt_count(tmp_path):
    model, raw, backend = setup(tmp_path, AnalyticLens)
    with pytest.raises(InterruptedError):
        run(model, raw, tmp_path / 'out', backend, cancelled=lambda: backend.calls >= 3)
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['evaluations'] == 3 and len(failure['history']) == 2
    assert failure['baseline_restored'] and backend.closed


def test_grid_cutoff_change_is_physical_but_requested_metric_stays_fixed(tmp_path):
    class Grid(AnalyticLens):
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            rows[0]['analysis']['frequency_range_cyc_per_mm'] = [0, 100 + self.state['x']]
            return rows
    model, raw, backend = setup(tmp_path, Grid)
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'completed'
    assert result['trials'][0]['measurements'][0]['analysis']['frequency_range_cyc_per_mm'] == [0, 119.8]


def test_external_inputs_cannot_change_job_configuration(tmp_path):
    from _lib.sensitivity import run_sensitivity_job
    model, raw, backend = setup(tmp_path, AnalyticLens)
    specification = DesignSpec.from_dict(raw)
    parameters = config()
    def factory(_):
        specification.data['budget']['max_evaluations'] = 0
        parameters['parameters'][0]['step_mm'] = 10
        return backend
    result = run_sensitivity_job(model, specification, tmp_path / 'out', factory, parameters)
    assert result['evaluations'] == 5
    assert result['perturbations']['parameters'][0]['step_mm'] == .2
    assert result['spec']['budget']['max_evaluations'] == 101


@pytest.mark.parametrize('bad', [{}, {'schema': '1', 'parameters': []},
    {'schema': '1', 'parameters': [{'surface': True, 'parameter': 'radius_mm', 'step_mm': 1}]},
    {'schema': '1', 'parameters': [{'surface': 0, 'parameter': 'radius_mm', 'step_mm': 1}]},
    {'schema': '1', 'parameters': [{'surface': 1, 'parameter': 'conic', 'step_mm': 1}]},
    {'schema': '1', 'parameters': [{'surface': 1, 'parameter': 'radius_mm', 'step_mm': 1, 'extra': 1}]},
    {'schema': '1', 'parameters': [{'surface': 1, 'parameter': 'radius_mm', 'step_mm': 1}] * 17}])
def test_invalid_config_rejected_before_output(tmp_path, bad):
    model, raw, backend = setup(tmp_path)
    with pytest.raises(ValueError):
        run(model, raw, tmp_path / 'out', backend, bad)
    assert not (tmp_path / 'out').exists()
