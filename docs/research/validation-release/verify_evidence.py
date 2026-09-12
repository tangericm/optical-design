"""Verify retained dev.4 evidence without starting either optical engine.

Run from the repository: uv run python docs/research/validation-release/verify_evidence.py
Absolute receipt paths are mapped to this checkout; original receipts are never rewritten.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    first = read(HERE/'native-pass/report.json')
    original_root = Path(first['source']['path']).parents[3]

    def local(path):
        return ROOT/Path(path).relative_to(original_root)

    mcp = read(HERE/'mcp-validation.json')
    summary = {}
    vectors = {}
    for backend in ('native', 'portable'):
        for label in ('pass', 'reject'):
            accepted = label == 'pass'
            name = f'{backend}-{label}'
            if backend == 'native':
                out = HERE/name
                report = read(out/'report.json')
                check(read(HERE/f'{name}-cli.json') == report, f'{name}: CLI/report mismatch')
            else:
                result = mcp[label]['result']
                out = local(result['output'])
                report = read(out/'report.json')
                check(result['report'] == report, f'{name}: MCP/report mismatch')
                check(read(local(result['logs']['stdout'])) == report, f'{name}: stdout mismatch')
                check(result['state'] == 'completed' and result['optical_accepted'] is accepted
                      and result['returncode'] == (0 if accepted else 1), f'{name}: MCP outcome')
                for key in ('model', 'spec', 'variables', 'validation_spec'):
                    request = mcp[label]['request']
                    check(sha(local(request[key])) == request[key+'_sha256'], f'{name}: input {key}')
            check(report['status'] == ('improved' if accepted else 'validation_failed'), name)
            check(report['source_unchanged'] and report['baseline_restored'], f'{name}: restoration')
            check(sha(local(report['source']['path'])) == report['source']['sha256'], f'{name}: source')
            check(report['evaluations'] == 81 and len(report['history']) == 81, f'{name}: budget')
            check([h['kind'] for h in report['history'][-4:]] == [
                'candidate_verification', 'saved_reload_verification',
                'validation_baseline', 'validation_candidate'], f'{name}: final evaluation order')
            for key in ('spec', 'variables'):
                check(sha(out/f'{key}.json') == report[key+'_sha256'], f'{name}: {key} hash')
                check(read(out/f'{key}.json') == report[key], f'{name}: {key} data')
            validation = report['validation']
            check(validation['status'] == ('passed' if accepted else 'requirements_not_met'), name)
            check(validation['evaluations'] == 2, f'{name}: validation budget')
            check(sha(out/'validation-spec.json') == validation['spec_sha256'], f'{name}: validation hash')
            check(read(out/'validation-spec.json') == validation['spec'], f'{name}: frozen spec')
            check(report['spec']['analysis']['sampling'] == 64
                  and validation['spec']['analysis']['sampling'] == 256, f'{name}: sampling')
            check(validation['candidate']['assessment']['passes'] is accepted, f'{name}: assessment')
            selected = report['candidate'] if accepted else report['rejected_candidate']
            check(validation['candidate']['parameters_mm'] == selected['parameters_mm'], f'{name}: candidate vector')
            check(validation['baseline']['parameters_mm'] == report['baseline']['parameters_mm'], f'{name}: baseline vector')
            check(report['saved_candidate_verified'] is accepted, f'{name}: acceptance flag')
            artifacts = report['artifacts']
            key = 'candidate' if accepted else 'rejected_candidate'
            check(sha(local(artifacts[key+'_model'])) == artifacts[key+'_sha256'], f'{name}: model hash')
            check(sha(local(artifacts['baseline_model'])) == artifacts['baseline_sha256'], f'{name}: baseline hash')
            source_snapshot = out/('source_snapshot'+local(report['source']['path']).suffix)
            check(sha(source_snapshot) == artifacts['source_snapshot_sha256']
                  == report['source']['sha256'], f'{name}: snapshot hash')
            if not accepted:
                check(report['candidate'] is None and 'candidate_model' not in artifacts
                      and not (out/('candidate-model'+source_snapshot.suffix)).exists(), f'{name}: quarantine')
            vectors[name] = validation['candidate']['parameters_mm']
            measures = validation['candidate']['measurements']
            summary[name] = {
                'status': report['status'], 'optical_accepted': accepted, 'evaluations': 81,
                'validation_evaluations': 2, 'parameters_mm': vectors[name],
                'rms_spot_um': next(m['value'] for m in measures if m['metric'] == 'rms_spot_um'),
                'tangential_mtf_20': next(m['value'] for m in measures
                                          if m['metric'] == 'mtf' and m['axis'] == 'tangential'),
                'report_sha256': sha(out/'report.json'),
            }
        check(vectors[backend+'-pass'] == vectors[backend+'-reject'], f'{backend}: winner changed')
    record = HERE/'verified-evidence.json'
    if record.exists():
        saved = read(record)
        check(saved['runs'] == summary, 'Recorded evidence summary changed')
        for relative, digest in saved['implementation_sha256'].items():
            check(sha(ROOT/relative) == digest, f'Implementation changed: {relative}')
    else:
        implementation = [p for p in (ROOT/'skills/optical-design/scripts').rglob('*.py')
                          if '__pycache__' not in p.parts]
        implementation.extend([ROOT/'skills/optical-design/assets/validation-spec.json',
                               ROOT/'skills/optical-design/SKILL.md'])
        payload = {'release': '0.1.0-dev.4', 'date': '2026-09-12', 'runs': summary,
                   'implementation_sha256': {p.relative_to(ROOT).as_posix(): sha(p)
                                             for p in sorted(implementation)}}
        record.write_bytes((json.dumps(payload, indent=2, allow_nan=False)+'\n').encode('utf-8'))
    print('Verified four live cases, source/artifact hashes, frozen specifications, final evaluation order, and implementation hashes.')


if __name__ == '__main__':
    main()
