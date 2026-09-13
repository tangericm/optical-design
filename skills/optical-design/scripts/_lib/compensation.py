"""Bounded final-air-gap compensation, retaining paired trial evidence."""
from __future__ import annotations

import copy
import math

from _lib.design_contract import assess, finite, objective_breakdown


def validate_compensator(config, spec, perturbations):
    expected = {'surface', 'parameter', 'min_mm', 'max_mm', 'max_evaluations'}
    if not isinstance(config, dict) or set(config) != expected:
        raise ValueError('compensator requires surface, parameter, min_mm, max_mm and max_evaluations')
    if type(config['surface']) is not int or config['surface'] < 1:
        raise ValueError('compensator surface must be a positive physical surface index')
    if config['parameter'] != 'thickness_mm':
        raise ValueError('compensator parameter must be thickness_mm for the final air gap')
    lo, hi = finite(config['min_mm'], 'compensator minimum'), finite(config['max_mm'], 'compensator maximum')
    if not 0 < lo < hi:
        raise ValueError('compensator requires 0 < min_mm < max_mm')
    if type(config['max_evaluations']) is not int or not 3 <= config['max_evaluations'] <= 201:
        raise ValueError('compensator max_evaluations must be an integer from 3 through 201')
    if spec.objective is None:
        raise ValueError('compensation requires an explicit design objective')
    if (config['surface'], config['parameter']) in perturbations:
        raise ValueError('compensator cannot also be a perturbed parameter')


