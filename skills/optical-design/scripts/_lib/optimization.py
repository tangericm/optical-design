"""Small-dimensional bounded search with independently verified optical acceptance."""
from __future__ import annotations

import copy
import math
import platform
import shutil
import time
from pathlib import Path

from _lib.design_contract import DesignSpec, assess, finite, objective_breakdown
from _lib.design_jobs import sha256, verify_artifact_hashes, write_json


def validate_variables(raw: dict, spec: DesignSpec) -> dict:
    if spec.objective is None:
        raise ValueError('optimization requires an explicit objective')
    if not isinstance(raw, dict) or set(raw) != {'schema', 'variables'} or raw['schema'] != '1':
        raise ValueError("variables specification requires schema '1' and variables only")
    config = copy.deepcopy(raw)
    variables = config['variables']
    if not isinstance(variables, list) or not 1 <= len(variables) <= 4:
        raise ValueError('declare 1 through 4 bounded variables')
    seen = set()
    for variable in variables:
        if not isinstance(variable, dict) or set(variable) != {'surface', 'parameter', 'min_mm', 'max_mm'}:
            raise ValueError('each variable requires surface, parameter, min_mm and max_mm only')
        surface, parameter = variable['surface'], variable['parameter']
        if type(surface) is not int or surface < 1:
            raise ValueError('variable surface must be a positive physical surface index')
        if parameter not in {'radius_mm', 'thickness_mm'}:
            raise ValueError('variables support radius_mm and thickness_mm only')
        lo, hi = finite(variable['min_mm'], 'min_mm'), finite(variable['max_mm'], 'max_mm')
        if lo >= hi or not math.isfinite(hi - lo):
            raise ValueError('variable requires finite min_mm < max_mm and finite width')
        if parameter == 'radius_mm' and lo <= 0 <= hi:
            raise ValueError('radius bounds must exclude zero and cannot cross plane curvature')
        if parameter == 'thickness_mm' and lo <= 0:
            raise ValueError('thickness bounds must be strictly positive')
        identity = (surface, parameter)
        if identity in seen:
            raise ValueError('duplicate variable surface/parameter')
        seen.add(identity)
    return config


def _fixed_inspection(inspection, initial, variables):
    """Remove only declared cells; verify derived portable axial positions explicitly.

    Native inspection repeats the prescription in invariants. Optiland stores native
    geometry plus absolute axial coordinates: changing thickness translates every
    downstream surface by the sum of preceding declared thickness changes.
    """
    value = copy.deepcopy(inspection)
    identities = {(v['surface'], v['parameter']) for v in variables}
    for collection in ('surfaces', 'prescription'):
        for surface in value.get(collection, []):
            for name in ('radius_mm', 'thickness_mm'):
                if (surface['index'], name) in identities:
                    surface[name] = None
    if (value['image_surface'] - 1, 'thickness_mm') in identities:
        value['focus_mm'] = None
    if 'axial_positions_mm' in initial:
        actual_positions = inspection.get('axial_positions_mm', [])
        if len(actual_positions) != len(initial['axial_positions_mm']):
            raise RuntimeError('fixed axial geometry surface count changed')
        actual_prescription = {s['index']: s for s in inspection['surfaces']}
        baseline_prescription = {s['index']: s for s in initial['surfaces']}
        shift = 0.0
        for index, (actual, original) in enumerate(zip(actual_positions, initial['axial_positions_mm'])):
            if isinstance(original, (int, float)):
                if not math.isclose(finite(actual, 'axial readback'), original + shift,
                                    rel_tol=1e-12, abs_tol=1e-10):
                    raise RuntimeError('fixed axial geometry changed outside declared thicknesses')
            elif actual != original:
                raise RuntimeError('fixed object axial geometry changed')
            if (index, 'thickness_mm') in identities:
                shift += (actual_prescription[index]['thickness_mm'] -
                          baseline_prescription[index]['thickness_mm'])
        value['axial_positions_mm'] = copy.deepcopy(initial['axial_positions_mm'])
    invariants = value['invariants']
    for surface in invariants.get('surfaces', []):
        for name in ('radius_mm', 'thickness_mm'):
            if (surface['index'], name) in identities and name in surface:
                surface[name] = None
    if 'surface_group' in invariants:
        original_surfaces = initial['invariants']['surface_group']['surfaces']
        actual_prescription = {s['index']: s for s in inspection['surfaces']}
        baseline_prescription = {s['index']: s for s in initial['surfaces']}
        shift = 0.0
        for index, surface in enumerate(invariants['surface_group']['surfaces']):
            geometry = surface['geometry']
            if 'z' in geometry['cs']:
                original_z = original_surfaces[index]['geometry']['cs']['z']
                if isinstance(original_z, (int, float)):
                    expected = original_z + shift
                    if not math.isclose(finite(geometry['cs']['z'], 'axial readback'), expected,
                                        rel_tol=1e-12, abs_tol=1e-10):
                        raise RuntimeError('fixed axial geometry changed outside declared thicknesses')
                    geometry['cs']['z'] = original_z
                elif geometry['cs']['z'] != original_z:
                    raise RuntimeError('fixed object axial geometry changed')
            if (index, 'radius_mm') in identities:
                geometry['radius'] = None
            if (index, 'thickness_mm') in identities:
                surface.pop('thickness', None)
                shift += (actual_prescription[index]['thickness_mm'] -
                          baseline_prescription[index]['thickness_mm'])
    return value


