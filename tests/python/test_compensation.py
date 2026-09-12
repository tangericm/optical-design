"""Paired tolerance compensation against a known analytic focus model."""
import copy
import json

import pytest
from _lib.design_contract import DesignSpec
from _lib.tolerancing import run_tolerance_job
from test_tolerancing import AffineBackend


class FocusBackend(AffineBackend):
    def inspect(self):
        result = super().inspect()
        result['focus_mm'] = self.state['thickness_mm']
        result['invariants']['radius_mm'] = self.state['radius_mm']
        return result

    def set_focus(self, value):
        self.set_parameter(1, 'thickness_mm', value)

    def evaluate(self, _spec):
        return [{'metric': 'rms_spot_um', 'field': 1, 'wavelength': 1, 'unit': 'um',
                 'value': (self.state['thickness_mm'] - (2 + self.state['radius_mm'] - 10)) ** 2}]


@pytest.fixture
def setup(tmp_path):
    source = tmp_path / 'source.json'
    source.write_text('{"radius_mm":10,"thickness_mm":2}')
    spec = DesignSpec.from_dict({'schema': '1', 'fields': [1], 'wavelengths': [1],
        'requirements': [{'id': 'spot', 'metric': 'rms_spot_um', 'unit': 'um',
                          'field': 1, 'wavelength': 1, 'max': .005}],
        'objective': {'metric': 'rms_spot_um', 'field': 1, 'wavelength': 1, 'direction': 'minimize'}})
    config = {'schema': '1', 'samples': 5, 'seed': 0, 'sensitivity_steps': [-1, 1],
        'perturbations': [{'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform', 'half_width_mm': 1}],
        'compensator': {'surface': 1, 'parameter': 'thickness_mm', 'min_mm': 1, 'max_mm': 3, 'max_evaluations': 21}}
    return source, spec, config


def test_known_focus_recovers_identical_draws_and_retains_uncompensated(setup, tmp_path):
    source, spec, config = setup
    original = source.read_bytes()
    instances = []
    def factory(path):
        backend = FocusBackend(path)
        instances.append(backend)
        return backend
    result = run_tolerance_job(source, spec, tmp_path / 'run', factory, config)
    plain = run_tolerance_job(source, spec, tmp_path / 'plain', FocusBackend,
                              {k: v for k, v in config.items() if k != 'compensator'})
    for row, before in zip(result['monte_carlo'], plain['monte_carlo'], strict=True):
        assert row['perturbations'] == before['perturbations']
        assert row['measurements'] == before['measurements']
        assert row['compensated']['status'] == 'pass'
        best = row['compensated']['best']
        assert best['focus_mm'] == pytest.approx(2 + row['perturbations'][0]['delta_mm'], abs=.071)
        assert best['assessment']['passes'] and best['verified']
        assert row['compensated']['evaluations'] <= 21
    paired = result['paired_yield']
    assert paired['uncompensated']['passes'] == 1
    assert paired['compensated']['passes'] == 5
    assert paired['recovered'] == 4 and paired['lost'] == 0
    assert paired['compensated']['wilson_95'][0] == pytest.approx(.5655175352)
    assert 'conditional' in paired['compensated']['interval_scope']
    rows = [result['nominal'], *result['sensitivity'], *result['monte_carlo']]
    assert result['evaluations'] == len(rows) + sum(r['compensated']['evaluations'] for r in rows)
    assert source.read_bytes() == original and result['baseline_restored']
    assert instances[0].closed and instances[0].state == {'radius_mm': 10, 'thickness_mm': 2}


def test_bounds_and_budget_preserve_best_feasible(setup, tmp_path):
    source, spec, config = setup
    config['compensator'].update(min_mm=1.9, max_mm=2.1, max_evaluations=3)
    result = run_tolerance_job(source, spec, tmp_path / 'run', FocusBackend, config)
    assert result['sensitivity'][0]['compensated']['status'] == 'fail'
    assert result['sensitivity'][0]['compensated']['best'] is None
    for row in [result['nominal'], *result['sensitivity'], *result['monte_carlo']]:
        search = row['compensated']
        assert search['evaluations'] <= 3
        assert all(1.9 <= point['focus_mm'] <= 2.1 for point in search['history'])
    assert result['nominal']['compensated']['best']['focus_mm'] == 2


@pytest.mark.parametrize('mode', ['ignored', 'coupled', 'evaluate_mutates', 'setter_raises'])
def test_failed_focus_edits_never_accept_false_recovery(setup, tmp_path, mode):
    source, spec, config = setup
    class BrokenFocus(FocusBackend):
        def set_focus(self, value):
            if mode == 'ignored':
                return
            if mode == 'setter_raises':
                raise ValueError('focus motor unavailable')
            super().set_focus(value)
            if mode == 'coupled':
                self.state['radius_mm'] = 10
        def evaluate(self, spec):
            result = super().evaluate(spec)
            if mode == 'evaluate_mutates' and self.state['thickness_mm'] != 2:
                self.state['radius_mm'] = 10
            return result
    result = run_tolerance_job(source, spec, tmp_path / 'run', BrokenFocus, config)
    row = result['sensitivity'][0]
    assert row['status'] == 'fail'
    assert row['compensated']['status'] != 'pass'
    assert row['compensated']['best'] is None
    assert row['compensated']['analysis_failures'] > 0
    assert result['baseline_restored']


