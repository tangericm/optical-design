"""Independent arithmetic and runner evidence for dimensionless composite merit."""
import copy
import json
import math

import pytest
from _lib import design_contract as contract
from test_design_contract import base_spec
from test_optiland_backend import singlet  # noqa: F401 -- shared pytest fixture
from test_optimization import CoupledLens, run, setup


def raw_spec():
    raw = base_spec()
    raw['objective'] = {'direction': 'minimize', 'aggregation': 'weighted_rms', 'terms': [
        {'metric': 'efl_mm', 'unit': 'mm', 'target': 50, 'scale': 2, 'weight': 1},
        {'metric': 'rms_spot_um', 'field': 1, 'wavelength': 1, 'unit': 'um',
         'target': 0, 'scale': 10, 'weight': 3}]}
    return raw


def rows():
    return [{'metric': 'efl_mm', 'unit': 'mm', 'value': 54},
            {'metric': 'rms_spot_um', 'field': 1, 'wavelength': 1, 'unit': 'um', 'value': 10}]


def test_mixed_units_normalize_before_weighted_rms_and_retain_term_evidence():
    spec = contract.DesignSpec.from_dict(raw_spec())
    result = contract.objective_breakdown(spec, rows())
    assert result['value'] == pytest.approx(math.sqrt(7 / 4))
    assert result['unit'] == '1'
    assert [t['normalized_residual'] for t in result['terms']] == [2, 1]
    assert [t['value'] for t in result['terms']] == [54, 10]
    assert [t['unit'] for t in result['terms']] == ['mm', 'um']
    assert contract.objective_value(spec, rows()) == result['value']
    assert len(spec.objective_metrics) == 2


@pytest.mark.parametrize('change', [
    lambda o: o.update(direction='maximize'), lambda o: o.update(aggregation='sum'),
    lambda o: o.update(terms=[]), lambda o: o.update(terms={}),
    lambda o: o.update(extra=True), lambda o: o['terms'][0].update(unit='um'),
    lambda o: o['terms'][0].update(scale=0), lambda o: o['terms'][0].update(weight=-1),
    lambda o: o['terms'][0].update(weight=True), lambda o: o['terms'][0].update(target=math.inf),
    lambda o: o['terms'][0].pop('target'), lambda o: o['terms'][1].update(field=2),
    lambda o: o['terms'][0].update(scale=math.nan),
])
def test_invalid_composite_contract_rejected(change):
    raw = raw_spec()
    change(raw['objective'])
    with pytest.raises(ValueError):
        contract.DesignSpec.from_dict(raw)


@pytest.mark.parametrize('change', [
    lambda r: r.pop(), lambda r: r.append(copy.deepcopy(r[0])),
    lambda r: r[0].update(unit='um'), lambda r: r[0].update(value=math.nan),
    lambda r: r[0].update(value=math.inf), lambda r: r[0].update(value=None),
    lambda r: r[0].update(value=True),
])
def test_missing_duplicate_wrong_unit_and_nonfinite_measurements_rejected(change):
    spec, values = contract.DesignSpec.from_dict(raw_spec()), rows()
    change(values)
    with pytest.raises(ValueError):
        contract.objective_value(spec, values)


def test_overflow_in_normalized_residual_fails():
    raw = raw_spec()
    raw['objective']['terms'][0].update(target=-1e308)
    values = rows()
    values[0]['value'] = 1e308
    with pytest.raises(ValueError, match='finite'):
        contract.objective_value(contract.DesignSpec.from_dict(raw), values)


def test_extreme_positive_weights_and_large_finite_residuals_are_not_dropped():
    raw = raw_spec()
    raw['objective']['terms'][0].update(target=0, scale=1, weight=5e-324)
    raw['objective']['terms'][1].update(target=0, scale=1, weight=1e308)
    values = rows()
    values[0]['value'], values[1]['value'] = 1e308, 0
    merit = contract.objective_value(contract.DesignSpec.from_dict(raw), values)
    assert merit == pytest.approx(2.2227587494850775e-8, rel=1e-8, abs=0)
    raw['objective']['terms'][0]['weight'] = 1e308
    values[1]['value'] = 1e308
    assert contract.objective_value(contract.DesignSpec.from_dict(raw), values) == pytest.approx(1e308)


