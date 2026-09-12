"""Offline final verification of native receipts using the final comparison code.

This is a receipt/array recheck, not another optical-engine execution. It writes only
final-verification.json beside this script. Both native jobs must have finished first.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'skills/optical-design/scripts'))
from _lib.profile_benchmark import _compare_profiles, _load_manifest


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(name, manifest_name):
    report_path = HERE / name / 'report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    cli = json.loads((HERE / f'{name}-cli.json').read_text(encoding='utf-8-sig'))
    if cli != report or report['status'] != 'benchmark_passed' or not report['source_unchanged']:
        raise ValueError('native shutdown receipt/CLI agreement failed')
    path, manifest, models, references, reference_path, *_ = _load_manifest(HERE / manifest_name)
    if digest(path) != report['reproducibility']['manifest_sha256']:
        raise ValueError('manifest does not match native receipt')
    if digest(reference_path) != report['reproducibility']['reference_sha256']:
        raise ValueError('reference does not match native receipt')
    cases = {case['id']: case for case in manifest['cases']}
    expected = {(model['id'], case_id) for model, _ in models for case_id in cases}
    identities = [(row['model_id'], row['case_id']) for row in report['records']]
    if len(set(identities)) != len(identities) or set(identities) != expected:
        raise ValueError('incomplete or repeated native case identity')
    if {m['id'] for m in report['models']} != {m['id'] for m, _ in models}:
        raise ValueError('native model inspection coverage differs')
    declared_models = {model['id']: (model, source) for model, source in models}
    for model in report['models']:
        declared, source = declared_models[model['id']]
        if (Path(model['source']).resolve() != source or model['source_sha256'] != declared['sha256'].lower() or
                not model['restored'] or digest(Path(model['copied_model'])) != model['source_sha256']):
            raise ValueError('copied native model not preserved')
        for dependency in model['inspection']['catalog_files'] + model['inspection']['coating_files']:
            if digest(Path(dependency['path'])) != dependency['sha256']:
                raise ValueError('native dependency changed after calculation')
    max_coordinate_error, max_power_error, profiles = 0.0, 0.0, 0
    intensity_errors_by_unit = {'relative': 0.0, 'W/mm^2': 0.0}
    for record in report['records']:
        raw_path = Path(record['raw_file'])
        if digest(raw_path) != record['raw_sha256'] or not record['restored']:
            raise ValueError('raw evidence changed after calculation')
        raw = json.loads(raw_path.read_text(encoding='utf-8'))
        identity = record['model_id'], record['case_id']
        case = cases[identity[1]]
        axes = {case['axis']} if case['method'] == 'huygens' else {'x', 'y'}
        if raw['case'] != case or set(raw['profiles']) != axes:
            raise ValueError('native analysis identity changed')
        for axis, profile in raw['profiles'].items():
            unit = 'relative' if case['method'] == 'huygens' else 'W/mm^2'
            if profile['profile_kind'] != 'cut' or profile['intensity_unit'] != unit:
                raise ValueError('native profile semantics changed')
            coordinates = references[identity]['profiles'][axis]['x_mm']
            max_coordinate_error = max(max_coordinate_error, *(abs(a-b) for a, b in zip(profile['x_mm'], coordinates)))
        comparison = _compare_profiles(raw, references[identity], manifest['comparison'])
        if not comparison['passes']:
            raise ValueError(f'final comparison code rejects {identity}')
        for axis, compared in comparison['axes'].items():
            unit = raw['profiles'][axis]['intensity_unit']
            intensity_errors_by_unit[unit] = max(intensity_errors_by_unit[unit], compared['max_abs_intensity_error'])
        if comparison['power']:
            max_power_error = max(max_power_error, abs(comparison['power']['actual_w'] - comparison['power']['reference_w']))
        profiles += len(axes)
    return {'status': 'verified', 'native_report_sha256': digest(report_path), 'cases': len(identities),
            'profiles': profiles,
            'max_abs_intensity_error_by_unit': intensity_errors_by_unit,
            'max_abs_coordinate_error_mm': max_coordinate_error, 'max_abs_power_error_w': max_power_error,
            'source_copies_dependencies_and_raw_hashes_verified': True}


def main():
    result = {'verified_at_utc': datetime.now(UTC).isoformat(),
              'verification_kind': 'offline receipt and array recheck; no additional optical-engine execution',
              'full_native_job': verify('live', 'manifest.json'),
              'final_cli_native_smoke': verify('smoke', 'smoke-manifest.json'),
              'validator_code_sha256': {name: digest(ROOT / 'skills/optical-design/scripts' / name)
                                        for name in ('benchmark.py', '_lib/native_profiles.py', '_lib/native_worker.py',
                                                     '_lib/profile_benchmark.py', '_lib/profiles.py')}}
    (HERE / 'final-verification.json').write_bytes((json.dumps(result, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
