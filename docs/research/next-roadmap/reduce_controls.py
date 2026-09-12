"""Recompute the Stock 840 nm controlled experiment from hashed native profiles."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'skills/optical-design/scripts'))
from _lib.profiles import profile_metrics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_raw(record, case):
    if record['case'] != case:
        raise ValueError('raw case differs from declared manifest identity')
    axes = {case['axis']} if case['method'] == 'huygens' else {'x', 'y'}
    if set(record['profiles']) != axes:
        raise ValueError('raw profile axis coverage differs')
    unit = 'relative' if case['method'] == 'huygens' else 'W/mm^2'
    for profile in record['profiles'].values():
        if profile['profile_kind'] != 'cut' or profile['intensity_unit'] != unit:
            raise ValueError('raw intensity units or cut semantics differ')
        if case['method'] == 'huygens' and profile['native_coordinate_unit'] != 'um':
            raise ValueError('native Huygens coordinate units differ')


def validate_control(label, before, after):
    """Assert a declared input control, without claiming independent output-grid control."""
    b, a = before['case'], after['case']
    changes = {key for key in set(b) | set(a) if key != 'id' and b.get(key) != a.get(key)}
    expected = ({'pupil'} if label == 'huygens_pupil' else
                {'image', 'delta_um'} if label.startswith('huygens_image') else
                {'sampling'} if label.startswith('pop_sampling') else {'resampling'})
    if changes != expected:
        raise ValueError(f'{label}: undeclared or missing case changes: {changes}')
    rb, ra = before['settings_readback'], after['settings_readback']
    changed_readbacks = {key for key in set(rb) | set(ra) if rb.get(key) != ra.get(key)}
    expected_readbacks = {'x_sampling', 'y_sampling', 'resampling'} if expected == {'sampling'} else expected
    if changed_readbacks != expected_readbacks:
        raise ValueError('native readback changes do not isolate the declared control')
    if 'resampling' in changed_readbacks:
        old_rows, new_rows = rb['resampling'], ra['resampling']
        if len(old_rows) != len(new_rows):
            raise ValueError('native resampling row coverage changed')
        for old, new in zip(old_rows, new_rows):
            changed = {key for key in set(old) | set(new) if old.get(key) != new.get(key)}
            allowed = {'x_sampling', 'y_sampling'} if expected == {'sampling'} else {'x_width_mm', 'y_width_mm'}
            if changed and (changed != allowed or (expected == {'resampling'} and old['surface'] != 24)):
                raise ValueError('undeclared native resampling change')
    if expected == {'resampling'}:
        old, new = b['resampling'], a['resampling']
        if len(old) != len(new) or [v['surface'] for v in old] != [v['surface'] for v in new]:
            raise ValueError('resampling schedule identity changed')
        differences = [(x, y) for x, y in zip(old, new) if x != y]
        if len(differences) != 1 or differences[0][0]['surface'] != 24:
            raise ValueError('more than the declared last resampling window changed')
    if label.startswith('huygens_image') and b['image'] * b['delta_um'] != a['image'] * a['delta_um']:
        raise ValueError('Huygens physical observation window changed')
    common = {}
    for axis, bm in before['profiles'].items():
        am = after['profiles'][axis]
        low = max(bm['grid']['bounds_mm'][0], am['grid']['bounds_mm'][0])
        high = min(bm['grid']['bounds_mm'][1], am['grid']['bounds_mm'][1])
        if low >= high:
            raise ValueError('controlled profiles have no common coordinate support')
        if label.startswith('huygens') and not np.allclose(
                bm['grid']['bounds_mm'], am['grid']['bounds_mm'], rtol=0, atol=1e-12):
            raise ValueError('Huygens pair does not preserve common observation bounds')
        for metrics in (bm, am):
            for threshold in metrics['threshold_details'].values():
                if (threshold['status'] != 'ok' or not low <= threshold['left_crossing_mm'] <
                        threshold['right_crossing_mm'] <= high):
                    raise ValueError('threshold crossings lack common valid profile support')
        common[axis] = [low, high]
    return common


def main():
    rows = {}
    provenance = []
    stock_identity = None
    for path in (HERE.parent / 'real-benchmark/live/report.json', HERE / 'live/report.json'):
        report = json.loads(path.read_text(encoding='utf-8'))
        if report['status'] not in ('completed', 'benchmark_passed'):
            raise ValueError('incomplete native report')
        if not report['source_unchanged'] or len(report['records']) != report['expected_records']:
            raise ValueError('source or record coverage failure')
        cli_path = path.parents[1] / ('live-cli.json' if path.parents[1].name == 'real-benchmark' else 'cli.json')
        if json.loads(cli_path.read_text(encoding='utf-8-sig')) != report:
            raise ValueError('native CLI and report receipts disagree')
        manifest_path = path.parents[1] / 'manifest.json'
        if digest(manifest_path) != report['reproducibility']['manifest_sha256']:
            raise ValueError('manifest hash differs from native receipt')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if 'reference' in manifest:
            reference = manifest['reference']
            actual_reference = digest(manifest_path.parent / reference['path'])
            if actual_reference != reference['sha256'] or actual_reference != report['reproducibility']['reference_sha256']:
                raise ValueError('reference hash differs from native receipt')
        cases = {case['id']: case for case in manifest['cases']}
        models = {model['id']: model for model in manifest['models']}
        if len(report['models']) != len(models) or {m['id'] for m in report['models']} != set(models):
            raise ValueError('native model inspection coverage differs from manifest')
        expected = {(model_id, case_id) for model_id in models for case_id in cases}
        identities = [(row['model_id'], row['case_id']) for row in report['records']]
        if len(identities) != len(set(identities)) or set(identities) != expected:
            raise ValueError('native record identity coverage differs from manifest')
        provenance.append({'path': str(path), 'sha256': digest(path),
                           'status': report['status'], 'reference_validated': report['reference_validated']})
        for model in report['models']:
            declared = models[model['id']]
            if (digest(Path(model['source'])) != model['source_sha256'] or
                    digest(Path(model['copied_model'])) != model['source_sha256'] or
                    model['source_sha256'] != declared['sha256'] or not model['restored'] or
                    Path(model['source']).resolve() != Path(declared['path']).resolve()):
                raise ValueError('source or restored copied model differs')
            inspection = model['inspection']
            for dependency in inspection['catalog_files'] + inspection['coating_files']:
                if digest(Path(dependency['path'])) != dependency['sha256']:
                    raise ValueError('native catalog/coating dependency changed')
            if model['id'] == 'Stock':
                wave = [w for w in inspection['wavelengths'] if w['index'] == 9]
                if len(wave) != 1 or wave[0]['wavelength_um'] != .840 or inspection['lens_units'] != 'Millimeters':
                    raise ValueError('native wavelength or lens units do not support 840 nm/mm interpretation')
                identity = (model['source_sha256'], inspection)
                if stock_identity is not None and identity != stock_identity:
                    raise ValueError('Stock model or inspected optical settings differ across runs')
                stock_identity = identity
        for row in report['records']:
            if row['model_id'] != 'Stock':
                continue
            raw = Path(row['raw_file'])
            if digest(raw) != row['raw_sha256'] or not row['restored']:
                raise ValueError('raw data or restoration evidence failed')
            record = json.loads(raw.read_text(encoding='utf-8'))
            validate_raw(record, cases[row['case_id']])
            if record['case']['wavelength'] != 9:
                continue
            if row['case_id'] in rows:
                raise ValueError('duplicate case')
            rows[row['case_id']] = record
    metrics = {name: {'case': r['case'], 'settings_readback': r['settings_readback'],
                      'grid': r.get('grid'), 'power_w': r.get('power_w'),
                      'raw_messages': r.get('messages'),
                      'profiles': {a: profile_metrics(p['x_mm'], p['intensity'], profile_kind='cut')
                                   for a, p in r['profiles'].items()}}
               for name, r in rows.items()}
    controls = [
        ('huygens_pupil', 'huygens_x_w9_p512_i128', 'huygens_x_w9_p1024_i128'),
        ('huygens_image', 'huygens_x_w9_p512_i128', 'huygens_x_w9_p512_i256'),
        ('huygens_image_at_finer_pupil', 'huygens_x_w9_p1024_i128', 'huygens_x_w9_p1024_i256'),
        ('pop_sampling_fixed_window', 'pop_w9_n2048', 'pop_w9_n4096'),
        ('pop_last_window_double', 'pop_w9_n2048', 'pop_w9_n2048_s24_128'),
        ('pop_last_window_half', 'pop_w9_n2048', 'pop_w9_n2048_s24_32'),
        ('pop_sampling_wider_last_window', 'pop_w9_n2048_s24_128', 'pop_w9_n4096_s24_128'),
    ]
    comparisons = []
    for label, before, after in controls:
        b, a = metrics[before], metrics[after]
        common = validate_control(label, b, a)
        change = {'control': label, 'before': before, 'after': after,
                  'common_threshold_support_mm': common, 'axes': {}}
        for axis in b['profiles']:
            bm, am = b['profiles'][axis], a['profiles'][axis]
            change['axes'][axis] = {
                'native_max_pitch_ratio': am['grid']['max_step_mm']/bm['grid']['max_step_mm'],
                'd1e2_change_percent': 100*(am['d1e2_mm']/bm['d1e2_mm']-1) if am['d1e2_mm'] and bm['d1e2_mm'] else None,
                'fwhm_change_percent': 100*(am['fwhm_mm']/bm['fwhm_mm']-1) if am['fwhm_mm'] and bm['fwhm_mm'] else None,
            }
        comparisons.append(change)
    result = {'schema_version': 1, 'wavelength_um': .840, 'physical_acceptance': False,
              'convergence_established': False, 'provenance': provenance,
              'cases': metrics, 'controls': comparisons}
    (HERE/'controlled-summary.json').write_bytes((json.dumps(result, indent=2, allow_nan=False)+'\n').encode('utf-8'))

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    sets = [
        ('Huygens X: pupil / image controls', 'x', ['huygens_x_w9_p512_i128', 'huygens_x_w9_p1024_i128', 'huygens_x_w9_p512_i256', 'huygens_x_w9_p1024_i256']),
        ('POP X: last resampling window', 'x', ['pop_w9_n2048', 'pop_w9_n2048_s24_32', 'pop_w9_n2048_s24_128', 'pop_w9_n4096_s24_128']),
        ('POP Y: last resampling window', 'y', ['pop_w9_n2048', 'pop_w9_n2048_s24_32', 'pop_w9_n2048_s24_128', 'pop_w9_n4096_s24_128']),
    ]
    for ax, (title, axis, names) in zip(axes, sets):
        for name in names:
            p = rows[name]['profiles'][axis]
            x, y = np.asarray(p['x_mm']), np.asarray(p['intensity'])
            label = name.replace('huygens_x_w9_', '').replace('pop_w9_', '').replace('_s24_', ', S24=')
            ax.plot(x*(1000 if axis=='y' else 1), y/y.max(), label=label, linewidth=1.1)
        ax.set(title=title, xlabel=f"{axis.upper()} position ({'um' if axis=='y' else 'mm'})",
               ylabel='Peak-normalized cut', xlim=(-20,20) if axis=='y' else (-.42,.42), ylim=(0,1.05))
        ax.axhline(np.exp(-2), color='gray', linestyle='--', linewidth=.7)
        ax.grid(alpha=.15)
        ax.legend(fontsize=7)
    fig.suptitle('Stock at 840 nm | numerical controls; physical validation remains open', fontsize=13)
    fig.savefig(HERE/'controls.png', dpi=170)
    plt.close(fig)
    print(json.dumps(comparisons, indent=2))


if __name__ == '__main__':
    main()
