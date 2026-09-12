"""Runner acceptance tests; the coupled analytic engine has a known interior optimum."""
import copy
import json
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec
from test_design_contract import base_spec


class CoupledLens:
    model_suffix = '.json'

    def __init__(self, model):
        self.state = json.loads(Path(model).read_text())
        self.calls = 0
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def inspect(self):
        surfaces = [{'index': 0, 'is_image': False, 'radius_mm': None, 'thickness_mm': None},
                    {'index': 1, 'is_image': False, 'radius_mm': self.state['x'], 'thickness_mm': 5},
                    {'index': 2, 'is_image': False, 'radius_mm': -30, 'thickness_mm': self.state['y']},
                    {'index': 3, 'is_image': True, 'radius_mm': None, 'thickness_mm': None}]
        fixed = copy.deepcopy(surfaces)
        del fixed[2]['thickness_mm']
        return {'engine': {'name': 'analytic-coupled'}, 'image_surface': 3,
                'focus_mm': self.state['y'], 'surfaces': surfaces,
                'invariants': {'surfaces': fixed, 'aperture_mm': self.state['aperture']}}

    def get_parameter(self, surface, name):
        return self.state[{(1, 'radius_mm'): 'x', (2, 'thickness_mm'): 'y'}[surface, name]]

    def set_parameter(self, surface, name, value):
        self.state[{(1, 'radius_mm'): 'x', (2, 'thickness_mm'): 'y'}[surface, name]] = value

    def evaluate(self, spec):
        self.calls += 1
        x, y = self.state['x'], self.state['y']
        # Rotated positive-definite quadratic, nonzero xy term; both variables matter.
        dx, dy = (x - 70) / 100, (y - 1.35)
        value = .95 - (dx + .6 * dy) ** 2 - .3 * (dx - dy) ** 2
        return [{'metric': 'mtf', 'field': 1, 'wavelength': 1, 'frequency': 50,
                     'axis': 'tangential', 'unit': '1', 'value': value},
                {'metric': 'total_track_mm', 'unit': 'mm', 'value': y}]

    def save(self, path):
        Path(path).write_text(json.dumps(self.state))

    def load(self, path):
        self.state = json.loads(Path(path).read_text())


def config():
    return {'schema': '1', 'variables': [
        {'surface': 1, 'parameter': 'radius_mm', 'min_mm': 10, 'max_mm': 110},
        {'surface': 2, 'parameter': 'thickness_mm', 'min_mm': 1, 'max_mm': 2}]}


def setup(tmp_path, engine=CoupledLens, budget=101):
    model = tmp_path / 'source.json'
    model.write_text(json.dumps({'x': 20, 'y': 1.8, 'aperture': 10}))
    raw = base_spec()
    raw.pop('focus')
    raw['budget']['max_evaluations'] = budget
    raw['requirements'][0]['min'] = 0
    backend = engine(model)
    return model, raw, backend


def run(model, raw, out, backend, variables=None, **kwargs):
    from _lib.optimization import run_optimization_job
    return run_optimization_job(model, DesignSpec.from_dict(raw), out, lambda _: backend,
                                config() if variables is None else variables, **kwargs)


def test_genuinely_coupled_optimum_normalized_bounds_source_and_reload(tmp_path):
    model, raw, backend = setup(tmp_path)
    original = model.read_bytes()
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'improved'
    candidate = result['candidate']
    assert candidate['parameters_mm'] == pytest.approx([70, 1.35], abs=.1)
    assert candidate['measurements'][0]['value'] > .9499
    assert result['saved_candidate_verified'] and result['baseline_restored']
    assert result['source_unchanged'] and model.read_bytes() == original
    assert backend.closed and backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}
    assert json.loads(Path(result['artifacts']['candidate_model']).read_text())['x'] > 65
    assert result['evaluations'] == backend.calls <= 101
    assert all(10 <= h['parameters_mm'][0] <= 110 and 1 <= h['parameters_mm'][1] <= 2
               for h in result['history'])


