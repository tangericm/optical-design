"""Predeclared multi-condition composite merit exercise through both actual CLIs."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    HERE = HERE / sys.argv[1]
    HERE.mkdir(exist_ok=False)
ASSETS = ROOT/'skills/optical-design/assets'
CLI = ROOT/'skills/optical-design/scripts/design.py'


def main():
    spec = {'schema': '1', 'name': 'Full-release nine-condition weighted spot merit',
        'fields': [1, 2, 3], 'wavelengths': [1, 2, 3], 'frequencies_cyc_per_mm': [],
        'requirements': [{'id': 'focal-length', 'metric': 'efl_mm', 'unit': 'mm', 'min': 48, 'max': 52},
                         {'id': 'track', 'metric': 'total_track_mm', 'unit': 'mm', 'max': 65}],
        'objective': {'direction': 'minimize', 'aggregation': 'weighted_rms', 'terms': []},
        'budget': {'max_evaluations': 41, 'timeout_s': 600},
        'analysis': {'sampling': 64, 'use_polarization': False}, 'minimum_gain': .001}
    for field in spec['fields']:
        for wave in spec['wavelengths']:
            metric = {'metric': 'rms_spot_um', 'field': field, 'wavelength': wave, 'unit': 'um'}
            spec['requirements'].append(dict(metric, id=f'spot-{field}-{wave}', max=120))
            spec['objective']['terms'].append(dict(metric, target=0, scale=30, weight=1))
    spec_path = HERE/'composite-spec.json'
    spec_path.write_bytes((json.dumps(spec, indent=2)+'\n').encode())
    results = {}
    for engine, model in [('optiland', ASSETS/'field-validation/portable.json'),
                          ('zos', ASSETS/'field-validation/native.zmx')]:
        out = HERE/f'composite-{engine}'
        with (HERE/f'composite-{engine}.log').open('wb') as log:
            result = subprocess.run([sys.executable, str(CLI), 'optimize', '--backend', engine,
                '--model', str(model), '--spec', str(spec_path), '--variables', str(ASSETS/'variables-example.json'),
                '--out', str(out), '--json'], stdout=log, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, (engine, result.returncode)
        report = json.loads((out/'report.json').read_text())
        assert report['status'] == 'improved' and report['saved_candidate_verified']
        assert report['source_unchanged'] and report['baseline_restored']
        assert len(report['candidate']['objective_breakdown']['terms']) == 9
        assert report['candidate']['objective_value'] < report['baseline']['objective_value']
        results[engine] = {key: report[key] for key in ['status', 'evaluations', 'artifacts']}
        results[engine].update(baseline_merit=report['baseline']['objective_value'],
                              candidate_merit=report['candidate']['objective_value'],
                              parameters_mm=report['candidate']['parameters_mm'])
        print(engine, results[engine], flush=True)
    (HERE/'composite-results.json').write_bytes((json.dumps(results, indent=2)+'\n').encode())


if __name__ == '__main__':
    main()