def test_compensation_reset_failure_stops_job(setup, tmp_path):
    source, spec, config = setup
    instances = []
    class FailedReset(FocusBackend):
        def load(self, path):
            if hasattr(self, 'state') and self.state['thickness_mm'] != 2:
                return
            super().load(path)
    def factory(path):
        backend = FailedReset(path)
        instances.append(backend)
        return backend
    with pytest.raises(RuntimeError, match='baseline.*compensation'):
        run_tolerance_job(source, spec, tmp_path / 'run', factory, config)
    failure = json.loads((tmp_path / 'run' / 'failure.json').read_text())
    assert failure['baseline_restored'] is False and instances[0].closed
    assert failure['yield']['not_run'] == 5


@pytest.mark.parametrize('change', [None, {}, {'surface': True}, {'surface': 0},
    {'parameter': 'radius_mm'}, {'min_mm': 0}, {'min_mm': True}, {'max_mm': float('inf')},
    {'min_mm': 3}, {'max_evaluations': 2}, {'max_evaluations': 202}, {'max_evaluations': True}, {'unknown': 1}])
def test_strict_compensator_configuration(setup, tmp_path, change):
    source, spec, config = setup
    config['compensator'] = ({**config['compensator'], **change} if change else change)
    def factory(_):
        pytest.fail('invalid configuration opened engine')
    with pytest.raises(ValueError):
        run_tolerance_job(source, spec, tmp_path / 'run', factory, config)


def test_compensator_requires_objective_and_disjoint_parameter(setup, tmp_path):
    source, spec, config = setup
    raw = copy.deepcopy(spec.data)
    raw.pop('objective')
    with pytest.raises(ValueError, match='objective'):
        run_tolerance_job(source, DesignSpec.from_dict(raw), tmp_path / 'a', FocusBackend, config)
    config['perturbations'][0]['parameter'] = 'thickness_mm'
    with pytest.raises(ValueError, match='perturb'):
        run_tolerance_job(source, spec, tmp_path / 'b', FocusBackend, config)


def test_compensator_must_be_final_gap(setup, tmp_path):
    source, spec, config = setup
    config['compensator']['surface'] = 2
    with pytest.raises(ValueError, match='final'):
        run_tolerance_job(source, spec, tmp_path / 'run', FocusBackend, config)


def test_uncompensated_analysis_mutation_is_not_used_as_compensation_reference(setup, tmp_path):
    source, spec, config = setup
    class MutatingAnalysis(FocusBackend):
        def evaluate(self, spec):
            result = super().evaluate(spec)
            self.state['radius_mm'] += .1
            return result
    result = run_tolerance_job(source, spec, tmp_path / 'run', MutatingAnalysis, config)
    assert result['nominal']['status'] == 'analysis_failed'
    assert result['nominal']['compensated']['evaluations'] == 0
    assert result['paired_yield']['compensated']['analysis_failures'] == 5


def test_timeout_keeps_active_paired_evidence_and_actual_calls(setup, tmp_path, monkeypatch):
    from _lib import tolerancing
    source, spec, config = setup
    clock, instances = [0], []
    monkeypatch.setattr(tolerancing.time, 'monotonic', lambda: clock[0])
    class SlowFocus(FocusBackend):
        def evaluate(self, spec):
            if self.state['thickness_mm'] != 2:
                clock[0] += 1000
            return super().evaluate(spec)
    def factory(path):
        backend = SlowFocus(path)
        instances.append(backend)
        return backend
    with pytest.raises(TimeoutError):
        run_tolerance_job(source, spec, tmp_path / 'run', factory, config)
    failure = json.loads((tmp_path / 'run' / 'failure.json').read_text())
    active = failure['active_trial']
    assert active['kind'] == 'nominal' and active['status'] == 'pass'
    assert active['compensated']['evaluations'] == 1 and failure['evaluations'] == 2
    assert active['compensated']['history'][0]['status'] == 'analysis_failed'
    assert active['compensated']['history'][0]['error_type'] == 'TimeoutError'
    assert failure['baseline_restored'] and instances[0].closed


def test_best_candidate_failure_on_repeat_is_not_accepted(setup, tmp_path):
    source, spec, config = setup
    class Unrepeatable(FocusBackend):
        def __init__(self, path):
            self.visited = set()
            super().__init__(path)
        def set_focus(self, value):
            if value in self.visited:
                raise RuntimeError('focus cannot reproduce')
            self.visited.add(value)
            super().set_focus(value)
    result = run_tolerance_job(source, spec, tmp_path / 'run', Unrepeatable, config)
    assert result['sensitivity'][0]['compensated']['status'] == 'analysis_failed'
    assert result['sensitivity'][0]['compensated']['best'] is None
    assert result['baseline_restored']


@pytest.mark.parametrize('corruption', ['image', 'interior', 'missing', 'valid'])
def test_axial_geometry_only_permits_image_shift_equal_to_focus_travel(setup, tmp_path, corruption):
    source, spec, config = setup
    class AxialBackend(FocusBackend):
        def inspect(self):
            result = super().inspect()
            axial = ['-inf', 0, self.state['thickness_mm']]
            if self.state['thickness_mm'] != 2:
                if corruption == 'image':
                    axial[-1] += .1
                elif corruption == 'interior':
                    axial[1] += .1
                elif corruption == 'missing':
                    return result
            result['axial_positions_mm'] = axial
            return result
    result = run_tolerance_job(source, spec, tmp_path / 'run', AxialBackend, config)
    row = result['sensitivity'][0]['compensated']
    assert row['status'] == ('pass' if corruption == 'valid' else 'fail')
    if corruption != 'valid':
        assert row['analysis_failures'] > 0 and row['best'] is None