def test_retains_best_feasible_even_when_unconstrained_optimum_fails(tmp_path):
    model, raw, backend = setup(tmp_path, budget=201)
    raw['requirements'].append({'id': 'travel', 'metric': 'total_track_mm', 'unit': 'mm', 'min': 1.6})
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'improved'
    assert result['candidate']['parameters_mm'][1] >= 1.6
    assert result['candidate']['assessment']['passes']
    assert any(not h['assessment']['passes'] for h in result['history'])


@pytest.mark.parametrize('mutation', ['ignored', 'coupled', 'fixed', 'evaluation_fixed'])
def test_unapplied_or_coupled_edits_and_fixed_changes_fail_closed(tmp_path, mutation):
    class Broken(CoupledLens):
        def set_parameter(self, surface, name, value):
            if mutation != 'ignored':
                super().set_parameter(surface, name, value)
            if mutation == 'coupled' and name == 'thickness_mm':
                self.state['x'] += 1
            if mutation == 'fixed':
                self.state['aperture'] += 1

        def evaluate(self, spec):
            rows = super().evaluate(spec)
            if mutation == 'evaluation_fixed' and self.calls > 1:
                self.state['aperture'] += 1
            return rows

    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises(RuntimeError, match='readback|fixed'):
        run(model, raw, tmp_path / 'out', backend)
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['baseline_restored'] and failure['source_unchanged']
    assert backend.closed
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('failure_kind', ['analysis', 'reload_vector', 'reload_objective', 'close', 'save'])
def test_failures_restore_without_success_receipt(tmp_path, failure_kind):
    class Broken(CoupledLens):
        reloaded = False

        def evaluate(self, spec):
            if failure_kind == 'analysis' and self.calls == 2:
                raise RuntimeError('analysis failed')
            rows = super().evaluate(spec)
            if failure_kind == 'reload_objective' and self.reloaded:
                rows[0]['value'] -= .1
            return rows

        def load(self, path):
            super().load(path)
            self.reloaded = Path(path).name.startswith('candidate')
            if failure_kind == 'reload_vector' and self.reloaded:
                self.state['x'] += .1

        def save(self, path):
            if failure_kind == 'save':
                raise RuntimeError('save failed')
            super().save(path)

        def __exit__(self, *args):
            super().__exit__(*args)
            if failure_kind == 'close':
                raise RuntimeError('close failed')

    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises(RuntimeError):
        run(model, raw, tmp_path / 'out', backend)
    assert backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}
    assert backend.closed
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('mode', ['deadline', 'cancel'])
def test_late_calls_and_cancellation_cannot_be_accepted(tmp_path, monkeypatch, mode):
    import _lib.optimization as optimizer
    clock = [0]
    monkeypatch.setattr(optimizer.time, 'monotonic', lambda: clock[0])

    class Slow(CoupledLens):
        def evaluate(self, spec):
            clock[0] += 2
            return super().evaluate(spec)

    model, raw, backend = setup(tmp_path, Slow)
    raw['budget']['timeout_s'] = 1 if mode == 'deadline' else 60
    with pytest.raises((TimeoutError, InterruptedError)):
        run(model, raw, tmp_path / 'out', backend, cancelled=lambda: mode == 'cancel')
    assert backend.closed and backend.state['x'] == 20
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']


def test_small_budget_and_minimum_gain_yield_no_candidate(tmp_path):
    model, raw, backend = setup(tmp_path, budget=7)
    raw['minimum_gain'] = 10
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'no_acceptable_improvement'
    assert result['evaluations'] <= 7
    assert result['candidate'] is None and not result['saved_candidate_verified']


@pytest.mark.parametrize('bad', [
    {}, {'schema': '1', 'variables': []},
    {'schema': '1', 'variables': [{'surface': 1, 'parameter': 'radius_mm', 'min_mm': -1, 'max_mm': 1}]},
    {'schema': '1', 'variables': [{'surface': True, 'parameter': 'radius_mm', 'min_mm': 1, 'max_mm': 2}]},
    {'schema': '1', 'variables': [{'surface': 0, 'parameter': 'radius_mm', 'min_mm': 1, 'max_mm': 2}]},
    {'schema': '1', 'variables': [{'surface': 1, 'parameter': 'thickness_mm', 'min_mm': 0, 'max_mm': 2}]},
    {'schema': '1', 'variables': [{'surface': 1, 'parameter': 'conic', 'min_mm': 1, 'max_mm': 2}]},
    {'schema': '1', 'variables': [{'surface': 1, 'parameter': 'radius_mm', 'min_mm': 1, 'max_mm': float('inf')}]},
    {'schema': '1', 'variables': [{'surface': 1, 'parameter': 'radius_mm', 'min_mm': 2, 'max_mm': 2}]},
])
def test_invalid_config_rejected_before_engine_or_artifacts(tmp_path, bad):
    model, raw, backend = setup(tmp_path)
    with pytest.raises(ValueError):
        run(model, raw, tmp_path / 'out', backend, variables=bad)
    assert backend.calls == 0 and not (tmp_path / 'out').exists()


