"""Explicit saved-model edits exercise real receipt, readback and recovery paths."""
import copy
import json
from pathlib import Path

import pytest
from _lib import model_actions as actions
from _lib.design_contract import DesignSpec
from test_optiland_backend import singlet  # noqa: F401 -- shared pytest fixture
from test_optimization import CoupledLens, setup


def changes():
    return {'schema': '1', 'changes': [
        {'surface': 1, 'parameter': 'radius_mm', 'expected_mm': 20, 'value_mm': 70},
        {'surface': 2, 'parameter': 'thickness_mm', 'expected_mm': 1.8, 'value_mm': 1.35}]}


def test_inspect_requires_no_spec_or_analysis_and_verifies_persisted_baseline(tmp_path):
    model, _raw, backend = setup(tmp_path)
    result = actions.run_inspect_job(model, tmp_path / 'out', lambda _: backend)
    assert result['status'] == 'inspected' and result['action'] == 'inspect'
    assert result['baseline']['inspection']['surfaces'][1]['radius_mm'] == 20
    assert result['baseline']['measurements'] == [] and 'assessment' not in result['baseline']
    assert 'spec' not in result and result['candidate'] is None
    assert backend.calls == 0 and backend.closed
    assert result['source_unchanged'] and result['baseline_restored']
    assert Path(result['artifacts']['source_snapshot']).read_bytes() == model.read_bytes()
    assert Path(result['artifacts']['baseline_model']).exists()
    assert json.loads((tmp_path / 'out/report.json').read_text()) == result


def test_explicit_edit_applies_all_cells_and_reloads_without_requiring_merit_gain(tmp_path):
    model, raw, backend = setup(tmp_path)
    raw['minimum_gain'] = 100
    original = model.read_bytes()
    result = actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    assert result['action'] == 'edit' and result['status'] == 'applied'
    assert result['candidate']['parameters_mm'] == [70, 1.35]
    assert result['candidate']['assessment']['passes'] and result['saved_candidate_verified']
    assert result['candidate']['objective_breakdown']['value'] == pytest.approx(.95)
    assert result['evaluations'] == 3 and result['baseline_restored'] and backend.closed
    assert model.read_bytes() == original
    assert backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}
    assert json.loads(Path(result['artifacts']['candidate_model']).read_text())['x'] == 70
    assert result['changes'] == changes() and result['changes_sha256']


def test_hard_failure_retains_rejected_saved_artifact_and_no_accepted_candidate(tmp_path):
    model, raw, backend = setup(tmp_path)
    raw['requirements'][0]['min'] = 1
    result = actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    assert result['status'] == 'requirements_not_met' and result['candidate'] is None
    assert not result['saved_candidate_verified']
    assert not result['rejected_candidate']['assessment']['passes']
    assert 'candidate_model' not in result['artifacts']
    assert Path(result['artifacts']['rejected_candidate_model']).exists()
    assert result['baseline_restored']


def test_edit_without_objective_and_noop_are_supported(tmp_path):
    model, raw, backend = setup(tmp_path)
    raw.pop('objective')
    config = changes()
    config['changes'][0]['value_mm'] = 20
    result = actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, config)
    assert result['status'] == 'applied'
    assert 'objective_breakdown' not in result['candidate']


def test_backend_reusing_measurement_buffer_cannot_rewrite_baseline_evidence(tmp_path):
    class Reused(CoupledLens):
        def __init__(self, model):
            super().__init__(model)
            self.shared = []
        def evaluate(self, spec):
            self.shared[:] = super().evaluate(spec)
            return self.shared
    model, raw, backend = setup(tmp_path, Reused)
    result = actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    assert result['baseline']['measurements'][1]['value'] == 1.8
    assert result['candidate']['measurements'][1]['value'] == 1.35


@pytest.mark.parametrize('change', [
    lambda c: c.update(schema=1), lambda c: c.update(extra=True),
    lambda c: c.update(changes=[]), lambda c: c.update(changes=c['changes'] * 9),
    lambda c: c['changes'].append(copy.deepcopy(c['changes'][0])),
    lambda c: c['changes'][0].update(surface=True), lambda c: c['changes'][0].update(surface=0),
    lambda c: c['changes'][0].update(parameter='conic'), lambda c: c['changes'][0].pop('expected_mm'),
    lambda c: c['changes'][0].update(value_mm=0), lambda c: c['changes'][0].update(expected_mm=0),
    lambda c: c['changes'][1].update(value_mm=-1), lambda c: c['changes'][1].update(expected_mm=-1),
    lambda c: c['changes'][0].update(expected_mm=True), lambda c: c['changes'][0].update(value_mm=float('inf')),
])
def test_invalid_changes_rejected_before_engine_open(tmp_path, change):
    model, raw, _backend = setup(tmp_path)
    config = changes()
    change(config)
    with pytest.raises(ValueError):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out',
                             lambda _: pytest.fail('invalid changes opened engine'), config)


