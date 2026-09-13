"""Deterministic, offline review packages from local optical job receipts.

Receipt consistency is checked without opening an optical engine or the source path.
Artifact hashes bind bytes, not a new verification of those bytes' optical behavior.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
from pathlib import Path, PureWindowsPath

from _lib.design_contract import (
    UNITS,
    DesignSpec,
    assess,
    finite,
    metric_key,
    objective_breakdown,
    objective_value,
)

STATUSES = {
    'audit': {'requirements_met', 'requirements_not_met'},
    'refocus': {'improved', 'no_acceptable_improvement'},
    'optimize': {'improved', 'no_acceptable_improvement', 'validation_failed'},
    'tolerance': {'completed'}, 'sensitivity': {'completed'},
    'inspect': {'completed', 'inspected'}, 'edit': {'applied', 'requirements_not_met'},
}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _decode(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    value = json.loads(data.decode('utf-8-sig'), object_pairs_hook=unique)
    json.dumps(value, allow_nan=False)
    return value


def _confined(raw, root):
    if not isinstance(raw, str) or not raw or '\x00' in raw:
        raise ValueError('artifact path must be nonempty text')
    win = PureWindowsPath(raw)
    if '..' in win.parts or '..' in Path(raw).parts or raw.startswith(('\\\\', '//')):
        raise ValueError('artifact path traversal or network path rejected')
    # Reject URI schemes and Windows alternate data streams, including on POSIX.
    if ':' in raw[len(win.drive):] or (win.drive and not Path(raw).is_absolute()):
        raise ValueError('invalid artifact path')
    path = Path(raw)
    path = (path if path.is_absolute() else root / path).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('artifact path escapes report directory')
    return path


def _digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _snapshot(report, key, filename, root, verified, *, required=False):
    if key not in report:
        if required:
            raise ValueError(f'missing {key} snapshot data')
        return
    path = _confined(filename, root)
    data = path.read_bytes()
    if _decode(data) != report[key]:
        raise ValueError(f'{key} snapshot differs from receipt')
    claimed = report.get(key + '_sha256')
    if claimed is not None and claimed != _sha(data):
        raise ValueError(f'{key} snapshot hash differs from receipt')
    verified[filename] = _sha(data)


def _measurement_entries(value, spec, label='report', validation_spec=None):
    """Reassess every nested evaluation, including histories and tolerance trials."""
    if isinstance(value, dict):
        if label.startswith('report.history[') and value.get('kind') in {'validation_baseline', 'validation_candidate'}:
            if validation_spec is None:
                raise ValueError('validation history has no validation specification')
            spec = validation_spec
        if 'measurements' in value:
            rows = value['measurements']
            if not isinstance(rows, list):
                raise ValueError(f'{label} measurements must be an array')
            keys = set()
            for row in rows:
                if not isinstance(row, dict) or row.get('metric') not in UNITS:
                    raise ValueError(f'{label} unsupported measurement identity')
                key = metric_key(row)
                if key in keys:
                    raise ValueError(f'{label} duplicate measurement identity')
                keys.add(key)
                if row.get('value') is not None:
                    finite(row['value'], 'measurement')
                if row['metric'] in {'mtf', 'rms_spot_um'}:
                    for name in ('field', 'wavelength'):
                        if type(row.get(name)) is not int or row[name] < 1:
                            raise ValueError(f'{label} invalid measurement {name}')
                    if row['metric'] == 'mtf':
                        finite(row.get('frequency'), 'frequency')
                        if row.get('axis') not in {'tangential', 'sagittal'}:
                            raise ValueError(f'{label} invalid MTF axis')
                    for metadata in (row.get('analysis', {}), row.get('settings', {})):
                        for name in ('field', 'wavelength'):
                            if name in metadata and metadata[name] != row[name]:
                                raise ValueError(f'{label} measurement settings identity mismatch')
            if spec is not None and 'assessment' in value:
                claimed = value['assessment']
                if value.get('status') == 'analysis_failed':
                    if claimed.get('passes') is not False:
                        raise ValueError('failed analysis cannot pass requirements')
                elif claimed != assess(spec, rows):
                    raise ValueError(f'{label} assessment differs from measurements')
            if spec is not None and ('objective_value' in value or 'objective_breakdown' in value):
                calculated = objective_breakdown(spec, rows)
                if ('objective_value' in value and value['objective_value'] != calculated['value']) or (
                        'objective_breakdown' in value and value['objective_breakdown'] != calculated):
                    raise ValueError(f'{label} objective evidence differs from measurements')
        for key, child in value.items():
            if key not in {'spec', 'assessment', 'validation'}:
                _measurement_entries(child, spec, label + '.' + key, validation_spec)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _measurement_entries(child, spec, f'{label}[{index}]', validation_spec)


def _parameter_evidence(entry, initial, parameters, expected):
    from _lib.optimization import _fixed_inspection
    actual = entry.get('parameters_mm', [])
    if len(actual) != len(expected):
        raise ValueError('parameter evidence length mismatch')
    inspection = entry['inspection']
    surfaces = {s['index']: s for s in inspection['surfaces']}
    originals = {s['index']: s for s in initial['surfaces']}
    if len(surfaces) != len(inspection['surfaces']):
        raise ValueError('duplicate inspection surface identity')
    for parameter, found, wanted in zip(parameters, actual, expected):
        index, name = parameter['surface'], parameter['parameter']
        if index <= 0 or index >= initial['image_surface'] or surfaces[index].get('is_image'):
            raise ValueError('parameter refers to a nonphysical or image surface')
        reported = finite(surfaces[index].get(name), 'inspection parameter')
        original = finite(originals[index].get(name), 'original parameter')
        tolerance = max(abs(wanted)*1e-12, 1e-12)
        if 'step_mm' in parameter:
            tolerance = min(tolerance, parameter['step_mm']*1e-6)
        if (any(abs(finite(x, 'parameter')-wanted) > tolerance or
                (wanted != original and x == original) for x in (found, reported)) or
                ('step_mm' in parameter and reported != found)):
            raise ValueError('parameter vector or inspection differs from declared value')
    try:
        if _fixed_inspection(inspection, initial, parameters) != _fixed_inspection(initial, initial, parameters):
            raise ValueError('fixed inspection invariants differ from baseline')
    except RuntimeError as exc:
        raise ValueError(f'fixed inspection evidence invalid: {exc}') from exc


def validate_sensitivity_evidence(report, spec):
    """Recompute declared-step sensitivities/rankings from serialized trial evidence.

    Pure offline helper for the review and owned-job acceptance boundaries. The
    caller must separately verify artifact hashes and each recorded assessment.
    """
    from _lib.sensitivity import (
        _difference,
        _measurements,
        validate_perturbations,
        validate_step_vector,
    )
    parameters = validate_perturbations(report['perturbations'])['parameters']
    baseline = report['baseline']
    vector = baseline['parameters_mm']
    validate_step_vector(parameters, vector)
    base_metrics, _ = _measurements(baseline['measurements'], spec)
    trials = report['trials']
    if len(vector) != len(parameters) or len(trials) != 2 * len(parameters):
        raise ValueError('sensitivity parameter/trial count mismatch')
    _parameter_evidence(baseline, baseline['inspection'], parameters, vector)
    expected = []
    for index, parameter in enumerate(parameters):
        pair = []
        for offset, direction in enumerate((-1, 1)):
            trial = trials[2 * index + offset]
            wanted = list(vector)
            wanted[index] += direction * parameter['step_mm']
            if (trial.get('parameter_index') != index or trial.get('direction') != direction or
                    trial.get('requested_parameters_mm') != wanted or len(trial.get('parameters_mm', [])) != len(wanted) or
                    any(not math.isclose(finite(a, 'sensitivity readback'), b, rel_tol=1e-12, abs_tol=1e-12)
                        for a, b in zip(trial['parameters_mm'], wanted))):
                raise ValueError('sensitivity trial identity or parameter mismatch')
            _parameter_evidence(trial, baseline['inspection'], parameters, wanted)
            pair.append(_measurements(trial['measurements'], spec, base_metrics)[0])
        result = {'parameter_index': index, **parameter, 'baseline_mm': vector[index], 'metrics': []}
        for key, row in base_metrics.items():
            identity = {k: row[k] for k in ('metric', 'field', 'wavelength', 'frequency', 'axis', 'unit') if k in row}
            result['metrics'].append({**identity, 'metric_key': key,
                **_difference(row['value'], pair[0][key]['value'], pair[1][key]['value'], parameter['step_mm'])})
        if spec.objective is not None:
            unit = '1' if spec.objective.get('aggregation') else UNITS[spec.objective['metric']]
            result['objective'] = {'unit': unit, **_difference(objective_value(spec, baseline['measurements']),
                objective_value(spec, trials[2 * index]['measurements']),
                objective_value(spec, trials[2 * index + 1]['measurements']), parameter['step_mm'])}
        expected.append(result)
    if report.get('sensitivities') != expected:
        raise ValueError('sensitivity derivatives differ from trial evidence')
    rankings = []
    for key, row in base_metrics.items():
        ranked = []
        for item in expected:
            metric = next(m for m in item['metrics'] if m['metric_key'] == key)
            ranked.append({k: item[k] for k in ('parameter_index', 'surface', 'parameter', 'step_mm')} |
                {'metric_key': key, 'unit': row['unit'], 'declared_step_effect': metric['declared_step_effect']})
        rankings.append({'metric_key': key, 'unit': row['unit'],
                         'parameters': sorted(ranked, key=lambda r: -r['declared_step_effect'])})
    if report.get('rankings') != rankings:
        raise ValueError('sensitivity rankings differ from declared-step effects')


def _validate(report, path):
    if not isinstance(report, dict):
        raise ValueError('receipt must be a JSON object')  # noqa: TRY004 -- malformed serialized input
    failed = report.get('status') == 'failed' or (path.name == 'failure.json' and 'error' in report)
    action = report.get('action', 'unknown')
    status = 'failed' if failed else report.get('status')
    if not failed and (report.get('schema') != '1' or status not in STATUSES.get(action, set())):
        raise ValueError('unsupported receipt schema, action or status')
    if not failed and (path.parent / 'failure.json').exists():
        raise ValueError('failure receipt exists; render failure.json for diagnostic output')
    verified = {}
    artifacts = report.get('artifacts', {})
    if not isinstance(artifacts, dict):
        raise ValueError('artifacts must be an object')  # noqa: TRY004 -- malformed serialized input
    if not failed:
        if report.get('source_unchanged') is not True or report.get('baseline_restored') is not True:
            raise ValueError('source preservation or restoration not verified')
        source = report.get('source', {})
        if not isinstance(source.get('path'), str) or not _digest(source.get('sha256')):
            raise ValueError('source identity missing')
        if 'baseline_model' not in artifacts:
            raise ValueError('missing baseline artifact')
    for name, raw in artifacts.items():
        if name.endswith('_model') or name == 'source_snapshot':
            artifact = _confined(raw, path.parent)
            digest = _sha(artifact.read_bytes())
            hash_name = name + '_sha256' if name == 'source_snapshot' else name[:-6] + '_sha256'
            if artifacts.get(hash_name) != digest:
                raise ValueError('artifact hash differs from receipt')
            verified[str(artifact.relative_to(path.parent)).replace('\\', '/')] = digest
    if 'source_snapshot_sha256' in artifacts:
        snapshots = list(path.parent.glob('source_snapshot.*'))
        if len(snapshots) != 1:
            raise ValueError('source snapshot missing or ambiguous')
        snapshot = _confined(str(snapshots[0]), path.parent)
        digest = _sha(snapshot.read_bytes())
        if digest != artifacts['source_snapshot_sha256'] or digest != report.get('source', {}).get('sha256'):
            raise ValueError('source snapshot identity mismatch')
        verified[snapshot.name] = digest
    spec = None
    if (not failed or 'spec' in report) and (action != 'inspect' or 'spec' in report):
        _snapshot(report, 'spec', 'spec.json', path.parent, verified, required=not failed)
        if 'spec' in report:
            spec = DesignSpec.from_dict(report['spec'])
    for key, filename in [('variables', 'variables.json'), ('tolerance', 'tolerance.json'),
                          ('perturbations', 'perturbations.json'), ('changes', 'changes.json')]:
        required = not failed and {'optimize': 'variables', 'tolerance': 'tolerance',
                                   'sensitivity': 'perturbations', 'edit': 'changes'}.get(action) == key
        _snapshot(report, key, filename, path.parent, verified, required=required)
    validation = report.get('validation')
    vspec = DesignSpec.from_dict(validation['spec']) if validation is not None else None
    _measurement_entries(report, spec, validation_spec=vspec)
    baseline = report.get('baseline', report.get('nominal'))
    if not failed:
        if not isinstance(baseline, dict):
            raise ValueError('baseline evidence missing')
        if action != 'inspect' and ('measurements' not in baseline or 'assessment' not in baseline):
            raise ValueError('baseline evaluation missing')
        if action == 'inspect' and not isinstance(baseline.get('inspection'), dict):
            raise ValueError('baseline inspection missing')
    candidate = report.get('candidate')
    accepted = not failed and status in {'improved', 'applied'}
    if accepted:
        if (not isinstance(candidate, dict) or 'measurements' not in candidate or
                candidate.get('assessment', {}).get('passes') is not True or
                report.get('saved_candidate_verified') is not True or 'candidate_model' not in artifacts):
            raise ValueError('accepted candidate lacks verified passing evidence')
        if status == 'improved':
            before = objective_value(spec, baseline['measurements'])
            after = objective_value(spec, candidate['measurements'])
            sign = 1 if spec.objective['direction'] == 'maximize' else -1
            if sign * (after - before) <= spec.data['minimum_gain']:
                raise ValueError('candidate improvement inconsistent with objective')
    elif not failed and (candidate is not None or 'candidate_model' in artifacts or report.get('saved_candidate_verified') is True):
        raise ValueError('nonaccepted status contains accepted candidate evidence')
    if not failed and action == 'audit' and baseline['assessment']['passes'] != (status == 'requirements_met'):
        raise ValueError('audit status differs from assessment')
    if not failed and (status == 'validation_failed' or (action == 'edit' and status == 'requirements_not_met')):
        if not isinstance(report.get('rejected_candidate'), dict) or 'rejected_candidate_model' not in artifacts:
            raise ValueError('rejected candidate evidence missing')
        if action == 'edit' and report['rejected_candidate'].get('assessment', {}).get('passes') is not False:
            raise ValueError('rejected edit assessment must fail')
    if validation is not None:
        _snapshot(validation, 'spec', 'validation-spec.json', path.parent, verified, required=True)
        _measurement_entries(validation, vspec, 'validation')
        wanted = {'improved': 'passed', 'validation_failed': 'requirements_not_met',
                  'no_acceptable_improvement': 'not_run_no_candidate'}.get(status)
        if not failed and wanted is not None and validation.get('status') != wanted:
            raise ValueError('validation status inconsistent with candidate acceptance')
        if not failed and wanted in {'passed', 'requirements_not_met'}:
            for name, selected in [('baseline', baseline), ('candidate', candidate or report.get('rejected_candidate'))]:
                entry = validation.get(name)
                if not isinstance(entry, dict) or 'assessment' not in entry or not isinstance(selected, dict):
                    raise ValueError('validation evaluation missing')
                if entry.get('parameters_mm') != selected.get('parameters_mm') or not entry.get('parameters_mm'):
                    raise ValueError('validation model parameter identity mismatch')
            if validation['candidate']['assessment']['passes'] != (wanted == 'passed'):
                raise ValueError('validation result inconsistent with assessment')
    if action == 'sensitivity' and not failed:
        validate_sensitivity_evidence(report, spec)
    if action == 'edit' and not failed:
        from _lib.model_actions import validate_changes
        changes = validate_changes(report['changes'])['changes']
        _parameter_evidence(baseline, baseline['inspection'], changes, [c['expected_mm'] for c in changes])
        selected = candidate or report['rejected_candidate']
        _parameter_evidence(selected, baseline['inspection'], changes, [c['value_mm'] for c in changes])
    return action, status, accepted, verified


def _text(value):
    if value is None:
        return 'unavailable'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return str(value)


def _md(value):
    value = html.escape(_text(value), quote=True)
    for char in ('\\', '`', '*', '_', '[', ']', '(', ')', '#', '|', '!'):
        value = value.replace(char, '\\' + char)
    return value.replace('\r', ' ').replace('\n', ' ')


class _Document:
    def __init__(self):
        self.markdown = []
        self.html = []

    def heading(self, title, level=2):
        self.markdown.extend(['#' * level + ' ' + title, ''])
        self.html.append(f'<h{level}>{html.escape(title)}</h{level}>')

    def paragraph(self, value):
        self.markdown.extend([_md(value), ''])
        self.html.append('<p>' + html.escape(_text(value)) + '</p>')

    def table(self, headers, rows):
        rows = list(rows)
        if not rows:
            self.paragraph('Data unavailable.')
            return
        self.markdown.extend(['| ' + ' | '.join(_md(x) for x in headers) + ' |',
                              '| ' + ' | '.join('---' for _ in headers) + ' |'])
        self.html.append('<div class="table-scroll"><table><thead><tr>' + ''.join('<th>' + html.escape(str(x)) + '</th>' for x in headers) + '</tr></thead><tbody>')
        for row in rows:
            self.markdown.append('| ' + ' | '.join(_md(x) for x in row) + ' |')
            self.html.append('<tr>' + ''.join('<td>' + html.escape(_text(x)) + '</td>' for x in row) + '</tr>')
        self.markdown.append('')
        self.html.append('</tbody></table></div>')

    def evidence(self, title, value):
        self.heading(title)
        if isinstance(value, (dict, list)):
            pretty = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
            fence = '~' * max(3, 1 + max((len(s) for s in re.findall('~+', pretty)), default=0))
            self.markdown.extend([fence + 'json', html.escape(pretty, quote=False), fence, ''])
            self.html.append('<details><summary>Show recorded structured evidence</summary><pre>' + html.escape(pretty) + '</pre></details>')
        else:
            self.paragraph(value if value is not None else 'Data unavailable.')


def _inspection(entry, report):
    return (entry or {}).get('inspection', report.get('inspection', {}))


def _physical(row, inspection):
    metadata = {**row.get('analysis', {}), **row.get('settings', {})}
    xy, wave = metadata.get('field_xy_deg'), metadata.get('wavelength_um')
    invariants = inspection.get('invariants', {})
    fields, waves = invariants.get('fields', []), invariants.get('wavelengths', [])
    if xy is None and isinstance(fields, list):
        match = next((f for f in fields if f.get('index') == row['field']), None)
        if match and 'x_deg' in match and 'y_deg' in match:
            xy = [match['x_deg'], match['y_deg']]
    if wave is None and isinstance(waves, list):
        match = next((w for w in waves if w.get('index') == row['wavelength']), None)
        if match:
            wave = match.get('um')
    return xy, wave, metadata


def _positions(inspection):
    recorded = inspection.get('axial_positions_mm')
    if recorded:
        return [(i, p) for i, p in enumerate(recorded) if type(p) in (float, int) and math.isfinite(p)], 'Recorded axial coordinates (mm).'
    surfaces = inspection.get('surfaces', inspection.get('prescription', []))
    surfaces = sorted((s for s in surfaces if s['index'] > 0), key=lambda s: s['index'])
    result, position = [], 0.0
    for surface in surfaces:
        result.append((surface['index'], position))
        if surface.get('is_image'):
            break
        gap = surface.get('thickness_mm')
        if type(gap) not in (int, float) or not math.isfinite(gap):
            return [], 'Axial vertex positions unavailable.'
        position += gap
        if not math.isfinite(position):
            return [], 'Axial vertex positions unavailable.'
    return result, 'Axial positions derived from recorded thicknesses; first real surface = 0 mm.'


def _render(report, action, status, accepted):
    doc = _Document()
    doc.heading('Optical design review', 1)
    doc.paragraph(f'Action: {action}. Outcome: {status}.')
    doc.paragraph('Diagnostic failure — results are incomplete and not accepted.' if status == 'failed' else 'Local receipt consistency and recorded artifact hashes verified.')
    doc.paragraph('Accepted candidate: saved and verified in the recorded job.' if accepted else 'No accepted candidate. Rejected or partial results remain diagnostic evidence.')
    doc.paragraph('This review runs no optical analyses. The source file was not reopened; source preservation and model readbacks are recorded job claims. Artifact hashes verify local bytes, not optical performance.')
    baseline = report.get('baseline', report.get('nominal')) or {}
    candidate = report.get('candidate') or report.get('rejected_candidate') or {}
    after_label = 'Candidate' if accepted else 'Rejected / diagnostic candidate'
    doc.heading('Provenance')
    doc.table(['Item', 'Recorded value'], [(key, report.get(key)) for key in ('source', 'source_unchanged', 'baseline_restored', 'saved_candidate_verified', 'evaluations', 'python_version', 'error')])
    doc.paragraph('Independent validation: ' + str((report.get('validation') or {}).get('status', 'not recorded')))
    doc.evidence('Engine and model inspection', _inspection(baseline, report).get('engine'))
    doc.heading('Requirements and measurements')
    spec = report.get('spec')
    if spec is None:
        doc.paragraph('Requirements: not supplied. No requirement pass is inferred.')
    for title, entry in [('Baseline', baseline), (after_label, candidate)]:
        if not entry:
            continue
        doc.heading(title + ' requirements', 3)
        doc.table(['Requirement', 'Status', 'Value / reason', 'Unit', 'Constraint'],
                  [(r.get('id'), r.get('status'), r.get('value', r.get('reason')), r.get('unit'), r.get('requirement'))
                   for r in entry.get('assessment', {}).get('requirements', [])])
    before = {metric_key(row): row for row in baseline.get('measurements', [])}
    after = {metric_key(row): row for row in candidate.get('measurements', [])}
    rows = []
    for key in sorted(before.keys() | after.keys()):
        b, a = before.get(key, {}), after.get(key, {})
        bv, av = b.get('value'), a.get('value')
        delta = av - bv if bv is not None and av is not None and a.get('unit') == b.get('unit') else None
        if delta is not None and not math.isfinite(delta):
            delta = None
        rows.append((key, b.get('value', b.get('reason')), a.get('value', a.get('reason')), delta, b.get('unit', a.get('unit'))))
    doc.heading('Metric comparison', 3)
    doc.table(['Metric identity', 'Baseline', after_label, 'Delta', 'Unit'], rows)
    doc.heading('Physical fields and wavelengths')
    doc.paragraph('Indices are 1-based engine selections. Physical field coordinates and wavelength values are shown only when recorded; unavailable coordinates are not inferred from indices.')
    physical = []
    for title, entry in [('Baseline', baseline), (after_label, candidate)]:
        for row in entry.get('measurements', []):
            if row['metric'] in {'mtf', 'rms_spot_um'}:
                xy, wave, analysis = _physical(row, _inspection(entry, report))
                physical.append((title, metric_key(row), xy, wave, analysis))
    doc.table(['Evaluation', 'Metric identity', 'Physical field (recorded units)', 'Wavelength (um)', 'Analysis settings / identity'], physical)
    doc.evidence('Declared analysis coverage', {k: spec.get(k) for k in ('fields', 'wavelengths', 'frequencies_cyc_per_mm', 'analysis')} if spec else None)
    doc.heading('Recorded MTF and spot samples')
    doc.paragraph('Charts show only recorded samples. No fitted curve, inferred ray intercepts, or unmeasured frequency coverage is supplied. Exact values and full identities appear above.')
    for metric, title in [('mtf', 'MTF'), ('rms_spot_um', 'RMS spot radius')]:
        points = [(label, row) for label, entry in [('Baseline', baseline), (after_label, candidate)]
                  for row in entry.get('measurements', []) if row['metric'] == metric and row.get('value') is not None and row.get('unit') == UNITS[metric]]
        if points:
            doc.heading(title, 3)
            doc.html.append(_chart(points, metric, title))
            doc.paragraph(f'{title}: {len(points)} recorded samples; chart included in standalone HTML.')
    doc.heading('Prescription changes')
    bi, ai = _inspection(baseline, report), _inspection(candidate, {})
    bs = {s['index']: s for s in bi.get('surfaces', bi.get('prescription', []))}
    ass = {s['index']: s for s in ai.get('surfaces', ai.get('prescription', []))}
    changes = []
    for index in sorted(bs.keys() | ass.keys()):
        for key in sorted(bs.get(index, {}).keys() | ass.get(index, {}).keys()):
            b, a = bs.get(index, {}).get(key), ass.get(index, {}).get(key)
            if candidate and b != a:
                changes.append((index, key, b, a))
    if candidate and bi.get('focus_mm') != ai.get('focus_mm'):
        changes.append(('image-space gap', 'focus_mm', bi.get('focus_mm'), ai.get('focus_mm')))
    doc.table(['Surface', 'Parameter', 'Baseline', after_label], changes)
    doc.paragraph('No change table does not certify unchanged geometry when inspection data are missing.')
    doc.heading('Axial schematic')
    doc.paragraph('Axial schematic only — surface vertices along the optical axis. No traced rays, lens sag, clear apertures, or imaging performance are depicted.')
    finite_positions, convention = _positions(bi)
    if len(finite_positions) >= 2:
        doc.paragraph(convention)
        doc.html.append(_schematic(finite_positions))
        doc.table(['Surface index', 'Axial vertex (mm)'], finite_positions)
    else:
        doc.paragraph('Axial vertex positions unavailable; no layout is invented.')
    for key, title in [('validation', 'Independent validation evidence'), ('objective', 'Objective'),
                       ('sensitivities', 'Local sensitivity derivatives'), ('rankings', 'Sensitivity rankings'),
                       ('trials', 'Sensitivity trials'), ('sensitivity', 'Tolerance sensitivity trials'),
                       ('yield', 'Recorded tolerance yield'), ('paired_yield', 'Paired tolerance yield')]:
        if key in report:
            if key == 'sensitivities':
                doc.heading('Sensitivity comparison')
                doc.table(['Surface / parameter', 'Step (mm)', 'Metric identity', 'Derivative (unit/mm)', 'Declared-step effect (unit)', 'Nonlinearity indicator'],
                          [(f"{item['surface']} / {item['parameter']}", item['step_mm'], row['metric_key'],
                            row['derivative_per_mm'], row['declared_step_effect'], row['nonlinearity_indicator'])
                           for item in report[key] for row in item['metrics']])
            doc.evidence(title, report[key])
    if spec and spec.get('objective'):
        doc.evidence('Objective definition', spec['objective'])
        for name, entry in [('Baseline', baseline), (after_label, candidate)]:
            if entry and 'objective_breakdown' in entry:
                doc.evidence(name + ' objective evidence', entry['objective_breakdown'])
    doc.evidence('Baseline physical model inventory', bi)
    if candidate:
        doc.evidence(after_label + ' physical model inventory', ai)
    doc.heading('Evidence boundary')
    doc.paragraph('Missing data remain unavailable. A failed requirement remains failed. Sensitivity describes local finite steps; it is not a manufacturing yield estimate. Optimizer results do not prove a global optimum. Separate validation is reported only when present.')
    return doc


def _chart(points, metric, title):
    xs = [row['frequency'] if metric == 'mtf' else row['field'] for _, row in points]
    ys = [row['value'] for _, row in points]
    lo, hi = min(xs), max(xs)
    bottom, top = min(0, min(ys)), max(1e-12, max(ys))
    # Scaling through a bounded ratio also avoids overflow on finite extreme inputs.
    def scale(value, low, high):
        size = max(abs(low), abs(high), 1)
        return (value / size - low / size) / ((high / size - low / size) or 1)
    body = [f'<svg viewBox="0 0 760 270" role="img" aria-label="{html.escape(title)} recorded samples"><rect width="760" height="270" fill="#fff"/><path d="M70 20V220H730" fill="none" stroke="#64748b"/>']
    for (label, row), x, y in zip(points, xs, ys):
        px, py = 70 + 650 * scale(x, lo, hi), 220 - 180 * scale(y, bottom, top)
        color = '#155e75' if label == 'Baseline' else '#b45309'
        body.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="5" fill="{color}"><title>{html.escape(label + ": " + metric_key(row) + " = " + str(y))}</title></circle>')
    xlabel = 'Frequency (cycles/mm)' if metric == 'mtf' else 'Field index (1-based; discrete samples)'
    body += [f'<text x="70" y="240">{lo:g}</text><text x="700" y="240">{hi:g}</text>',
             f'<text x="8" y="30">{top:.4g}</text><text x="8" y="220">{bottom:.4g}</text>',
             f'<text x="260" y="260">{xlabel}</text><text x="80" y="20">{html.escape(title)} ({UNITS[metric]})</text></svg>',
             '<p class="legend">Teal: baseline. Amber: candidate (acceptance status stated above). Points only; no interpolation.</p>']
    return ''.join(body)


def _schematic(positions):
    lo, hi = min(p for _, p in positions), max(p for _, p in positions)
    size = max(abs(lo), abs(hi), 1)
    span = (hi / size - lo / size) or 1
    body = ['<svg viewBox="0 0 760 180" role="img" aria-label="Axial surface vertex schematic"><path d="M30 80H730" stroke="#64748b"/>']
    for i, p in positions:
        x = 40 + 680 * (p / size - lo / size) / span
        body.append(f'<path d="M{x:.3f} 45V115" stroke="#155e75"/><text x="{x:.3f}" y="{135 + (i % 2) * 20}" text-anchor="middle">S{i}</text>')
    return ''.join(body) + '</svg>'


def _load_verified(report_path):
    if str(report_path).startswith(('\\\\', '//')):
        raise ValueError('receipt must be a local file')
    path = Path(report_path).resolve(strict=True)
    data = path.read_bytes()
    report = _decode(data)
    try:
        action, status, accepted, verified = _validate(report, path)
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError(f'invalid receipt structure: {exc}') from exc
    metadata = {'action': action, 'status': status, 'accepted_candidate': accepted,
                'receipt_sha256': _sha(data), 'verified_local_artifacts': dict(sorted(verified.items()))}
    return report, metadata


def validate_review_receipt(report_path) -> dict:
    """Validate local evidence without writing files or running an optical engine.

    Returns action, status, accepted_candidate, receipt_sha256 and
    verified_local_artifacts. Does not establish original job ownership.
    """
    return _load_verified(report_path)[1]


def render_review(report_path, out) -> dict:
    """Validate a local receipt and create a new standalone review directory.

    The manifest uses relative output names so identical input produces identical
    output bytes regardless of the chosen new output directory.
    """
    target = Path(out).resolve()
    if target.exists():
        raise ValueError('review output directory must be new')
    report, metadata = _load_verified(report_path)
    try:
        doc = _render(report, metadata['action'], metadata['status'], metadata['accepted_candidate'])
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
        raise ValueError(f'invalid receipt structure: {exc}') from exc
    markdown = ('\n'.join(doc.markdown) + '\n').encode('utf-8')
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'; form-action \'none\'">'
            '<title>Optical design review</title><style>'
            'body{max-width:1100px;margin:40px auto;padding:0 24px;color:#172b3a;background:#f7f8fa;font:16px/1.55 system-ui,sans-serif}'
            'h1{font-size:2.3rem}h2{border-top:1px solid #ccd5dd;padding-top:28px;margin-top:40px}h3{margin-top:28px}'
            'p,td{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;background:white;font-size:14px}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,monospace;background:white;padding:16px}summary{cursor:pointer;color:#155e75}'
            'td,th{border:1px solid #d4dce2;padding:10px;text-align:left;vertical-align:top}th{background:#e8eef2}'
            '.table-scroll{overflow-x:auto}svg{display:block;width:100%;max-height:330px;background:white;margin:16px 0;font:13px system-ui}'
            '.legend{font-size:14px} @media print{body{margin:0;background:white}h2{break-after:avoid}tr,svg{break-inside:avoid}}'
            '</style></head><body>' + '\n'.join(doc.html) + '</body></html>\n').encode('utf-8')
    outputs = {'report.html': page, 'report.md': markdown}
    manifest = {'schema': '1', 'tool': 'optical-design-review', **metadata,
                'verification': 'offline receipt consistency and local hashes; no optical engine or source reopen',
                'files': {name: {'sha256': _sha(content), 'bytes': len(content)} for name, content in outputs.items()}}
    target.mkdir(parents=True, exist_ok=False)
    for name, content in outputs.items():
        (target / name).write_bytes(content)
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    return manifest