def test_image_variable_rejected_and_restored(tmp_path):
    model, raw, backend = setup(tmp_path)
    variables = config()
    variables['variables'][0]['surface'] = 3
    with pytest.raises(ValueError, match='surface'):
        run(model, raw, tmp_path / 'out', backend, variables=variables)
    assert backend.closed and backend.calls == 0


def test_cli_optimization_dispatches_explicit_variables(tmp_path, monkeypatch, run):
    import _lib.optiland_backend as portable
    import design
    model, raw, backend = setup(tmp_path)
    spec_path, variables_path = tmp_path / 'spec.json', tmp_path / 'variables.json'
    spec_path.write_text(json.dumps(raw))
    variables_path.write_text(json.dumps(config()))
    monkeypatch.setattr(portable, 'OptilandBackend', lambda _: backend)
    argv = ['optimize', '--model', str(model), '--spec', str(spec_path), '--out', str(tmp_path / 'out'),
            '--backend', 'optiland', '--variables', str(variables_path), '--json']
    code, stdout, stderr = run(design.main, argv)
    assert code == 0, stderr
    assert json.loads(stdout)['action'] == 'optimize'
    assert json.loads(stdout)['saved_candidate_verified']


def test_undeclared_focus_change_is_fixed_even_when_legacy_invariant_omits_it(tmp_path):
    class HiddenFocus(CoupledLens):
        def set_parameter(self, surface, name, value):
            super().set_parameter(surface, name, value)
            self.state['y'] += .1

    model, raw, backend = setup(tmp_path, HiddenFocus)
    variables = config()
    variables['variables'] = variables['variables'][:1]
    with pytest.raises(RuntimeError, match='fixed'):
        run(model, raw, tmp_path / 'out', backend, variables=variables)


def test_tiny_ignored_nonzero_edit_rejected_despite_readback_tolerance(tmp_path):
    class Ignored(CoupledLens):
        def set_parameter(self, surface, name, value):
            pass

    model, raw, backend = setup(tmp_path, Ignored)
    variables = {'schema': '1', 'variables': [
        {'surface': 1, 'parameter': 'radius_mm', 'min_mm': 20, 'max_mm': 20 + 1e-11}]}
    with pytest.raises(RuntimeError, match='readback'):
        run(model, raw, tmp_path / 'out', backend, variables=variables)


def test_complete_axial_readback_accepts_only_sum_of_declared_thickness_changes():
    from _lib.optimization import _fixed_inspection
    initial = {'image_surface': 3, 'focus_mm': 4, 'surfaces': [
        {'index': 1, 'thickness_mm': 5}, {'index': 2, 'thickness_mm': 4}],
        'invariants': {}, 'axial_positions_mm': ['-inf', 0, 5, 9]}
    variables = [{'surface': 1, 'parameter': 'thickness_mm'}]
    edited = copy.deepcopy(initial)
    edited['surfaces'][0]['thickness_mm'] = 6
    edited['axial_positions_mm'] = ['-inf', 0, 6, 10]
    assert _fixed_inspection(edited, initial, variables) == _fixed_inspection(initial, initial, variables)
    edited['axial_positions_mm'][-1] = 10.1
    with pytest.raises(RuntimeError, match='axial'):
        _fixed_inspection(edited, initial, variables)