def test_stale_second_expected_value_prevents_every_mutation(tmp_path):
    class Recorded(CoupledLens):
        setters = 0
        def set_parameter(self, *args):
            self.setters += 1
            super().set_parameter(*args)
    model, raw, backend = setup(tmp_path, Recorded)
    config = changes()
    config['changes'][1]['expected_mm'] = 1.9
    with pytest.raises(ValueError, match='expected|stale'):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, config)
    assert backend.setters == 0 and backend.calls == 0
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']


@pytest.mark.parametrize('kind', ['ignored', 'coupled', 'fixed', 'evaluation_fixed', 'inspection_readback'])
def test_edit_detects_ignored_coupled_or_undeclared_changes(tmp_path, kind):
    class Broken(CoupledLens):
        def set_parameter(self, surface, name, value):
            if kind != 'ignored':
                super().set_parameter(surface, name, value)
            if kind == 'coupled' and surface == 1:
                self.state['y'] = 1.35  # Would be hidden if only checking after both setters.
            if kind == 'fixed':
                self.state['aperture'] += 1
        def evaluate(self, spec):
            result = super().evaluate(spec)
            if kind == 'evaluation_fixed':
                self.state['aperture'] += 1
            return result
        def inspect(self):
            result = super().inspect()
            if kind == 'inspection_readback' and self.state['x'] != 20:
                result['surfaces'][1]['radius_mm'] = 20
            return result
    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises(RuntimeError, match='readback|fixed'):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    assert backend.closed and backend.state == {'x': 20, 'y': 1.8, 'aperture': 10}
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('kind', ['reload_parameter', 'reload_metric', 'close', 'save', 'restore'])
def test_failed_reload_save_teardown_or_restoration_never_writes_success(tmp_path, kind):
    class Broken(CoupledLens):
        reloaded = False
        def load(self, path):
            if kind == 'restore' and self.state['x'] != 20 and 'baseline' in Path(path).name:
                raise RuntimeError('restore failure')
            super().load(path)
            self.reloaded = 'candidate' in Path(path).name
            if kind == 'reload_parameter' and self.reloaded:
                self.state['x'] += 1
        def evaluate(self, spec):
            result = super().evaluate(spec)
            if kind == 'reload_metric' and self.reloaded:
                result[0]['value'] -= .01
            return result
        def save(self, path):
            if kind == 'save':
                raise RuntimeError('save failure')
            super().save(path)
        def __exit__(self, *args):
            super().__exit__(*args)
            if kind == 'close':
                raise RuntimeError('teardown failure')
    model, raw, backend = setup(tmp_path, Broken)
    with pytest.raises(RuntimeError):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert failure['status'] == 'failed' and backend.closed
    assert failure['baseline_restored'] == (kind != 'restore')
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('kind', ['cancel', 'deadline', 'spec_mutation'])
def test_late_analysis_cancellation_or_spec_mutation_aborts_and_restores(tmp_path, monkeypatch, kind):
    clock = [0]
    monkeypatch.setattr(actions.time, 'monotonic', lambda: clock[0])
    class Interrupted(CoupledLens):
        def evaluate(self, spec):
            result = super().evaluate(spec)
            clock[0] = 1000
            if kind == 'spec_mutation':
                spec.data['requirements'][0]['min'] = -100
            return result
    model, raw, backend = setup(tmp_path, Interrupted)
    raw['budget']['timeout_s'] = 2000 if kind != 'deadline' else 60
    with pytest.raises((RuntimeError, TimeoutError, InterruptedError)):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend,
                             changes(), cancelled=lambda: kind == 'cancel' and clock[0] > 0)
    assert backend.closed and backend.state['x'] == 20
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']


