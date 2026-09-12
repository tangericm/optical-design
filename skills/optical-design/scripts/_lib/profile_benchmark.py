"""Explicit, copied-model diffraction-profile benchmarking; no design optimization."""
from __future__ import annotations

import copy
import hashlib
import json
import platform
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from _lib.design_contract import finite
from _lib.design_jobs import sha256, write_json
from _lib.profiles import profile_metrics


def validate_case(raw):
    if not isinstance(raw, dict) or raw.get('method') not in {'huygens', 'pop'}:
        raise ValueError('profile method must be huygens or pop')
    case = copy.deepcopy(raw)
    common = {'id', 'method', 'field', 'wavelength', 'polarization'}
    required = common | ({'axis', 'pupil', 'image', 'delta_um', 'reference'} if case['method'] == 'huygens' else
                         {'sampling', 'window_mm', 'waist_x_mm', 'waist_y_mm', 'start_surface', 'end_surface',
                          'power_w', 'separate_xy', 'resampling'})
    if set(case) != required:
        raise ValueError(f'case requires exactly these keys: {sorted(required)}')
    if not isinstance(case['id'], str) or not case['id'] or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in case['id']):
        raise ValueError('case id must be a nonempty filename-safe identifier')
    for key in ('field', 'wavelength'):
        if type(case[key]) is not int or case[key] < (0 if key == 'wavelength' and case['method'] == 'huygens' else 1):
            raise ValueError(f'invalid {key} index')
    if type(case['polarization']) is not bool:
        raise ValueError('polarization must be explicit boolean')
    if case['method'] == 'huygens':
        if case['axis'] not in {'x', 'y'} or case['reference'] not in {'Planar', 'Spherical'}:
            raise ValueError('invalid Huygens axis/reference')
        for key in ('pupil', 'image'):
            if type(case[key]) is not int or case[key] not in {32, 64, 128, 256, 512, 1024}:
                raise ValueError(f'invalid {key} sampling')
        if finite(case['delta_um'], 'image delta') <= 0:
            raise ValueError('image delta must be positive um')
    else:
        if type(case['sampling']) is not int or case['sampling'] not in {128, 256, 512, 1024, 2048, 4096}:
            raise ValueError('invalid POP sampling')
        for key in ('window_mm', 'waist_x_mm', 'waist_y_mm', 'power_w'):
            if finite(case[key], key) <= 0:
                raise ValueError(f'{key} must be positive')
        for key in ('start_surface', 'end_surface'):
            if type(case[key]) is not int or case[key] < 1:
                raise ValueError('invalid POP start/end surface')
        if case['start_surface'] >= case['end_surface'] or type(case['separate_xy']) is not bool:
            raise ValueError('invalid POP range/separate_xy')
        resampling = case['resampling']
        if not isinstance(resampling, list) or len(resampling) > 32:
            raise ValueError('resampling must be a list of at most 32 declared planes')
        seen = set()
        for row in resampling:
            if not isinstance(row, dict) or set(row) != {'surface', 'width_mm'}:
                raise ValueError('resampling needs surface and width_mm')
            if (type(row['surface']) is not int or not case['start_surface'] <= row['surface'] < case['end_surface'] or
                    row['surface'] in seen or finite(row['width_mm'], 'resampling width') <= 0):
                raise ValueError('invalid/duplicate resampling plane')
            seen.add(row['surface'])
    return case


def _identifier(value):
    if not isinstance(value, str) or re.fullmatch(r'[A-Za-z0-9_-]+', value) is None:
        raise ValueError('ids must be nonempty filename-safe identifiers')
    return value


def _hashed_path(entry, base):
    if not isinstance(entry.get('path'), str) or not entry['path']:
        raise ValueError('file path must be an explicit nonempty string')
    digest = entry.get('sha256')
    if not isinstance(digest, str) or re.fullmatch(r'[a-fA-F0-9]{64}', digest) is None:
        raise ValueError('file sha256 must contain exactly 64 hexadecimal characters')
    path = (base / entry['path']).resolve(strict=True)
    if not path.is_file() or sha256(path) != digest.lower():
        raise ValueError(f'file content does not match declared SHA-256: {entry["path"]}')
    return path


def _axes(case):
    return {case['axis']} if case['method'] == 'huygens' else {'x', 'y'}


