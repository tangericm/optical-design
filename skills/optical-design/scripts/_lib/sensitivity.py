"""Source-preserving local central differences with explicit finite-step evidence."""
from __future__ import annotations

import copy
import math
import platform
import shutil
import time
from pathlib import Path

from _lib.design_contract import UNITS, DesignSpec, assess, finite, metric_key, objective_breakdown
from _lib.design_jobs import sha256, write_json
from _lib.optimization import _fixed_inspection


def validate_perturbations(raw: dict) -> dict:
    if not isinstance(raw, dict) or set(raw) != {'schema', 'parameters'} or raw['schema'] != '1':
        raise ValueError("sensitivity requires schema '1' and parameters only")
    config = copy.deepcopy(raw)
    parameters = config['parameters']
    if not isinstance(parameters, list) or not 1 <= len(parameters) <= 16:
        raise ValueError('declare 1 through 16 sensitivity parameters')
    seen = set()
    for parameter in parameters:
        if not isinstance(parameter, dict) or set(parameter) != {'surface', 'parameter', 'step_mm'}:
            raise ValueError('each parameter requires surface, parameter and step_mm only')
        surface, name = parameter['surface'], parameter['parameter']
        if type(surface) is not int or surface < 1:
            raise ValueError('parameter surface must be a positive physical surface index')
        if name not in {'radius_mm', 'thickness_mm'}:
            raise ValueError('parameters support radius_mm and thickness_mm only')
        if finite(parameter['step_mm'], 'step_mm') <= 0:
            raise ValueError('step_mm must be strictly positive')
        if (surface, name) in seen:
            raise ValueError('duplicate sensitivity surface/parameter')
        seen.add((surface, name))
    return config


def _metadata(row):
    result = copy.deepcopy(row)
    result.pop('value', None)
    # The FFT cutoff/grid changes physically with prescription. The requested
    # frequency, interpolation method and analysis settings must still match.
    if isinstance(result.get('analysis'), dict):
        result['analysis'].pop('frequency_range_cyc_per_mm', None)
    return result


def validate_step_vector(parameters, vector):
    """Share physical/representability checks between live and offline evidence."""
    if len(parameters) != len(vector):
        raise ValueError('sensitivity parameter vector length mismatch')
    for p, original in zip(parameters, vector):
        original = finite(original, 'baseline parameter')
        minus, plus = original - p['step_mm'], original + p['step_mm']
        if not math.isfinite(minus) or not math.isfinite(plus) or not minus < original < plus:
            raise ValueError('step_mm must produce two distinct finite parameter values')
        if p['parameter'] == 'thickness_mm' and minus <= 0:
            raise ValueError('thickness sensitivity steps must stay strictly positive')
        if p['parameter'] == 'radius_mm' and minus <= 0 <= plus:
            raise ValueError('radius sensitivity steps cannot reach zero or cross plane curvature')


def _measurements(rows, spec, baseline=None):
    if not isinstance(rows, list) or not rows:
        raise ValueError('sensitivity requires available measurements')
    indexed = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('metric') not in UNITS:
            raise ValueError('unsupported sensitivity measurement')
        key = metric_key(row)
        if key in indexed:
            raise ValueError(f'duplicate sensitivity measurement: {key}')
        if row.get('unit') != UNITS[row['metric']] or row.get('reason') or row.get('error'):
            raise ValueError(f'unavailable or incomparable sensitivity measurement: {key}')
        finite(row.get('value'), 'sensitivity measurement')
        indexed[key] = row
    assessment = assess(spec, rows)
    if any(r['status'] in {'unavailable', 'incomparable'} for r in assessment['requirements']):
        raise ValueError('required sensitivity metric unavailable or incomparable')
    if baseline is not None:
        if set(indexed) != set(baseline):
            raise ValueError('sensitivity measurement identities changed')
        if any(_metadata(row) != _metadata(baseline[key]) for key, row in indexed.items()):
            raise ValueError('sensitivity measurement metadata changed')
    return indexed, assessment


def _difference(original, minus, plus, step):
    negative, positive = minus - original, plus - original
    derivative = (positive / step - negative / step) / 2
    second = positive + negative
    effect = abs(derivative * step)
    scale = abs(positive) + abs(negative)
    if math.isfinite(scale):
        nonlinearity = abs(second) / scale if scale else 0.0
    else:
        largest = max(abs(positive), abs(negative))
        nonlinearity = abs(second / largest) / (abs(positive) / largest + abs(negative) / largest)
    values = {'baseline_value': original, 'minus_value': minus, 'plus_value': plus,
              'derivative_per_mm': derivative, 'declared_step_effect': effect,
              'minus_delta': negative, 'plus_delta': positive,
              'max_absolute_step_effect': max(abs(negative), abs(positive)),
              'second_difference': second, 'second_derivative_per_mm2': (second / step) / step,
              'nonlinearity_indicator': nonlinearity}
    for name, value in values.items():
        finite(value, name)
    return values