def _rank(entry, sign):
    """Feasible points always win; violation reduction guides an infeasible baseline."""
    violation = 0.0
    for row in entry['assessment']['requirements']:
        if row['status'] in {'unavailable', 'incomparable'}:
            violation += 1e100
        elif row['status'] == 'fail':
            requirement, actual = row['requirement'], row['value']
            for key, direction in (('min', -1), ('max', 1)):
                if key in requirement:
                    bound = requirement[key]
                    violation += max(0, direction * (actual - bound)) / max(1, abs(bound))
    return (int(entry['assessment']['passes']), -violation, sign * entry['objective_value'])


def run_optimization_job(model, spec: DesignSpec, out, factory, variables: dict, *, cancelled=None,
                         validation_spec: DesignSpec | None = None) -> dict:
    """Optimize a disposable copy, reserve two evaluations for candidate verification.

    Exceptions abort acceptance, restore the backend even after deadline/cancellation,
    and retain failure evidence. A receipt is written only after backend teardown.
    """
    spec = DesignSpec.from_dict(spec.data)
    frozen_spec = copy.deepcopy(spec.data)
    config = validate_variables(variables, spec)
    validation = None
    if validation_spec is not None:
        validation_spec = DesignSpec.from_dict(validation_spec.data)
        if validation_spec.objective is not None or 'focus' in validation_spec.data:
            raise ValueError('validation specification must contain requirements without objective or focus')
        validation = {'status': 'not_run_no_candidate', 'spec': copy.deepcopy(validation_spec.data),
                      'evaluations': 0, 'baseline': None, 'candidate': None,
                      'evaluation_differences': [key for key in ('fields', 'wavelengths',
                          'frequencies_cyc_per_mm', 'analysis') if spec.data[key] != validation_spec.data[key]],
                      'scope': 'separate-spec numerical check; not measured physical validation or unbiased holdout',
                      'budget_policy': 'all analyses share optimization budget; validation stage also obeys its own timeout'}
    reserved = 4 if validation is not None else 2
    variables = config['variables']
    model, out = Path(model).resolve(strict=True), Path(out).resolve()
    if not model.is_file():
        raise ValueError('model must be a file')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('output directory must be new or empty; existing evidence is immutable')
    original_hash = sha256(model)
    out.mkdir(parents=True, exist_ok=True)
    working, snapshot = out / ('working' + model.suffix), out / ('source_snapshot' + model.suffix)
    baseline_path = snapshot
    deadline = time.monotonic() + spec.data['budget']['timeout_s']
    maximum = spec.data['budget']['max_evaluations']
    count, history = 0, []
    initial, baseline, candidate, rejected_candidate = None, None, None, None
    validation_deadline = None
    restored, cleanup_error = False, None
    evidence_hashes = {model: original_hash}
    sign = 1 if spec.objective['direction'] == 'maximize' else -1

    def check_time():
        if spec.data != frozen_spec:
            raise RuntimeError('specification changed during optimization')
        if cancelled and cancelled():
            raise InterruptedError('optimization cancelled')
        if time.monotonic() >= deadline:
            raise TimeoutError('optimization time budget exhausted between native calls')
        if validation_deadline is not None and time.monotonic() >= validation_deadline:
            raise TimeoutError('validation time budget exhausted between native calls')

    def call(function, *args):
        check_time()
        result = function(*args)
        check_time()
        return result

    try:
        shutil.copy2(model, working)
        shutil.copy2(model, snapshot)
        if sha256(working) != original_hash or sha256(snapshot) != original_hash:
            raise RuntimeError('source copy changed before optimization')
        evidence_hashes[snapshot] = original_hash
        write_json(out / 'spec.json', frozen_spec)
        write_json(out / 'variables.json', config)
        for path in (out / 'spec.json', out / 'variables.json'):
            evidence_hashes[path] = sha256(path)
        if validation is not None:
            write_json(out / 'validation-spec.json', validation_spec.data)
            validation['spec_sha256'] = sha256(out / 'validation-spec.json')
            evidence_hashes[out / 'validation-spec.json'] = validation['spec_sha256']
        with factory(working) as backend:
            recovery = snapshot
            active_error = None
            try:
                initial = copy.deepcopy(call(backend.inspect))
                baseline_path = out / ('baseline-model' + getattr(backend, 'model_suffix', model.suffix))
                candidate_path = out / ('candidate-model' + getattr(backend, 'model_suffix', model.suffix))
                call(backend.save, baseline_path)
                evidence_hashes[baseline_path] = sha256(baseline_path)
                recovery = baseline_path
                allowed = {s['index'] for s in initial['surfaces']
                           if s['index'] > 0 and not s.get('is_image') and s['index'] < initial['image_surface']}
                if any(v['surface'] not in allowed for v in variables):
                    raise ValueError('variable surface must exclude object/image and identify a physical surface')
                baseline_vector = [finite(call(backend.get_parameter, v['surface'], v['parameter']),
                                          'baseline parameter') for v in variables]
                fixed = _fixed_inspection(initial, initial, variables)

                def verify(expected, *, bounded):
                    actual = [finite(call(backend.get_parameter, v['surface'], v['parameter']),
                                     'parameter readback') for v in variables]
                    for v, requested, found, original in zip(variables, expected, actual, baseline_vector):
                        if bounded and not v['min_mm'] <= found <= v['max_mm']:
                            raise RuntimeError('parameter readback lies outside declared bounds')
                        if (not math.isclose(found, requested, rel_tol=1e-12, abs_tol=1e-12) or
                                (requested != original and found == original)):
                            raise RuntimeError('all-variable readback did not reproduce requested vector')
                    inspection = copy.deepcopy(call(backend.inspect))
                    if _fixed_inspection(inspection, initial, variables) != fixed:
                        raise RuntimeError('fixed optical model invariants changed')
                    return inspection, actual

                def evaluate(expected, kind, *, bounded=True, analysis_spec=None):
                    nonlocal count
                    if count >= maximum:
                        raise RuntimeError('evaluation budget exhausted')
                    verify(expected, bounded=bounded)
                    count += 1  # Count attempted analyses, including failed or late calls.
                    if analysis_spec is not None:
                        validation['evaluations'] += 1
                    selected_spec = spec if analysis_spec is None else analysis_spec
                    if analysis_spec is not None and analysis_spec.data != validation['spec']:
                        raise RuntimeError('validation specification changed before analysis')
                    rows = copy.deepcopy(call(backend.evaluate, selected_spec))
                    if analysis_spec is not None and analysis_spec.data != validation['spec']:
                        raise RuntimeError('validation specification changed during analysis')
                    inspection, actual = verify(expected, bounded=bounded)
                    entry = {'kind': kind, 'parameters_mm': actual, 'inspection': inspection,
                             'measurements': rows, 'assessment': assess(selected_spec, rows)}
                    if analysis_spec is None:
                        entry['objective_breakdown'] = objective_breakdown(spec, rows)
                        entry['objective_value'] = entry['objective_breakdown']['value']
                    history.append(entry)
                    return entry

                def apply(vector):
                    # Every point starts from an inspected native baseline, including solves.
                    call(backend.load, baseline_path)
                    if call(backend.inspect) != initial:
                        raise RuntimeError('baseline restoration did not reproduce before candidate')
                    for variable, position in zip(variables, vector):
                        call(backend.set_parameter, variable['surface'], variable['parameter'], position)
                    verify(vector, bounded=True)

                baseline = evaluate(baseline_vector, 'baseline', bounded=False)
                write_json(out / 'baseline.json', baseline)
                evidence_hashes[out / 'baseline.json'] = sha256(out / 'baseline.json')
                widths = [v['max_mm'] - v['min_mm'] for v in variables]
                start = [min(1.0, max(0.0, (x - v['min_mm']) / width))
                         for x, v, width in zip(baseline_vector, variables, widths)]
                best = None
                cache = {}

                def sample(point):
                    nonlocal best
                    key = tuple(point)
                    if key in cache:
                        return cache[key]
                    if count >= maximum - reserved:
                        return None
                    vector = [min(v['max_mm'], max(v['min_mm'], v['min_mm'] + x * width))
                              for x, v, width in zip(point, variables, widths)]
                    apply(vector)
                    entry = evaluate(vector, 'search')
                    cache[key] = entry
                    if entry['assessment']['passes'] and (best is None or
                            sign * entry['objective_value'] > sign * best['objective_value']):
                        best = entry
                    return entry

                center, current = start, sample(start)
                midpoint = [.5] * len(variables)
                middle = sample(midpoint)
                if middle and _rank(middle, sign) > _rank(current, sign):
                    center, current = midpoint, middle
                step = .5
                termination = 'evaluation_budget'
                # Normalized Hooke-Jeeves-style polling, with a coupled pattern move.
                while count < maximum - reserved and step >= 1e-6:
                    before, previous = list(center), current
                    for axis in range(len(variables)):
                        for direction in (1, -1):
                            point = list(center)
                            point[axis] = min(1.0, max(0.0, point[axis] + direction * step))
                            entry = sample(point)
                            if entry and _rank(entry, sign) > _rank(current, sign):
                                center, current = point, entry
                    if _rank(current, sign) > _rank(previous, sign):
                        point = [min(1.0, max(0.0, 2 * x - y)) for x, y in zip(center, before)]
                        entry = sample(point)
                        if entry and _rank(entry, sign) > _rank(current, sign):
                            center, current = point, entry
                    else:
                        step /= 2
                if step < 1e-6:
                    termination = 'normalized_step_limit'

                def require_gain(entry):
                    if (not entry['assessment']['passes'] or
                            sign * (entry['objective_value'] - baseline['objective_value']) <= spec.data['minimum_gain']):
                        raise RuntimeError('candidate no longer passes all requirements and minimum improvement')

                if best and sign * (best['objective_value'] - baseline['objective_value']) > spec.data['minimum_gain']:
                    apply(best['parameters_mm'])
                    candidate = evaluate(best['parameters_mm'], 'candidate_verification')
                    require_gain(candidate)
                    call(backend.save, candidate_path)
                    evidence_hashes[candidate_path] = sha256(candidate_path)
                    call(backend.load, candidate_path)
                    reloaded = evaluate(candidate['parameters_mm'], 'saved_reload_verification')
                    require_gain(reloaded)
                    if not math.isclose(candidate['objective_value'], reloaded['objective_value'],
                                        rel_tol=1e-5, abs_tol=1e-8):
                        raise RuntimeError('saved candidate objective changed on reload')
                    candidate = reloaded
                    if validation is not None:
                        # Search has ended. These results never feed back into candidate selection.
                        validation['status'] = 'analysis_failed'
                        validation_deadline = time.monotonic() + validation_spec.data['budget']['timeout_s']
                        call(backend.load, baseline_path)
                        if call(backend.inspect) != initial:
                            raise RuntimeError('baseline did not reproduce before validation')
                        validation['baseline'] = evaluate(baseline_vector, 'validation_baseline',
                                                         bounded=False, analysis_spec=validation_spec)
                        call(backend.load, candidate_path)
                        validation['candidate'] = evaluate(candidate['parameters_mm'], 'validation_candidate',
                                                          analysis_spec=validation_spec)
                        validation['status'] = ('passed' if validation['candidate']['assessment']['passes']
                                                else 'requirements_not_met')
                        validation_deadline = None
                        if validation['status'] != 'passed':
                            rejected_candidate, candidate = candidate, None
            except BaseException as exc:
                active_error = exc
                raise
            finally:
                # Recovery deliberately runs outside the exhausted budget.
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
        if sha256(model) != original_hash:
            raise RuntimeError('source changed during optimization; result cannot be accepted')
        verify_artifact_hashes(evidence_hashes)
        artifacts = {'baseline_model': str(baseline_path), 'baseline_sha256': evidence_hashes[baseline_path],
                     'source_snapshot_sha256': original_hash}
        if candidate:
            artifacts.update(candidate_model=str(candidate_path), candidate_sha256=evidence_hashes[candidate_path])
        if rejected_candidate:
            rejected_path = out / ('rejected-candidate-model' + candidate_path.suffix)
            candidate_path.replace(rejected_path)
            artifacts.update(rejected_candidate_model=str(rejected_path),
                             rejected_candidate_sha256=evidence_hashes[candidate_path])
        report = {'schema': '1', 'action': 'optimize',
                  'status': ('improved' if candidate else 'validation_failed' if rejected_candidate
                             else 'no_acceptable_improvement'),
                  'source': {'path': str(model), 'sha256': original_hash}, 'source_unchanged': True,
                  'spec': frozen_spec, 'variables': config, 'baseline': baseline, 'candidate': candidate,
                  'history': history, 'evaluations': count, 'baseline_restored': restored,
                  'saved_candidate_verified': candidate is not None, 'artifacts': artifacts,
                  'spec_sha256': evidence_hashes[out / 'spec.json'], 'variables_sha256': evidence_hashes[out / 'variables.json'],
                  'python_version': platform.python_version(),
                  'search': {'method': 'normalized_bounded_pattern_search', 'global_optimum_proven': False,
                             'termination': termination, 'final_normalized_step': step,
                             'verification_evaluations_reserved': reserved},
                  'parameter_readback_tolerance': {'relative': 1e-12, 'absolute_mm': 1e-12,
                                                   'nonzero_delta_requires_actual_change': True},
                  'time_budget_policy': 'cooperative_between_native_calls'}
        if validation is not None:
            report.update(validation=validation, rejected_candidate=rejected_candidate)
        write_json(out / 'report.json', report)
        return report
    except BaseException as exc:
        failure = {'schema': '1', 'action': 'optimize', 'status': 'failed',
                   'error': str(exc), 'error_type': type(exc).__name__, 'cleanup_error': cleanup_error,
                   'baseline_restored': restored, 'source_unchanged': model.is_file() and sha256(model) == original_hash,
                   'evaluations': count, 'history': history}
        if validation is not None:
            failure['validation'] = validation
        write_json(out / 'failure.json', failure)
        raise