def _checked_profile(profile, *, reference=False):
    if not isinstance(profile, dict) or not {'x_mm', 'intensity'} <= set(profile):
        raise ValueError('profiles require x_mm and intensity arrays')
    if reference and set(profile) != {'x_mm', 'intensity'}:
        raise ValueError('reference profiles require exactly x_mm and intensity')
    diagnostics = profile_metrics(profile['x_mm'], profile['intensity'],
                                  profile_kind=profile.get('profile_kind', 'cut'))
    return np.asarray(profile['x_mm'], float), np.asarray(profile['intensity'], float), diagnostics


def _load_manifest(manifest_path):
    path = Path(manifest_path).resolve(strict=True)
    manifest_bytes = path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = json.loads(manifest_bytes.decode('utf-8-sig'))
    required = {'schema_version', 'name', 'models', 'cases'}
    if (not isinstance(manifest, dict) or not required <= set(manifest) or
            set(manifest) - required - {'reference', 'comparison'} or
            type(manifest['schema_version']) is not int or manifest['schema_version'] != 1):
        raise ValueError('manifest requires schema_version 1, name, models and cases; only reference/comparison are optional')
    if not isinstance(manifest['name'], str) or not manifest['name'].strip():
        raise ValueError('manifest name must be a nonempty string')
    if not isinstance(manifest['models'], list) or not manifest['models']:
        raise ValueError('models must be a nonempty list')
    if not isinstance(manifest['cases'], list) or not manifest['cases']:
        raise ValueError('cases must be a nonempty list')
    models, model_ids, case_ids = [], set(), set()
    folded_model_ids, folded_case_ids = set(), set()
    for model in manifest['models']:
        if not isinstance(model, dict) or set(model) != {'id', 'path', 'sha256'}:
            raise ValueError('models require exactly id, path and sha256')
        identity = _identifier(model['id'])
        if identity.casefold() in folded_model_ids:
            raise ValueError('duplicate model id')
        model_ids.add(identity)
        folded_model_ids.add(identity.casefold())
        models.append((model, _hashed_path(model, path.parent)))
    manifest['cases'] = [validate_case(c) for c in manifest['cases']]
    for case in manifest['cases']:
        if case['id'].casefold() in folded_case_ids:
            raise ValueError('duplicate case id')
        case_ids.add(case['id'])
        folded_case_ids.add(case['id'].casefold())
    if ('reference' in manifest) != ('comparison' in manifest):
        raise ValueError('reference and comparison must be supplied together')
    references, reference_path = {}, None
    if 'reference' in manifest:
        source = manifest['reference']
        if not isinstance(source, dict) or set(source) != {'path', 'sha256'}:
            raise ValueError('reference requires exactly path and sha256')
        comparison = manifest['comparison']
        if (not isinstance(comparison, dict) or not {'rtol', 'atol'} <= set(comparison) or
                set(comparison) - {'rtol', 'atol', 'coordinate_atol_mm'}):
            raise ValueError('comparison requires rtol/atol; optional coordinate_atol_mm')
        comparison.setdefault('coordinate_atol_mm', 1e-10)
        for key, value in comparison.items():
            if finite(value, key) < 0:
                raise ValueError('comparison tolerances must be nonnegative')
        reference_path = _hashed_path(source, path.parent)
        reference_bytes = reference_path.read_bytes()
        if hashlib.sha256(reference_bytes).hexdigest() != source['sha256'].lower():
            raise ValueError('reference changed between hash verification and reading')
        raw = json.loads(reference_bytes.decode('utf-8-sig'))
        if not isinstance(raw, dict) or set(raw) != {'records'} or not isinstance(raw['records'], list):
            raise ValueError('reference requires exactly a records list')
        cases = {case['id']: case for case in manifest['cases']}
        for record in raw['records']:
            if (not isinstance(record, dict) or not {'model_id', 'case_id', 'profiles'} <= set(record) or
                    set(record) - {'model_id', 'case_id', 'profiles', 'power_w'}):
                raise ValueError('reference records require model_id, case_id, profiles; optional power_w')
            key = (_identifier(record['model_id']), _identifier(record['case_id']))
            if key in references or key[0] not in model_ids or key[1] not in cases:
                raise ValueError('duplicate or unknown reference model/case identity')
            if not isinstance(record['profiles'], dict) or set(record['profiles']) != _axes(cases[key[1]]):
                raise ValueError('reference axes must exactly match the declared case')
            for profile in record['profiles'].values():
                _checked_profile(profile, reference=True)
            if 'power_w' in record and finite(record['power_w'], 'reference power') <= 0:
                raise ValueError('reference power must be positive')
            references[key] = record
        if set(references) != {(m, c) for m in model_ids for c in case_ids}:
            raise ValueError('reference must cover every model/case exactly once')
    return path, manifest, models, references, reference_path, manifest_hash


