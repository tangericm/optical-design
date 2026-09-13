"""Saved-model inspection and explicit edits with verified readback and recovery."""
from __future__ import annotations

import copy
import math
import platform
import shutil
import time
from pathlib import Path

from _lib.design_contract import DesignSpec, assess, finite, metric_key, objective_breakdown
from _lib.design_jobs import sha256, write_json
from _lib.optimization import _fixed_inspection


def validate_changes(raw):
    if not isinstance(raw, dict) or set(raw) != {'schema', 'changes'} or raw['schema'] != '1':
        raise ValueError("changes specification requires schema '1' and changes only")
    config = copy.deepcopy(raw)
    if not isinstance(config['changes'], list) or not 1 <= len(config['changes']) <= 16:
        raise ValueError('declare 1 through 16 explicit changes')
    seen = set()
    for change in config['changes']:
        if not isinstance(change, dict) or set(change) != {'surface', 'parameter', 'expected_mm', 'value_mm'}:
            raise ValueError('each change requires surface, parameter, expected_mm and value_mm only')
        surface, parameter = change['surface'], change['parameter']
        if type(surface) is not int or surface < 1:
            raise ValueError('change surface must be a positive physical surface index')
        if parameter not in {'radius_mm', 'thickness_mm'}:
            raise ValueError('changes support radius_mm and thickness_mm only')
        for name in ('expected_mm', 'value_mm'):
            value = finite(change[name], name)
            if parameter == 'radius_mm' and value == 0:
                raise ValueError('radius values must be nonzero')
            if parameter == 'thickness_mm' and value <= 0:
                raise ValueError('thickness values must be positive')
        if (surface, parameter) in seen:
            raise ValueError('duplicate change surface/parameter')
        seen.add((surface, parameter))
    return config


def run_inspect_job(model, out, factory, *, cancelled=None):
    """Inspect a saved copy without inventing requirements or running optical analyses."""
    return _run(model, out, factory, cancelled=cancelled)


def run_edit_job(model, spec, out, factory, changes, *, cancelled=None):
    """Apply explicit cells, then independently reload and gate against hard requirements."""
    config = validate_changes(changes)
    spec = DesignSpec.from_dict(spec.data)
    return _run(model, out, factory, spec=spec, config=config, cancelled=cancelled)


def _reproduces(before, after):
    """Compare saved-model measurement identities, availability, units and values."""
    def indexed(rows):
        result = {}
        for row in rows:
            key = metric_key(row)
            if key in result:
                raise RuntimeError('duplicate saved candidate measurement')
            result[key] = row
        return result
    left, right = indexed(before), indexed(after)
    if set(left) != set(right):
        return False
    for key, first in left.items():
        second = right[key]
        if first.get('unit') != second.get('unit'):
            return False
        a, b = first.get('value'), second.get('value')
        if a is None or b is None:
            if a != b or first.get('reason') != second.get('reason'):
                return False
        elif not math.isclose(finite(a, 'candidate measurement'), finite(b, 'reloaded measurement'),
                              rel_tol=1e-5, abs_tol=1e-8):
            return False
    return True


