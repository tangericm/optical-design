"""Verify retained field/wavelength evidence without an optical engine.

The first run writes verified-evidence.json; subsequent runs verify its exact contents.
Receipt absolute paths map to this checkout without modifying the retained reports.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'skills/optical-design/scripts'))
from _lib.design_contract import DesignSpec, assess, metric_key


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = read(HERE/'predeclared-inputs.json')
    for path, digest in manifest['inputs_sha256'].items():
        require(sha(ROOT/path) == digest, f'Changed predeclared input: {path}')
    portable = read(HERE/'optiland-runs.json')
    native = read(HERE/'corrected-native/zos-runs.json')
    original = Path(portable['control']['request']['model']).parents[4]

    def local(path):
        return ROOT/Path(path).relative_to(original)

    runs = {}
    for engine in ('optiland', 'zos'):
        winners = []
        for label in ('control', 'validation'):
            accepted = label == 'control'
            name = f'{engine}-{label}'
            if engine == 'optiland':
                result = portable[label]['result']
                output = local(result['output'])
                report = read(output/'report.json')
                require(report == result['report'] == read(local(result['logs']['stdout'])), name+' receipt')
                require(result['state'] == 'completed' and result['optical_accepted'] is accepted, name+' MCP')
                returncode = result['returncode']
                for key in ('model', 'spec', 'variables', 'validation_spec'):
                    request = portable[label]['request']
                    require(sha(local(request[key])) == request[key+'_sha256'], name+' input '+key)
            else:
                output = local(native[label]['output'])
                report = read(output/'report.json')
                require(report == read(HERE/f'corrected-native/native-{label}-stdout.json'), name+' receipt')
                returncode = native[label]['returncode']
            require(returncode == (0 if accepted else 1), name+' exit')
            require(report['status'] == ('improved' if accepted else 'validation_failed'), name+' status')
            require(report['source_unchanged'] and report['baseline_restored'], name+' restoration')
            require(sha(local(report['source']['path'])) == report['source']['sha256'], name+' source hash')
            source_asset = 'skills/optical-design/assets/field-validation/'+('native.zmx' if engine == 'zos' else 'portable.json')
            require(report['source']['sha256'] == manifest['inputs_sha256'][source_asset], name+' predeclared model')
            require(report['spec'] == DesignSpec.from_dict(read(ROOT/'skills/optical-design/assets/field-validation/search.json')).data,
                    name+' predeclared search')
            require(report['evaluations'] == len(report['history']) == 81, name+' budget')
            require([r['kind'] for r in report['history'][-2:]] == ['validation_baseline', 'validation_candidate'], name+' order')
            for key in ('spec', 'variables'):
                require(sha(output/f'{key}.json') == report[key+'_sha256'], name+' '+key+' hash')
                require(read(output/f'{key}.json') == report[key], name+' '+key+' data')
            require(report['variables'] == read(ROOT/'skills/optical-design/assets/variables-example.json'), name+' frozen bounds')
            v = report['validation']
            spec = DesignSpec.from_dict(read(ROOT/f'skills/optical-design/assets/field-validation/{label}.json'))
            require(v['spec'] == spec.data == read(output/'validation-spec.json'), name+' validation spec')
            require(sha(output/'validation-spec.json') == v['spec_sha256'], name+' validation hash')
            require(v['evaluations'] == 2 and v['status'] == ('passed' if accepted else 'requirements_not_met'), name+' validation status')
            selected = report['candidate'] if accepted else report['rejected_candidate']
            for role, model_entry in [('baseline', report['baseline']), ('candidate', selected)]:
                entry = v[role]
                require(entry['parameters_mm'] == model_entry['parameters_mm'], name+' '+role+' parameters')
                require(entry['assessment'] == assess(spec, entry['measurements']), name+' '+role+' assessment')
                inv = entry['inspection']['invariants']
                if engine == 'zos':
                    fields = [f['y_deg'] for f in inv['fields']]
                    waves = [w['um'] for w in inv['wavelengths']]
                    primary = [w['primary'] for w in inv['wavelengths']]
                else:
                    fields = [f['y'] for f in inv['fields']['fields']]
                    waves = [w['value'] for w in inv['wavelengths']['wavelengths']]
                    primary = [w['is_primary'] for w in inv['wavelengths']['wavelengths']]
                require(fields == [0, 3, 6] and waves == [.4861327, .55, .6562725]
                        and primary == [False, True, False], name+' '+role+' physical identities')
                rows = {metric_key(r): r for r in entry['measurements']}
                for req in spec.data['requirements']:
                    require(metric_key(req) in rows and rows[metric_key(req)]['value'] is not None,
                            name+' '+role+' missing required measurement')
                if engine == 'zos':
                    for row in rows.values():
                        if row['metric'] == 'rms_spot_um':
                            settings = row['settings']
                            require(settings['spectral_mode'] == 'monochromatic'
                                and settings['field'] == row['field'] and settings['wavelength'] == row['wavelength']
                                and settings['field_xy_deg'] == [0, fields[row['field']-1]]
                                and settings['wavelength_um'] == waves[row['wavelength']-1], name+' native selection')
            require(v['candidate']['assessment']['passes'] is accepted, name+' acceptance')
            require(report['saved_candidate_verified'] is accepted, name+' saved flag')
            artifacts = report['artifacts']
            selected_key = 'candidate' if accepted else 'rejected_candidate'
            for key in ('baseline', selected_key):
                require(sha(local(artifacts[key+'_model'])) == artifacts[key+'_sha256'], name+' '+key+' model hash')
            suffix = local(report['source']['path']).suffix
            require(sha(output/('source_snapshot'+suffix)) == artifacts['source_snapshot_sha256']
                    == report['source']['sha256'], name+' source snapshot')
            if not accepted:
                require(report['candidate'] is None and 'candidate_model' not in artifacts
                        and not (output/('candidate-model'+suffix)).exists(), name+' quarantine')
                scoped = [r for r in v['candidate']['measurements'] if 'field' in r]
                expected = {(f, w, m, a) for f in (1, 2, 3) for w in (1, 2, 3)
                            for m, a in [('rms_spot_um', None), ('mtf', 'tangential'), ('mtf', 'sagittal')]}
                require({(r['field'], r['wavelength'], r['metric'], r.get('axis')) for r in scoped} == expected,
                        name+' incomplete grid')
            winners.append(selected['parameters_mm'])
            runs[name] = dict(status=report['status'], optical_accepted=accepted, evaluations=81,
                validation_evaluations=2, parameters_mm=selected['parameters_mm'],
                failed_requirements=[r['id'] for r in v['candidate']['assessment']['requirements'] if r['status'] != 'pass'],
                measurements=[{k: val for k, val in r.items() if k not in ('analysis', 'settings')}
                              for r in v['candidate']['measurements']], report_sha256=sha(output/'report.json'))
        require(winners[0] == winners[1], engine+' control and expanded search winners differ')
    files = sorted((ROOT/'skills/optical-design/scripts').rglob('*.py'))
    payload = dict(release='0.1.0-dev.5', date='2026-09-13', runs=runs,
        implementation_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in files})
    target = HERE/'verified-evidence.json'
    if target.exists():
        require(read(target) == payload, 'Recorded results or implementation hashes changed')
    else:
        target.write_bytes((json.dumps(payload, indent=2, allow_nan=False)+'\n').encode('utf-8'))
    print('Verified four runs, complete 3x3 grids, physical identities, fixed winners, assessments, hashes and quarantine.')


if __name__ == '__main__':
    main()