def _still_matches(path, digest):
    try:
        return path.is_file() and sha256(path) == digest
    except OSError:
        return False


def _compare_profiles(actual, reference, settings):
    axes = {}
    for axis, profile in actual['profiles'].items():
        x, intensity, _ = _checked_profile(profile)
        rx, ri, _ = _checked_profile(reference['profiles'][axis], reference=True)
        same_shape = x.shape == rx.shape
        grid_matches = same_shape and np.allclose(x, rx, rtol=0, atol=settings['coordinate_atol_mm'])
        intensity_matches = same_shape and np.allclose(intensity, ri, rtol=settings['rtol'], atol=settings['atol'])
        axes[axis] = {'passes': bool(grid_matches and intensity_matches), 'shape_matches': same_shape,
                      'grid_matches': bool(grid_matches), 'intensity_matches': bool(intensity_matches),
                      'max_abs_intensity_error': float(np.max(abs(intensity-ri))) if same_shape else None,
                      'interpolation': False, 'normalization': 'none'}
    power = None
    if 'power_w' in reference:
        value = actual.get('power_w')
        passed = value is not None and np.isclose(value, reference['power_w'], rtol=settings['rtol'], atol=settings['atol'])
        power = {'passes': bool(passed), 'actual_w': value, 'reference_w': reference['power_w']}
    return {'passes': all(a['passes'] for a in axes.values()) and (power is None or power['passes']),
            'axes': axes, 'power': power, 'settings': settings}