def test_inspect_teardown_failure_retains_only_failure_receipt(tmp_path):
    class Broken(CoupledLens):
        def __exit__(self, *args):
            super().__exit__(*args)
            raise RuntimeError('teardown')
    model, _raw, backend = setup(tmp_path, Broken)
    with pytest.raises(RuntimeError, match='teardown'):
        actions.run_inspect_job(model, tmp_path / 'out', lambda _: backend)
    assert (tmp_path / 'out/failure.json').exists() and not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('surface', [3, 4])
def test_image_or_missing_surface_rejected_before_analysis(tmp_path, surface):
    model, raw, backend = setup(tmp_path)
    config = changes()
    config['changes'][0]['surface'] = surface
    with pytest.raises(ValueError, match='physical'):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, config)
    assert backend.calls == 0 and backend.closed


def test_inspect_cancellation_prevents_engine_open_and_retains_failure(tmp_path):
    model, _raw, _backend = setup(tmp_path)
    with pytest.raises(InterruptedError):
        actions.run_inspect_job(model, tmp_path / 'out', lambda _: pytest.fail('cancelled job opened engine'),
                                 cancelled=lambda: True)
    assert json.loads((tmp_path / 'out/failure.json').read_text())['source_unchanged']


def test_existing_output_is_never_overwritten(tmp_path):
    model, _raw, _backend = setup(tmp_path)
    out = tmp_path / 'out'
    out.mkdir()
    (out / 'report.json').write_text('keep evidence')
    with pytest.raises(ValueError, match='empty'):
        actions.run_inspect_job(model, out, lambda _: pytest.fail('occupied output opened engine'))
    assert (out / 'report.json').read_text() == 'keep evidence'


def test_source_change_during_owned_job_blocks_receipt_without_overwriting_source(tmp_path):
    model, raw, backend = setup(tmp_path)
    class SourceChanged(CoupledLens):
        def evaluate(self, spec):
            result = super().evaluate(spec)
            model.write_text('externally changed')
            return result
    backend = SourceChanged(model)
    with pytest.raises(RuntimeError, match='source changed'):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    failure = json.loads((tmp_path / 'out/failure.json').read_text())
    assert not failure['source_unchanged'] and failure['baseline_restored']
    assert model.read_text() == 'externally changed' and not (tmp_path / 'out/report.json').exists()


@pytest.mark.parametrize('name', ['spec.json', 'changes.json', 'source_snapshot.json',
                                  'baseline-model.json', 'candidate-model.json'])
def test_artifact_mutation_during_teardown_cannot_be_blessed_with_new_hash(tmp_path, name):
    class Tampered(CoupledLens):
        def __exit__(self, *args):
            super().__exit__(*args)
            (tmp_path / 'out' / name).write_text('{"tampered":true}')
    model, raw, backend = setup(tmp_path, Tampered)
    with pytest.raises(RuntimeError, match='artifact|snapshot|evidence'):
        actions.run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'out', lambda _: backend, changes())
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']
    assert not (tmp_path / 'out/report.json').exists()


@pytest.mark.tier1
def test_portable_inspection_and_explicit_geometry_edits_are_source_preserving(singlet, tmp_path):  # noqa: F811
    from _lib.optiland_backend import OptilandBackend
    original = singlet.read_bytes()
    inspected = actions.run_inspect_job(singlet, tmp_path / 'inspect', OptilandBackend)
    initial = inspected['baseline']['inspection']
    raw = {'schema': '1', 'fields': [1], 'wavelengths': [1],
           'requirements': [{'id': 'efl', 'metric': 'efl_mm', 'unit': 'mm', 'min': 40, 'max': 60}]}
    config = {'schema': '1', 'changes': [
        {'surface': 1, 'parameter': 'radius_mm', 'expected_mm': 50, 'value_mm': 52},
        {'surface': 1, 'parameter': 'thickness_mm', 'expected_mm': 5, 'value_mm': 6}]}
    result = actions.run_edit_job(singlet, DesignSpec.from_dict(raw), tmp_path / 'edit', OptilandBackend, config)
    assert result['status'] == 'applied' and result['saved_candidate_verified']
    changed = result['candidate']['inspection']
    assert changed['surfaces'][1]['radius_mm'] == 52 and changed['surfaces'][1]['thickness_mm'] == 6
    assert changed['axial_positions_mm'][2:] == pytest.approx([v + 1 for v in initial['axial_positions_mm'][2:]])
    assert result['baseline_restored'] and singlet.read_bytes() == original