def run_sensitivity_job(model, spec: DesignSpec, out, factory, perturbations: dict, *, cancelled=None) -> dict:
    """Evaluate baseline and exactly two trials per parameter; never accept an edit.

    Analysis attempts share the spec budget. Recovery and context-manager teardown
    run outside deadline/cancellation; only successful teardown permits a receipt.
    """
    spec = DesignSpec.from_dict(spec.data)
    frozen_spec = copy.deepcopy(spec.data)
    config = validate_perturbations(perturbations)
    parameters = config['parameters']
    maximum = frozen_spec['budget']['max_evaluations']
    if 1 + 2 * len(parameters) > maximum:
        raise ValueError('evaluation budget must cover baseline and both sides of every parameter')
    model, out = Path(model).resolve(strict=True), Path(out).resolve()
    if not model.is_file():
        raise ValueError('model must be a file')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('output directory must be new or empty; existing evidence is immutable')
    original_hash = sha256(model)
    out.mkdir(parents=True, exist_ok=True)
    working, snapshot = out / ('working' + model.suffix), out / ('source_snapshot' + model.suffix)
    baseline_path = snapshot
    deadline = time.monotonic() + frozen_spec['budget']['timeout_s']
    count, history, trials, sensitivities = 0, [], [], []
    initial, baseline, baseline_metrics = None, None, None
    restored, cleanup_error = False, None

    def check_time():
        if cancelled and cancelled():
            raise InterruptedError('sensitivity cancelled')
        if time.monotonic() >= deadline:
            raise TimeoutError('sensitivity time budget exhausted between native calls')
        if spec.data != frozen_spec:
            raise RuntimeError('sensitivity specification changed during execution')

    def call(function, *args):
        check_time()
        result = function(*args)
        check_time()
        return result

    try:
        shutil.copy2(model, working)
        shutil.copy2(model, snapshot)
        if sha256(snapshot) != original_hash or sha256(working) != original_hash:
            raise RuntimeError('source changed while making sensitivity copies')
        write_json(out / 'spec.json', frozen_spec)
        write_json(out / 'perturbations.json', config)
        spec_hash, config_hash = sha256(out / 'spec.json'), sha256(out / 'perturbations.json')
        with factory(working) as backend:
            recovery, active_error = snapshot, None
            try:
                initial = copy.deepcopy(call(backend.inspect))
                baseline_path = out / ('baseline-model' + getattr(backend, 'model_suffix', model.suffix))
                call(backend.save, baseline_path)
                recovery = baseline_path
                baseline_hash = sha256(baseline_path)
                allowed = {s['index'] for s in initial['surfaces']
                           if 0 < s['index'] < initial['image_surface'] and not s.get('is_image')}
                if any(p['surface'] not in allowed for p in parameters):
                    raise ValueError('sensitivity surface must exclude object/image and identify a physical surface')
                vector = [finite(call(backend.get_parameter, p['surface'], p['parameter']),
                                 'baseline parameter') for p in parameters]
                validate_step_vector(parameters, vector)
                fixed = _fixed_inspection(initial, initial, parameters)

                def verify(expected):
                    actual = [finite(call(backend.get_parameter, p['surface'], p['parameter']),
                                     'parameter readback') for p in parameters]
                    for p, requested, found, original in zip(parameters, expected, actual, vector):
                        tolerance = min(max(abs(requested) * 1e-12, 1e-12), p['step_mm'] * 1e-6)
                        if abs(found - requested) > tolerance or (requested != original and found == original):
                            raise RuntimeError('parameter readback did not reproduce declared sensitivity vector')
                    inspection = copy.deepcopy(call(backend.inspect))
                    if _fixed_inspection(inspection, initial, parameters) != fixed:
                        raise RuntimeError('fixed optical model invariants changed')
                    # Verify the inspection agrees with the dedicated parameter getter.
                    surfaces = {s['index']: s for s in inspection['surfaces']}
                    for p, found in zip(parameters, actual):
                        if surfaces[p['surface']][p['parameter']] != found:
                            raise RuntimeError('inspection and parameter readback disagree')
                    return inspection, actual

                def load_baseline():
                    if sha256(baseline_path) != baseline_hash:
                        raise RuntimeError('saved baseline changed during sensitivity')
                    call(backend.load, baseline_path)
                    if call(backend.inspect) != initial:
                        raise RuntimeError('baseline restoration did not reproduce original inspection')

                def evaluate(expected, kind, parameter_index=None, direction=None):
                    nonlocal count
                    if count >= maximum:
                        raise RuntimeError('evaluation budget exhausted')
                    verify(expected)
                    check_time()
                    count += 1
                    rows = copy.deepcopy(call(backend.evaluate, spec))
                    inspection, actual = verify(expected)
                    indexed, assessment = _measurements(rows, spec, baseline_metrics)
                    entry = {'kind': kind, 'parameters_mm': actual, 'inspection': inspection,
                             'measurements': rows, 'assessment': assessment}
                    if parameter_index is not None:
                        entry.update(parameter_index=parameter_index, direction=direction,
                                     requested_parameters_mm=list(expected))
                    if spec.objective is not None:
                        entry['objective_breakdown'] = objective_breakdown(spec, rows)
                        entry['objective_value'] = entry['objective_breakdown']['value']
                    history.append(entry)
                    return entry, indexed

                load_baseline()
                baseline, baseline_metrics = evaluate(vector, 'baseline')
                write_json(out / 'baseline.json', baseline)
                for index, p in enumerate(parameters):
                    pair = []
                    for direction in (-1, 1):
                        load_baseline()
                        requested = list(vector)
                        requested[index] += direction * p['step_mm']
                        call(backend.set_parameter, p['surface'], p['parameter'], requested[index])
                        trial, measurements = evaluate(requested, 'perturbation', index, direction)
                        trials.append(trial)
                        pair.append((trial, measurements))
                    minus, plus = pair
                    result = {'parameter_index': index, **copy.deepcopy(p), 'baseline_mm': vector[index],
                              'metrics': []}
                    for key, row in baseline_metrics.items():
                        identity = {k: row[k] for k in ('metric', 'field', 'wavelength', 'frequency', 'axis', 'unit') if k in row}
                        result['metrics'].append({**identity, 'metric_key': key,
                            **_difference(row['value'], minus[1][key]['value'], plus[1][key]['value'], p['step_mm'])})
                    if spec.objective is not None:
                        unit = '1' if spec.objective.get('aggregation') else UNITS[spec.objective['metric']]
                        result['objective'] = {'unit': unit, **_difference(baseline['objective_value'],
                            minus[0]['objective_value'], plus[0]['objective_value'], p['step_mm'])}
                    sensitivities.append(result)
            except BaseException as exc:
                active_error = exc
                raise
            finally:
                try:
                    backend.load(recovery)
                    restored = initial is None or backend.inspect() == initial
                    if not restored:
                        raise RuntimeError('baseline restoration did not reproduce original inspection')
                except BaseException as exc:
                    cleanup_error = f'{type(exc).__name__}: {exc}'
                    if active_error is None:
                        raise
        check_time()
        if sha256(model) != original_hash or sha256(snapshot) != original_hash:
            raise RuntimeError('source or source snapshot changed during sensitivity')
        if sha256(baseline_path) != baseline_hash:
            raise RuntimeError('saved baseline changed during sensitivity')
        if sha256(out / 'spec.json') != spec_hash or sha256(out / 'perturbations.json') != config_hash:
            raise RuntimeError('saved sensitivity specification or perturbations changed')
        rankings = []
        for key, row in baseline_metrics.items():
            ranked = []
            for sensitivity in sensitivities:
                metric = next(m for m in sensitivity['metrics'] if m['metric_key'] == key)
                ranked.append({k: sensitivity[k] for k in ('parameter_index', 'surface', 'parameter', 'step_mm')} |
                              {'metric_key': key, 'unit': row['unit'], 'declared_step_effect': metric['declared_step_effect']})
            rankings.append({'metric_key': key, 'unit': row['unit'],
                             'parameters': sorted(ranked, key=lambda r: -r['declared_step_effect'])})
        report = {'schema': '1', 'action': 'sensitivity', 'status': 'completed',
                  'source': {'path': str(model), 'sha256': original_hash}, 'source_unchanged': True,
                  'spec': frozen_spec, 'perturbations': config, 'baseline': baseline, 'candidate': None,
                  'history': history, 'trials': trials, 'sensitivities': sensitivities, 'rankings': rankings,
                  'evaluations': count, 'baseline_restored': restored, 'saved_candidate_verified': False,
                  'artifacts': {'baseline_model': str(baseline_path), 'baseline_sha256': baseline_hash,
                                'source_snapshot_sha256': sha256(snapshot)},
                  'spec_sha256': spec_hash, 'perturbations_sha256': config_hash,
                  'python_version': platform.python_version(),
                  'method': 'central_finite_difference_at_declared_steps',
                  'ranking_basis': 'absolute derivative times declared step; within identical metric and unit only',
                  'time_budget_policy': 'cooperative_between_native_calls',
                  'scope': 'local numerical sensitivity; no optimization, tolerance distribution or manufacturing yield'}
        write_json(out / 'report.json', report)
        return report
    except BaseException as exc:
        write_json(out / 'failure.json', {'schema': '1', 'action': 'sensitivity', 'status': 'failed',
            'error': str(exc), 'error_type': type(exc).__name__, 'cleanup_error': cleanup_error,
            'source': {'path': str(model), 'sha256': original_hash}, 'spec': frozen_spec, 'perturbations': config,
            'source_unchanged': model.is_file() and sha256(model) == original_hash,
            'baseline_restored': restored, 'baseline': baseline, 'evaluations': count,
            'history': history, 'trials': trials, 'sensitivities': sensitivities})
        raise