def compensate(backend, spec, config, original, reset, call, evaluate):
    """Search on identical perturbations; reset failure is fatal, candidate errors are evidence.

    ``reset`` restores/verifies the nominal baseline and reapplies the original draws.
    The caller owns elapsed-time checks and total evaluation accounting. One of the
    per-trial evaluation slots is reserved for independently reproducing the best result.
    The bounded local search is deliberately not a proof of global optimality.
    """
    result = {'status': 'analysis_failed', 'best': None, 'history': [], 'evaluations': 0,
              'analysis_failures': 0, 'candidate_attempts': 0, 'settings': copy.deepcopy(config),
              'method': 'bounded coarse grid then golden interval refinement; best feasible retention',
              'evaluation_budget_scope': 'additional analysis calls per trial, including final verification',
              'baseline_reused': False}
    original['compensated'] = result
    if original['status'] == 'analysis_failed':
        result['error'] = 'uncompensated trial failed; no trusted perturbed baseline for compensation'
        return result
    reference = copy.deepcopy(call(backend.inspect))
    lo, hi = config['min_mm'], config['max_mm']
    sign = 1 if spec.objective['direction'] == 'maximize' else -1
    best, best_score = None, -math.inf

    def verify(position):
        inspection = copy.deepcopy(call(backend.inspect))
        if inspection['invariants'] != reference['invariants']:
            raise RuntimeError('compensation changed optical invariants outside the final gap')
        if 'axial_positions_mm' in reference:
            before = reference['axial_positions_mm']
            after = inspection.get('axial_positions_mm')
            if not isinstance(after, list) or len(after) != len(before) or after[:-1] != before[:-1]:
                raise RuntimeError('compensation changed nonimage axial geometry')
            expected = finite(before[-1], 'reference image position') + position - reference['focus_mm']
            if not math.isclose(finite(after[-1], 'image position'), expected, rel_tol=1e-12, abs_tol=1e-10):
                raise RuntimeError('image axial displacement differs from compensator travel')
        actual = finite(call(backend.get_parameter, config['surface'], config['parameter']), 'focus readback')
        reported = finite(inspection.get('focus_mm'), 'inspection focus readback')
        if (not lo <= actual <= hi or not math.isclose(actual, position, rel_tol=1e-12, abs_tol=1e-12)
                or not math.isclose(reported, position, rel_tol=1e-12, abs_tol=1e-12)
                or (position != reference['focus_mm'] and actual == reference['focus_mm'])):
            raise RuntimeError('compensator focus did not reproduce at readback within bounds')
        for p in original['perturbations']:
            value = finite(call(backend.get_parameter, p['surface'], p['parameter']), 'perturbation readback')
            if (not math.isclose(value, p['value_mm'], rel_tol=1e-12, abs_tol=1e-12)
                    or (p['delta_mm'] != 0 and value == p['baseline_mm'])):
                raise RuntimeError('compensation changed an applied perturbation at readback')
        return inspection

    if original['assessment']['passes'] and lo <= reference['focus_mm'] <= hi:
        try:
            verify(reference['focus_mm'])
            original['objective_breakdown'] = objective_breakdown(spec, original['measurements'])
            original['objective_value'] = original['objective_breakdown']['value']
            best_score = sign * original['objective_value']
            best = {'focus_mm': reference['focus_mm'], 'inspection': reference,
                    'measurements': copy.deepcopy(original['measurements']),
                    'assessment': copy.deepcopy(original['assessment']), 'verified': False,
                    'objective_value': original['objective_value'],
                    'objective_breakdown': copy.deepcopy(original['objective_breakdown'])}
            result['baseline_reused'] = True
        except (TimeoutError, InterruptedError):
            raise
        except Exception as exc:  # noqa: BLE001 -- unusable original objective cannot seed the search.
            result['baseline_reuse_error'] = str(exc)

    def sample(position, *, verification=False):
        nonlocal best, best_score
        # A failed reset must stop the job, even when previous candidates were accepted.
        reset()
        if call(backend.inspect) != reference:
            raise RuntimeError('perturbed baseline did not reproduce before compensation')
        row = {'focus_mm': position, 'verification': verification, 'status': 'analysis_failed',
               'measurements': [], 'assessment': {'passes': False, 'requirements': []}}
        result['candidate_attempts'] += 1
        score = -math.inf
        try:
            call(backend.set_focus, position)
            verify(position)
            result['evaluations'] += 1
            row['measurements'] = evaluate()
            row['inspection'] = verify(position)
            row['assessment'] = assess(spec, row['measurements'])
            row['objective_breakdown'] = objective_breakdown(spec, row['measurements'])
            value = row['objective_breakdown']['value']
            score = sign * value
            row['objective_value'] = value
            row['status'] = 'pass' if row['assessment']['passes'] else 'fail'
            if not verification and row['assessment']['passes'] and score > best_score:
                best, best_score = copy.deepcopy(row), score
        except (TimeoutError, InterruptedError) as exc:
            row.update(error=str(exc), error_type=type(exc).__name__)
            result['analysis_failures'] += 1
            result['history'].append(row)
            raise
        except Exception as exc:  # noqa: BLE001 -- retain native rejection/readback/analysis failures.
            row.update(error=str(exc), error_type=type(exc).__name__)
            result['analysis_failures'] += 1
        result['history'].append(row)
        return row, score

    # Limit candidate attempts as well as analyses: rejected setters cannot create an unbounded loop.
    search_budget = config['max_evaluations'] - 1
    coarse_count = min(7, search_budget)
    samples = []
    for i in range(coarse_count):
        position = lo + (hi - lo) * i / (coarse_count - 1)
        _, score = sample(position)
        samples.append((position, score))
    valid = [(position, score) for position, score in samples if math.isfinite(score)]
    if valid:
        peak = max(valid, key=lambda point: point[1])[0]
        step = (hi - lo) / (coarse_count - 1)
        left, right = max(lo, peak - step), min(hi, peak + step)
        ratio = (math.sqrt(5) - 1) / 2
        while result['candidate_attempts'] + 2 <= search_budget:
            x1, x2 = right - ratio * (right - left), left + ratio * (right - left)
            _, y1 = sample(x1)
            _, y2 = sample(x2)
            if y1 > y2:
                right = x2
            else:
                left = x1
    if best is not None:
        verified, score = sample(best['focus_mm'], verification=True)
        if (verified['status'] == 'pass'
                and math.isclose(score, best_score, rel_tol=1e-5, abs_tol=1e-8)):
            verified['verified'] = True
            result['best'] = copy.deepcopy(verified)
            result['status'] = 'pass'
        else:
            result['error'] = 'best feasible compensated result did not reproduce'
            if verified['status'] != 'analysis_failed':
                result['analysis_failures'] += 1
    elif any(row['status'] != 'analysis_failed' for row in result['history']):
        result['status'] = 'fail'
    else:
        result['error'] = 'all compensation candidates failed analysis or readback'
    return result