def test_legacy_objective_keeps_units_direction_and_signed_value():
    raw = base_spec()
    raw['objective'] = {'metric': 'efl_mm', 'direction': 'maximize'}
    spec = contract.DesignSpec.from_dict(raw)
    result = contract.objective_breakdown(spec, [{'metric': 'efl_mm', 'unit': 'mm', 'value': -12}])
    assert result['value'] == -12
    assert result['unit'] == 'mm' and result['direction'] == 'maximize'
    assert len(spec.objective_metrics) == 1
    raw.pop('objective')
    assert contract.DesignSpec.from_dict(raw).objective_metrics == []


class MultiConditionLens(CoupledLens):
    def evaluate(self, spec):
        self.calls += 1
        return [{'metric': 'efl_mm', 'unit': 'mm', 'value': self.state['x']},
                {'metric': 'total_track_mm', 'unit': 'mm', 'value': self.state['y']}]


def optimization_spec(raw):
    raw['requirements'] = [{'id': 'track', 'metric': 'total_track_mm', 'unit': 'mm', 'min': 1}]
    raw['objective'] = {'direction': 'minimize', 'aggregation': 'weighted_rms', 'terms': [
        {'metric': 'efl_mm', 'unit': 'mm', 'target': 70, 'scale': 100, 'weight': 1},
        {'metric': 'total_track_mm', 'unit': 'mm', 'target': 1.35, 'scale': 1, 'weight': 3}]}
    return raw


def test_multi_condition_optimum_and_saved_reload_include_merit_evidence(tmp_path):
    model, raw, backend = setup(tmp_path, MultiConditionLens, budget=201)
    result = run(model, optimization_spec(raw), tmp_path / 'out', backend)
    assert result['status'] == 'improved'
    assert result['candidate']['parameters_mm'] == pytest.approx([70, 1.35], abs=.02)
    assert result['saved_candidate_verified'] and result['baseline_restored']
    assert result['source_unchanged'] and backend.closed
    for entry in [result['baseline'], result['candidate'], *result['history']]:
        assert entry['objective_breakdown']['unit'] == '1'
        assert len(entry['objective_breakdown']['terms']) == 2
        assert entry['objective_value'] == entry['objective_breakdown']['value']


def test_composite_cannot_accept_failed_hard_requirement(tmp_path):
    model, raw, backend = setup(tmp_path, MultiConditionLens)
    optimization_spec(raw)['requirements'][0]['min'] = 3
    result = run(model, raw, tmp_path / 'out', backend)
    assert result['status'] == 'no_acceptable_improvement'
    assert result['candidate'] is None


def test_composite_failure_restores_and_writes_failure_receipt(tmp_path):
    class Missing(MultiConditionLens):
        def evaluate(self, spec):
            return super().evaluate(spec)[1:]
    model, raw, backend = setup(tmp_path, Missing)
    with pytest.raises(ValueError):
        run(model, optimization_spec(raw), tmp_path / 'out', backend)
    assert json.loads((tmp_path / 'out/failure.json').read_text())['baseline_restored']
    assert backend.closed and not (tmp_path / 'out/report.json').exists()


