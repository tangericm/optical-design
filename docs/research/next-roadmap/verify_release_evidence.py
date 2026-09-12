"""Verify retained release receipts against current model/artifact bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_report(path):
    report = read(path)
    assert report['source_unchanged'] and report['baseline_restored']
    assert digest(report['source']['path']) == report['source']['sha256']
    assert read(Path(path).parent/'spec.json') == report['spec']
    for key, value in report['artifacts'].items():
        if key.endswith('_model'):
            assert digest(value) == report['artifacts'][key[:-6]+'_sha256']
    return report


def main():
    evidence = {'schema_version': 1, 'optimization': {}, 'compensation': {}, 'mcp': {},
                'physical_acceptance': False, 'checks': []}
    draws = []
    for backend in ('native', 'portable'):
        path = HERE/f'optimize-{backend}/report.json'
        report = verify_report(path)
        assert report['status'] == 'improved' and report['saved_candidate_verified']
        assert report['candidate']['assessment']['passes']
        assert report['evaluations'] <= report['spec']['budget']['max_evaluations']
        before, after = report['baseline']['parameters_mm'], report['candidate']['parameters_mm']
        assert len(before) == len(after) == 2 and all(a != b for a, b in zip(before, after))
        for variable, value in zip(report['variables']['variables'], after):
            assert variable['min_mm'] <= value <= variable['max_mm']
        assert report['candidate']['objective_value'] < report['baseline']['objective_value'] - report['spec']['minimum_gain']
        evidence['optimization'][backend] = {'report_sha256': digest(path), 'evaluations': report['evaluations'],
            'parameters_before_mm': before, 'parameters_after_mm': after,
            'rms_spot_before_um': report['baseline']['objective_value'],
            'rms_spot_after_um': report['candidate']['objective_value']}
        path = HERE/f'compensate-{backend}/report.json'
        report = verify_report(path)
        assert report['status'] == 'completed'
        paired = report['paired_yield']
        assert paired['compensated']['requested'] == paired['compensated']['attempted'] == 8
        assert paired['compensated']['analysis_failures'] == paired['uncompensated']['analysis_failures'] == 0
        all_trials = [report['nominal'], *report['sensitivity'], *report['monte_carlo']]
        assert report['evaluations'] == len(all_trials) + sum(t['compensated']['evaluations'] for t in all_trials)
        for row in all_trials:
            assert row['compensated']['evaluations'] <= report['compensation']['max_evaluations']
            if row['compensated']['status'] == 'pass':
                best = row['compensated']['best']
                assert best['verified'] and best['assessment']['passes']
                assert report['compensation']['min_mm'] <= best['focus_mm'] <= report['compensation']['max_mm']
        draws.append([[p['delta_mm'] for p in row['perturbations']] for row in report['monte_carlo']])
        evidence['compensation'][backend] = {'report_sha256': digest(path), 'paired_yield': paired,
                                            'evaluations': report['evaluations']}
    assert draws[0] == draws[1]
    evidence['checks'].append('identical seeded perturbation draws across engines')
    for path in sorted(HERE.glob('mcp-*-client.json')):
        client = read(path)
        outcome = client['outcome']
        if outcome['state'] != 'completed':
            continue  # Earlier rejected launch diagnostics are intentionally retained.
        report = verify_report(Path(outcome['output'])/'report.json')
        assert outcome['optical_accepted'] and report == outcome['report']
        assert read(outcome['logs']['stdout']) == report
        for name in ('model', 'spec'):
            assert digest(client['request'][name]) == client['request'][name+'_sha256']
        evidence['mcp'][path.stem] = {'client_sha256': digest(path), 'job_id': outcome['job_id'],
                                    'backend': outcome['backend'], 'accepted': True}
    assert {v['backend'] for v in evidence['mcp'].values()} == {'optiland', 'zos'}
    cancellation_path = HERE/'mcp-native-cancel-evidence.json'
    cancellation = read(cancellation_path)
    assert cancellation['native_job_started'] and cancellation['nominal_evidence_before_cancel']
    assert cancellation['live_native_processes'] and not cancellation['owned_native_pids_remaining']
    assert cancellation['unrelated_process_alive'] and cancellation['source_unchanged']
    assert cancellation['results']['state'] == 'cancelled'
    assert cancellation['results']['report'] is None and not cancellation['results']['optical_accepted']
    evidence['native_cancellation'] = {'sha256': digest(cancellation_path), 'verified': True}
    # Capture the final code used for revalidation separately from immutable native receipts.
    evidence['implementation_sha256'] = {str(p.relative_to(ROOT)): digest(p)
        for p in sorted((ROOT/'skills/optical-design/scripts').rglob('*.py'))}
    (HERE/'verified-workflows.json').write_bytes((json.dumps(evidence, indent=2, allow_nan=False)+'\n').encode('utf-8'))
    print('Verified two-engine optimization, compensation and actual MCP optical receipts.')


if __name__ == '__main__':
    main()