@pytest.mark.tier1
def test_portable_two_variable_job_verifies_geometry_source_and_saved_optics(tmp_path):
    pytest.importorskip('optiland')
    from _lib.optiland_backend import OptilandBackend
    from _lib.optimization import run_optimization_job
    model = Path(__file__).resolve().parents[2] / 'skills/optical-design/assets/portable-singlet.json'
    raw = json.loads((model.parent / 'refocus-spec.json').read_text())
    raw['budget']['max_evaluations'] = 81
    raw['budget']['timeout_s'] = 120
    variables = {'schema': '1', 'variables': [
        {'surface': 1, 'parameter': 'radius_mm', 'min_mm': 48, 'max_mm': 52},
        {'surface': 2, 'parameter': 'thickness_mm', 'min_mm': 44, 'max_mm': 51}]}
    result = run_optimization_job(model, DesignSpec.from_dict(raw), tmp_path / 'out',
                                  OptilandBackend, variables)
    assert result['status'] == 'improved'
    assert result['saved_candidate_verified'] and result['baseline_restored'] and result['source_unchanged']
    before, after = result['baseline']['parameters_mm'], result['candidate']['parameters_mm']
    assert before[0] != after[0] and before[1] != after[1]


def test_minimize_direction_and_bounded_boundary_optimum(tmp_path):
    class Cost(CoupledLens):
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            rows[0]['value'] = 1 - rows[0]['value']
            return rows

    model, raw, backend = setup(tmp_path, Cost)
    raw['objective']['direction'] = 'minimize'
    variables = config()
    variables['variables'][0]['max_mm'] = 50
    result = run(model, raw, tmp_path / 'out', backend, variables=variables)
    assert result['status'] == 'improved'
    assert result['candidate']['parameters_mm'][0] == 50
    assert result['candidate']['objective_value'] < result['baseline']['objective_value']


def test_missing_hard_requirement_never_accepts_optimum(tmp_path):
    model, raw, backend = setup(tmp_path)
    raw['requirements'].append({'id': 'missing', 'metric': 'efl_mm', 'unit': 'mm', 'min': 10})
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'no_acceptable_improvement'
    assert result['candidate'] is None


def test_changed_source_fails_without_overwriting_external_change(tmp_path):
    model, raw, backend = setup(tmp_path)
    original_evaluate = backend.evaluate

    def mutate_source(spec):
        model.write_text('external change')
        return original_evaluate(spec)

    backend.evaluate = mutate_source
    with pytest.raises(RuntimeError, match='source changed'):
        run(model, raw, tmp_path / 'out', backend)
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['baseline_restored'] and not failure['source_unchanged']
    assert model.read_text() == 'external change'
    assert json.loads((tmp_path / 'out/source_snapshot.json').read_text())['x'] == 20


def test_restore_failure_retains_original_analysis_error_and_no_success(tmp_path):
    class CannotRestore(CoupledLens):
        failed = False

        def evaluate(self, spec):
            if self.calls == 2:
                self.failed = True
                raise RuntimeError('original analysis error')
            return super().evaluate(spec)

        def load(self, path):
            if self.failed:
                raise RuntimeError('restoration error')
            super().load(path)

    model, raw, backend = setup(tmp_path, CannotRestore)
    with pytest.raises(RuntimeError, match='original analysis error'):
        run(model, raw, tmp_path / 'out', backend)
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert not failure['baseline_restored'] and 'restoration error' in failure['cleanup_error']


def test_no_objective_duplicate_and_too_many_variables_rejected(tmp_path):
    model, raw, backend = setup(tmp_path)
    duplicate = config()
    duplicate['variables'].append(copy.deepcopy(duplicate['variables'][0]))
    too_many = config()
    too_many['variables'] *= 3
    for variables in (duplicate, too_many):
        with pytest.raises(ValueError):
            run(model, raw, tmp_path / 'out', backend, variables=variables)
    raw.pop('objective')
    with pytest.raises(ValueError, match='objective'):
        run(model, raw, tmp_path / 'out', backend)
    assert not (tmp_path / 'out').exists()


@pytest.mark.parametrize('action,variables', [('optimize', False), ('audit', True), ('refocus', True)])
def test_cli_requires_variables_only_for_optimization(run, action, variables):
    import design
    argv = [action, '--model', 'missing', '--spec', 'missing', '--out', 'out', '--backend', 'optiland']
    if variables:
        argv += ['--variables', 'missing']
    code, _, error = run(design.main, argv)
    assert code == 2 and '--variables' in error