def test_refocus_finds_weighted_compromise_and_retains_each_evaluation(tmp_path):
    from _lib.design_jobs import run_job
    from test_design_jobs import AnalyticFocus

    class TwoTargetFocus(AnalyticFocus):
        def evaluate(self, spec):
            self.calls += 1
            return [{'metric': 'efl_mm', 'unit': 'mm', 'value': self.focus},
                    {'metric': 'total_track_mm', 'unit': 'mm', 'value': self.focus}]

    model = tmp_path / 'source.lens'
    model.write_text('60')
    raw = optimization_spec(base_spec())
    raw['objective']['terms'][0].update(target=50, scale=1, weight=3)
    raw['objective']['terms'][1].update(target=46, scale=1, weight=1)
    raw['budget']['max_evaluations'] = 61
    result = run_job(model, contract.DesignSpec.from_dict(raw), tmp_path / 'out', TwoTargetFocus,
                     action='refocus')
    # d/dx [3(x-50)^2 + (x-46)^2] = 8x-392, so x = 49.
    assert result['candidate']['inspection']['focus_mm'] == pytest.approx(49, abs=.001)
    assert result['candidate']['objective_value'] == pytest.approx(math.sqrt(3), abs=1e-6)
    assert result['saved_candidate_verified'] and result['baseline_restored']
    assert all(len(h['objective_breakdown']['terms']) == 2 for h in result['history'])
    assert model.read_text() == '60'


def test_compensation_retains_composite_terms_and_verifies_best(tmp_path):
    from _lib.tolerancing import run_tolerance_job
    from test_compensation import FocusBackend

    source = tmp_path / 'source.json'
    source.write_text('{"radius_mm":10,"thickness_mm":2}')
    raw = raw_spec()
    raw['requirements'] = [{'id': 'spot', 'metric': 'rms_spot_um', 'unit': 'um',
                           'field': 1, 'wavelength': 1, 'max': .005}]
    raw['objective']['terms'] = [raw['objective']['terms'][1]]
    raw['objective']['terms'][0]['scale'] = 1
    config = {'schema': '1', 'samples': 2, 'seed': 0, 'sensitivity_steps': [-1, 1],
              'perturbations': [{'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform',
                                 'half_width_mm': 1}],
              'compensator': {'surface': 1, 'parameter': 'thickness_mm', 'min_mm': 1,
                              'max_mm': 3, 'max_evaluations': 21}}
    result = run_tolerance_job(source, contract.DesignSpec.from_dict(raw), tmp_path / 'out',
                               FocusBackend, config)
    for trial in [result['nominal'], *result['sensitivity'], *result['monte_carlo']]:
        search = trial['compensated']
        assert search['status'] == 'pass' and search['best']['verified']
        assert search['best']['objective_value'] == search['best']['measurements'][0]['value']
        assert all(len(h['objective_breakdown']['terms']) == 1 for h in search['history'])
    assert result['nominal']['objective_breakdown']['value'] == 0
    assert result['baseline_restored']


def test_field_wave_axis_and_frequency_remain_distinct_objective_requests():
    raw = raw_spec()
    raw.update(fields=[1, 2], wavelengths=[1, 2], frequencies_cyc_per_mm=[10, 20])
    raw['requirements'] = [{'id': 'track', 'metric': 'total_track_mm', 'unit': 'mm', 'min': 0}]
    raw['objective']['terms'] = [
        {'metric': 'mtf', 'unit': '1', 'field': f, 'wavelength': w, 'frequency': n,
         'axis': a, 'target': .8, 'scale': .2, 'weight': 1}
        for f in (1, 2) for w in (1, 2) for n in (10, 20) for a in ('tangential', 'sagittal')]
    spec = contract.DesignSpec.from_dict(raw)
    values = [dict(t, value=.6) for t in spec.objective_metrics]
    result = contract.objective_breakdown(spec, values)
    assert len({t['key'] for t in result['terms']}) == 16
    assert result['value'] == pytest.approx(1)


@pytest.mark.tier1
def test_portable_evaluates_objective_only_metrics(singlet):  # noqa: F811 -- pytest fixture injection
    from _lib.optiland_backend import OptilandBackend
    raw = raw_spec()
    raw['requirements'] = [{'id': 'track', 'metric': 'total_track_mm', 'unit': 'mm', 'min': 0}]
    with OptilandBackend(singlet) as backend:
        spec = contract.DesignSpec.from_dict(raw)
        measurements = backend.evaluate(spec)
    assert {r['metric'] for r in measurements} == {'efl_mm', 'rms_spot_um', 'total_track_mm'}
    assert math.isfinite(contract.objective_value(spec, measurements))