def _run(model, out, factory, *, spec=None, config=None, cancelled=None):
    action = 'edit' if spec is not None else 'inspect'
    frozen_spec = copy.deepcopy(spec.data) if spec is not None else None
    model, out = Path(model).resolve(strict=True), Path(out).resolve()
    if not model.is_file():
        raise ValueError('model must be a file')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('output directory must be new or empty; existing evidence is immutable')
    original_hash = sha256(model)
    out.mkdir(parents=True, exist_ok=True)
    working = out / ('working' + model.suffix)
    snapshot = out / ('source_snapshot' + model.suffix)
    baseline_path, candidate_path = snapshot, None
    deadline = time.monotonic() + (frozen_spec['budget']['timeout_s'] if frozen_spec else 120)
    maximum = frozen_spec['budget']['max_evaluations'] if frozen_spec else 0
    initial, baseline, candidate, rejected = None, None, None, None
    count, history, restored, cleanup_error = 0, [], False, None
    edits = config['changes'] if config else []
    evidence_hashes = {}

    def check():
        if cancelled and cancelled():
            raise InterruptedError(f'{action} cancelled')
        if time.monotonic() >= deadline:
            raise TimeoutError(f'{action} time budget exhausted between engine calls')
        if spec is not None and spec.data != frozen_spec:
            raise RuntimeError('design specification changed during edit')

    def call(function, *args):
        check()
        result = function(*args)
        check()
        return result

    try:
        check()
        shutil.copy2(model, working)
        shutil.copy2(model, snapshot)
        if sha256(working) != original_hash or sha256(snapshot) != original_hash:
            raise RuntimeError('source changed while taking input snapshots')
        evidence_hashes[snapshot] = original_hash
        if spec is not None:
            write_json(out / 'spec.json', frozen_spec)
            write_json(out / 'changes.json', config)
            for name in ('spec.json', 'changes.json'):
                evidence_hashes[out / name] = sha256(out / name)
        with factory(working) as backend:
            recovery, active_error = snapshot, None
            try:
                initial = copy.deepcopy(call(backend.inspect))
                suffix = getattr(backend, 'model_suffix', model.suffix)
                baseline_path = out / ('baseline-model' + suffix)
                candidate_path = out / ('candidate-model' + suffix)
                call(backend.save, baseline_path)
                evidence_hashes[baseline_path] = sha256(baseline_path)
                recovery = baseline_path
                call(backend.load, baseline_path)
                if call(backend.inspect) != initial:
                    raise RuntimeError('saved baseline inspection changed on reload')
                if spec is None:
                    baseline = {'inspection': initial, 'measurements': []}
                else:
                    allowed = {s['index'] for s in initial['surfaces']
                               if 0 < s['index'] < initial['image_surface'] and not s.get('is_image')}
                    if any(e['surface'] not in allowed for e in edits):
                        raise ValueError('change must identify a physical non-object, non-image surface')
                    original = [finite(call(backend.get_parameter, e['surface'], e['parameter']),
                                       'original parameter') for e in edits]
                    # Validate the entire expected vector before evaluating or changing anything.
                    for e, found in zip(edits, original):
                        if not math.isclose(found, e['expected_mm'], rel_tol=1e-12, abs_tol=1e-12):
                            raise ValueError(f"stale expected_mm for surface {e['surface']} {e['parameter']}")
                    fixed = _fixed_inspection(initial, initial, edits)

                    def verify(expected):
                        actual = [finite(call(backend.get_parameter, e['surface'], e['parameter']),
                                         'parameter readback') for e in edits]
                        inspection = copy.deepcopy(call(backend.inspect))
                        surfaces = {s['index']: s for s in inspection['surfaces']}
                        for e, wanted, found, before in zip(edits, expected, actual, original):
                            reported = finite(surfaces[e['surface']].get(e['parameter']), 'inspection readback')
                            if (not math.isclose(found, wanted, rel_tol=1e-12, abs_tol=1e-12) or
                                    not math.isclose(reported, wanted, rel_tol=1e-12, abs_tol=1e-12) or
                                    (wanted != before and (found == before or reported == before))):
                                raise RuntimeError('explicit change readback did not reproduce requested vector')
                        if _fixed_inspection(inspection, initial, edits) != fixed:
                            raise RuntimeError('fixed optical model invariants changed')
                        return inspection, actual

                    def evaluate(expected, kind):
                        nonlocal count
                        if count >= maximum:
                            raise RuntimeError('edit evaluation budget exhausted')
                        verify(expected)
                        count += 1
                        rows = copy.deepcopy(call(backend.evaluate, spec))
                        inspection, actual = verify(expected)
                        entry = {'kind': kind, 'parameters_mm': actual, 'inspection': inspection,
                                 'measurements': rows, 'assessment': assess(spec, rows)}
                        if spec.objective is not None:
                            entry['objective_breakdown'] = objective_breakdown(spec, rows)
                            entry['objective_value'] = entry['objective_breakdown']['value']
                        history.append(entry)
                        return entry

                    baseline = evaluate(original, 'baseline')
                    expected = list(original)
                    for index, edit in enumerate(edits):
                        call(backend.set_parameter, edit['surface'], edit['parameter'], edit['value_mm'])
                        expected[index] = edit['value_mm']
                        # Checking the partial vector prevents an early coupled setter being hidden.
                        verify(expected)
                    proposed = evaluate(expected, 'explicit_candidate')
                    call(backend.save, candidate_path)
                    evidence_hashes[candidate_path] = sha256(candidate_path)
                    call(backend.load, candidate_path)
                    reloaded = evaluate(expected, 'saved_reload_verification')
                    if not _reproduces(proposed['measurements'], reloaded['measurements']):
                        raise RuntimeError('saved candidate measurements changed on reload')
                    # Numerical readback tolerance cannot excuse crossing a hard requirement.
                    if proposed['assessment']['passes'] != reloaded['assessment']['passes']:
                        raise RuntimeError('saved candidate requirement status changed on reload')
                    if reloaded['assessment']['passes']:
                        candidate = reloaded
                    else:
                        rejected = reloaded
                write_json(out / 'baseline.json', baseline)
            except BaseException as exc:
                active_error = exc
                raise
            finally:
                # Always recover outside deadline and cancellation limits, including save errors.
                try:
                    backend.load(recovery)
                    restored = initial is None or backend.inspect() == initial
                    if not restored:
                        raise RuntimeError('baseline restoration did not reproduce original inspection')
                except BaseException as exc:
                    cleanup_error = f'{type(exc).__name__}: {exc}'
                    if active_error is None:
                        raise
        check()
        if not model.is_file() or sha256(model) != original_hash:
            raise RuntimeError(f'source changed during {action}; result cannot be accepted')
        for path, expected_hash in evidence_hashes.items():
            if not path.is_file() or sha256(path) != expected_hash:
                raise RuntimeError(f'evidence artifact changed during {action}: {path.name}')
        artifacts = {'baseline_model': str(baseline_path), 'baseline_sha256': evidence_hashes[baseline_path],
                     'source_snapshot': str(snapshot), 'source_snapshot_sha256': original_hash}
        if candidate:
            artifacts.update(candidate_model=str(candidate_path), candidate_sha256=evidence_hashes[candidate_path])
        if rejected:
            rejected_path = out / ('rejected-candidate-model' + candidate_path.suffix)
            candidate_path.replace(rejected_path)
            artifacts.update(rejected_candidate_model=str(rejected_path),
                             rejected_candidate_sha256=evidence_hashes[candidate_path])
        report = {'schema': '1', 'action': action,
                  'status': 'inspected' if spec is None else 'applied' if candidate else 'requirements_not_met',
                  'source': {'path': str(model), 'sha256': original_hash}, 'source_unchanged': True,
                  'baseline': baseline, 'candidate': candidate, 'history': history, 'evaluations': count,
                  'baseline_restored': restored, 'saved_candidate_verified': candidate is not None,
                  'artifacts': artifacts, 'python_version': platform.python_version(),
                  'time_budget_policy': 'cooperative_between_engine_calls; recovery outside budget'}
        if spec is not None:
            report.update(spec=frozen_spec, spec_sha256=evidence_hashes[out / 'spec.json'],
                          changes=config, changes_sha256=evidence_hashes[out / 'changes.json'], rejected_candidate=rejected,
                          parameter_readback_tolerance={'relative': 1e-12, 'absolute_mm': 1e-12,
                                                       'nonzero_delta_requires_actual_change': True})
        write_json(out / 'report.json', report)
        return report
    except BaseException as exc:
        write_json(out / 'failure.json', {'schema': '1', 'action': action, 'status': 'failed',
                   'source': {'path': str(model), 'sha256': original_hash},
                   'error': str(exc), 'error_type': type(exc).__name__, 'cleanup_error': cleanup_error,
                   'baseline_restored': restored,
                   'source_unchanged': model.is_file() and sha256(model) == original_hash,
                   'evaluations': count, 'history': history})
        raise