def run_benchmark(manifest_path, out, factory=None):
    """Benchmark a complete model/case Cartesian product on verified disposable copies.

    Coordinate comparisons never interpolate. Huygens relative values and POP absolute
    irradiance are compared as returned; diagnostic sampling warnings cannot establish
    or negate numerical reproduction. No reference means completed but unvalidated.
    """
    started_at = datetime.now(UTC).isoformat()
    path, manifest, sources, references, reference_path, manifest_hash = _load_manifest(manifest_path)
    if factory is None:
        from _lib.native_profiles import NativeProfileBackend
        factory = NativeProfileBackend
    out = Path(out).resolve()
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('output must be new or empty; benchmark evidence is immutable')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'models').mkdir()
    (out / 'raw').mkdir()
    records, model_records = [], []
    source_checks, cleanup_error = {}, None
    reference_hash = manifest['reference']['sha256'].lower() if reference_path else None
    try:
        write_json(out / 'manifest.json', manifest)
        for model, source in sources:
            copied = out / 'models' / (model['id'] + source.suffix)
            shutil.copy2(source, copied)
            copied_hash = sha256(copied)
            if copied_hash != model['sha256'].lower():
                raise RuntimeError('copied model differs from declared source hash')
            evidence = {'id': model['id'], 'source': str(source), 'source_sha256': model['sha256'].lower(),
                        'copied_model': str(copied), 'copied_sha256': copied_hash, 'restored': False}
            model_records.append(evidence)
            with factory(copied) as backend:
                initial = copy.deepcopy(backend.inspect())
                evidence['inspection'] = initial
                active_error = None
                try:
                    for case in manifest['cases']:
                        backend.restore()
                        if backend.inspect() != initial:
                            raise RuntimeError('baseline restoration failed before case')
                        raw = backend.evaluate(copy.deepcopy(case))
                        raw_name = f'{len(model["id"])}_{model["id"]}--{case["id"]}.json'
                        write_json(out / 'raw' / raw_name, raw)
                        raw_hash = sha256(out / 'raw' / raw_name)
                        if not isinstance(raw, dict) or raw.get('case') != case:
                            raise ValueError('native result case identity differs from requested settings')
                        if not isinstance(raw.get('profiles'), dict) or set(raw['profiles']) != _axes(case):
                            raise ValueError('native profile axes do not exactly match the case')
                        diagnostics = {}
                        for axis, profile in raw['profiles'].items():
                            expected_unit = 'relative' if case['method'] == 'huygens' else 'W/mm^2'
                            if profile.get('profile_kind') != 'cut' or profile.get('intensity_unit') != expected_unit:
                                raise ValueError('native profile kind/units differ from the declared analysis contract')
                            diagnostics[axis] = _checked_profile(profile)[2]
                        if 'power_w' in raw and finite(raw['power_w'], 'native power') <= 0:
                            raise ValueError('native power must be positive')
                        reference = references.get((model['id'], case['id']))
                        comparison = _compare_profiles(raw, reference, manifest['comparison']) if reference else None
                        backend.restore()
                        if backend.inspect() != initial or sha256(copied) != copied_hash:
                            raise RuntimeError('baseline restoration or copied-file preservation failed after case')
                        records.append({'model_id': model['id'], 'case_id': case['id'], 'raw_file': str(out / 'raw' / raw_name),
                                        'raw_sha256': raw_hash, 'restored': True,
                                        'diagnostics': diagnostics, 'comparison': comparison})
                        write_json(out / 'records.json', records)
                except BaseException as exc:
                    active_error = exc
                    raise
                finally:
                    try:
                        backend.restore()
                        evidence['restored'] = backend.inspect() == initial and sha256(copied) == copied_hash
                        if not evidence['restored']:
                            raise RuntimeError('baseline restoration failed during cleanup')
                    except BaseException as exc:
                        cleanup_error = f'{type(exc).__name__}: {exc}'
                        if active_error is None:
                            raise
        if len(records) != len(sources) * len(manifest['cases']):
            raise RuntimeError('partial benchmark cannot produce a completion receipt')
        if any(not _still_matches(Path(record['raw_file']), record['raw_sha256']) for record in records):
            raise RuntimeError('raw artifact preservation failed before final receipt')
    except BaseException as exc:
        write_json(out / 'failure.json', {'status': 'failed', 'error': str(exc), 'error_type': type(exc).__name__,
                                        'cleanup_error': cleanup_error, 'completed_records': len(records),
                                        'models': model_records})
        raise
    finally:
        source_checks = {model['id']: _still_matches(source, model['sha256'].lower())
                         for model, source in sources}
        unchanged = all(source_checks.values()) and _still_matches(path, manifest_hash)
        if reference_path:
            unchanged = unchanged and _still_matches(reference_path, reference_hash)
        failure_path = out / 'failure.json'
        if failure_path.exists() or not unchanged:
            failure = json.loads(failure_path.read_text(encoding='utf-8')) if failure_path.exists() else {'status': 'failed'}
            failure.update(source_unchanged=unchanged, source_checks=source_checks, completed_records=len(records),
                           started_at_utc=started_at, finished_at_utc=datetime.now(UTC).isoformat())
            if not unchanged:
                failure['preservation_error'] = 'source, manifest or reference changed during benchmark'
            write_json(failure_path, failure)
        if not unchanged:
            raise RuntimeError('benchmark input preservation failed')
    passed = all(r['comparison']['passes'] for r in records) if references else None
    report = {'schema_version': 1, 'name': manifest['name'], 'status': ('benchmark_passed' if passed else 'benchmark_failed') if references else 'completed',
              'reference_validated': passed is True, 'reference_supplied': bool(references),
              'reference_integrity_verified': bool(references),
              'source_unchanged': True, 'models': model_records, 'records': records,
              'started_at_utc': started_at, 'finished_at_utc': datetime.now(UTC).isoformat(),
              'expected_records': len(sources) * len(manifest['cases']),
              'reproducibility': {'manifest_sha256': manifest_hash, 'reference_sha256': reference_hash,
                                  'python_version': platform.python_version(), 'comparison': manifest.get('comparison'),
                                  'metric_diagnostics_affect_reproduction': False,
                                  'no_reference_policy': 'completed means unvalidated; no benchmark acceptance claimed'}}
    write_json(out / 'report.json', report)
    return report
