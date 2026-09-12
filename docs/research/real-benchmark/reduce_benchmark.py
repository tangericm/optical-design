"""Reduce completed native benchmark evidence; never open or modify optical models.

Run: uv run --with matplotlib python docs/research/real-benchmark/reduce_benchmark.py
Outputs derived-summary.json and profiles.png beside the input report directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/optical-design/scripts'))
from _lib.profiles import combine_spectral_profiles, profile_metrics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path(__file__).parent / 'live/report.json')
    args = parser.parse_args()
    path = args.report.resolve()
    report = json.loads(path.read_text(encoding='utf-8'))
    if report['status'] != 'benchmark_passed' or len(report['records']) != report['expected_records']:
        raise ValueError('reduction requires a complete passing same-method reference benchmark')
    records = {}
    for row in report['records']:
        raw_path = Path(row['raw_file'])
        if digest(raw_path) != row['raw_sha256']:
            raise ValueError('raw evidence hash changed')
        records[row['model_id'], row['case_id']] = json.loads(raw_path.read_text(encoding='utf-8'))
    summary = {'report_sha256': digest(path), 'physical_acceptance': False,
               'interpretation': 'same-method reproduction only; independent physical validation remains open',
               'models': []}
    plot_rows = []
    for model in report['models']:
        model_id = model['id']
        waves = model['inspection']['wavelengths']
        if len(waves) != 18:
            raise ValueError('this project reducer requires exactly 18 active wavelengths')
        weights = np.array([w['weight'] for w in waves], float)
        weights /= weights.sum()
        result = {'id': model_id, 'source_sha256': model['source_sha256'], 'full_spectrum': {},
                  'pop_840nm': {}, 'huygens_y_pupil_change': {}}
        curves = {}
        for axis in ('x', 'y'):
            hcase = 'huygens_x_w0_p512_i128' if axis == 'x' else 'huygens_y_w0_p256_i128'
            h = records[model_id, hcase]['profiles'][axis]
            spectral_rows = []
            for wave, weight in zip(waves, weights):
                row = records[model_id, f"pop_w{wave['index']}_n1024"]['profiles'][axis]
                spectral_rows.append({**row, 'weight': float(weight), 'wavelength_um': wave['wavelength_um'],
                                      'source': f"{model_id}:pop_w{wave['index']}_n1024:{axis}"})
            # Match the historical reducer's displayed grid, while forbidding its zero extrapolation.
            grid = np.linspace(-.6, .6, 6001) if axis == 'x' else np.linspace(-.05, .05, 5001)
            requested_bounds = [float(grid[0]), float(grid[-1])]
            lower = max(row['x_mm'][0] for row in spectral_rows)
            upper = min(row['x_mm'][-1] for row in spectral_rows)
            grid = grid[(grid >= lower) & (grid <= upper)]
            p = combine_spectral_profiles(spectral_rows, shared_grid=grid)
            hm = profile_metrics(h['x_mm'], h['intensity'], profile_kind='cut')
            pm = profile_metrics(p['x_mm'], p['intensity'], profile_kind='cut')
            native_steps = [r['grid']['max_step_mm'] for r in p['input_profiles']]
            result['full_spectrum'][axis] = {
                'huygens': hm, 'pop': pm,
                'pop_native_max_step_mm_range': [min(native_steps), max(native_steps)],
                'pop_interpolation': p['interpolation'],
                'requested_reporting_bounds_mm': requested_bounds,
                'retained_reporting_bounds_mm': [float(grid[0]), float(grid[-1])],
                'common_native_overlap_mm': p['common_overlap_mm'],
                'pop_input_profiles': p['input_profiles'],
                'pop_sampling_acceptance': 'not established by interpolated-grid metric status',
                'd1e2_difference_percent_of_huygens':
                    100 * (pm['d1e2_mm'] / hm['d1e2_mm'] - 1) if hm['d1e2_mm'] and pm['d1e2_mm'] else None}
            curves[axis] = (h, p)
        for sampling in (1024, 2048, 4096):
            raw = records[model_id, f'pop_w9_n{sampling}']
            result['pop_840nm'][str(sampling)] = {
                'grid': raw['grid'], 'power_w': raw['power_w'],
                'launch_window_mm': raw['case']['window_mm'],
                'metrics': {axis: profile_metrics(p['x_mm'], p['intensity'], profile_kind='cut')
                            for axis, p in raw['profiles'].items()}}
        for pupil in (128, 256):
            h = records[model_id, f'huygens_y_w0_p{pupil}_i128']['profiles']['y']
            result['huygens_y_pupil_change'][str(pupil)] = profile_metrics(h['x_mm'], h['intensity'], profile_kind='cut')
        fine = result['pop_840nm']
        result['convergence_limitations'] = {
            'y_pixel_pitch_ratio_4096_over_2048': fine['4096']['grid']['dy_mm'] / fine['2048']['grid']['dy_mm'],
            'x_pixel_pitch_ratio_4096_over_2048': fine['4096']['grid']['dx_mm'] / fine['2048']['grid']['dx_mm'],
            'pop_1024_to_2048_changes_launch_window': True,
            'huygens_x_control_changes_pupil_and_image_sampling_together': True,
            'physical_convergence_established': False}
        summary['models'].append(result)
        plot_rows.append((model_id, curves))
    out = path.parent.parent
    (out / 'derived-summary.json').write_bytes((json.dumps(summary, indent=2, allow_nan=False) + '\n').encode('utf-8'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, len(plot_rows), figsize=(13, 6.7), constrained_layout=True)
    for col, (model_id, curves) in enumerate(plot_rows):
        for row, axis in enumerate(('x', 'y')):
            ax = axes[row, col]
            for p, color, label in zip(curves[axis], ('#176b9b', '#ce622b'), ('Huygens', 'POP spectral sum')):
                x, y = np.asarray(p['x_mm']), np.asarray(p['intensity'])
                ax.plot(x * (1000 if axis == 'y' else 1), y/y.max(), color=color, label=label, linewidth=1.7)
            ax.axhline(np.exp(-2), color='#888888', linewidth=.8, linestyle='--')
            ax.set(xlim=(-.45, .45) if axis == 'x' else (-25, 25), ylim=(0, 1.06),
                   xlabel=f"{axis.upper()} position ({'mm' if axis == 'x' else 'µm'})",
                   ylabel='Normalized intensity' if col == 0 else '')
            ax.grid(alpha=.15)
            if row == 0:
                ax.set_title(model_id)
            if col == 0 and row == 0:
                ax.legend(loc='lower center', fontsize=8)
    fig.suptitle('Fresh native central cuts • 18-wavelength source\nShape comparison; each displayed curve normalized to its own peak', fontsize=13)
    fig.savefig(out / 'profiles.png', dpi=180)
    plt.close(fig)
    print(json.dumps({'derived_summary': str(out / 'derived-summary.json'), 'figure': str(out / 'profiles.png')}))


if __name__ == '__main__':
    main()
