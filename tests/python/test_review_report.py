"""Offline report integrity and truthful presentation contracts."""
import json
import re

import pytest
from _lib.design_contract import DesignSpec, assess
from _lib.design_jobs import run_job, sha256
from test_design_contract import base_spec
from test_design_jobs import AnalyticFocus


def receipt(tmp_path, action='audit'):
    model = tmp_path / 'source.lens'
    model.write_text('60')
    directory = tmp_path / 'evidence'
    report = run_job(model, DesignSpec.from_dict(base_spec()), directory, AnalyticFocus, action=action)
    return directory / 'report.json', report


def write(path, report):
    path.write_text(json.dumps(report), encoding='utf-8')


def render(path, out):
    from _lib.review_report import render_review
    return render_review(path, out)


def test_deterministic_offline_review_preserves_failed_requirements(tmp_path):
    path, _report = receipt(tmp_path)
    # Source is provenance text only; the renderer must never reopen it.
    (tmp_path / 'source.lens').unlink()
    first = render(path, tmp_path / 'review-a')
    second = render(path, tmp_path / 'review-b')
    assert first == second
    for name in ('report.html', 'report.md', 'manifest.json'):
        assert (tmp_path / 'review-a' / name).read_bytes() == (tmp_path / 'review-b' / name).read_bytes()
    html = (tmp_path / 'review-a/report.html').read_text(encoding='utf-8')
    assert 'requirements_not_met' in html and 'No accepted candidate' in html
    assert 'contrast' in html and 'fail' in html
    assert 'MTF' in html and '<svg' in html
    assert 'Physical field' in html and 'unavailable' in html
    assert 'source file was not reopened' in html
    assert first['receipt_sha256'] == sha256(path)


def test_improved_review_compares_actual_measurements_and_prescription(tmp_path):
    path, _report = receipt(tmp_path, 'refocus')
    render(path, tmp_path / 'review')
    md = (tmp_path / 'review/report.md').read_text(encoding='utf-8')
    assert 'Accepted candidate' in md and r'focus\_mm' in md
    assert 'Baseline' in md and 'Candidate' in md and 'Delta' in md
    assert 'Independent validation: not recorded' in md


@pytest.mark.parametrize('mutation', ['hash', 'outside', 'traversal', 'duplicate', 'assessment', 'spec', 'missing', 'false_acceptance'])
def test_invalid_receipt_is_rejected_before_creating_output(tmp_path, mutation):
    path, report = receipt(tmp_path)
    if mutation == 'hash':
        report['artifacts']['baseline_sha256'] = '0' * 64
    elif mutation == 'outside':
        report['artifacts']['baseline_model'] = str(tmp_path / 'source.lens')
    elif mutation == 'traversal':
        report['artifacts']['baseline_model'] = '../source.lens'
    elif mutation == 'duplicate':
        report['baseline']['measurements'] *= 2
    elif mutation == 'assessment':
        report['baseline']['assessment']['passes'] = True
    elif mutation == 'spec':
        report['spec']['requirements'][0]['min'] = 0
    elif mutation == 'missing':
        report['baseline']['measurements'] = []
    else:
        report['status'] = 'requirements_met'
    write(path, report)
    with pytest.raises(ValueError):
        render(path, tmp_path / 'review')
    assert not (tmp_path / 'review').exists()


def test_untrusted_text_is_escaped_in_html_and_markdown(tmp_path):
    path, report = receipt(tmp_path)
    payload = '<script>alert(1)</script> [click](javascript:alert(2)) | injected'
    report['source']['path'] = payload
    report['baseline']['inspection']['engine']['name'] = payload
    write(path, report)
    render(path, tmp_path / 'review')
    html = (tmp_path / 'review/report.html').read_text(encoding='utf-8')
    md = (tmp_path / 'review/report.md').read_text(encoding='utf-8')
    assert '<script' not in html and '<script' not in md
    outside_code = re.sub(r'(?ms)^~~~json\n.*?^~~~\n', '', md)
    assert '&lt;script&gt;' in html and '[click](javascript:' not in outside_code
    assert '<script' not in html and 'src="http' not in html


def test_failure_receipt_is_diagnostic_without_invented_metrics(tmp_path):
    path = tmp_path / 'failure.json'
    write(path, {'error': 'engine stopped', 'baseline_restored': False})
    result = render(path, tmp_path / 'review')
    md = (tmp_path / 'review/report.md').read_text(encoding='utf-8')
    assert result['status'] == 'failed'
    assert 'Diagnostic failure' in md and 'No accepted candidate' in md
    assert 'engine stopped' in md and 'unavailable' in md


def test_existing_directory_never_overwritten(tmp_path):
    path, _ = receipt(tmp_path)
    out = tmp_path / 'review'
    out.mkdir()
    with pytest.raises(ValueError, match='new'):
        render(path, out)


def test_inspection_receipt_needs_no_fabricated_spec(tmp_path):
    path, report = receipt(tmp_path)
    for key in ('spec', 'spec_sha256', 'history'):
        report.pop(key)
    report.update(action='inspect', status='completed', baseline={'inspection': report['baseline']['inspection']})
    write(path, report)
    render(path, tmp_path / 'review')
    md = (tmp_path / 'review/report.md').read_text(encoding='utf-8')
    assert 'Requirements: not supplied' in md


def test_missing_measurement_can_be_truthfully_unavailable(tmp_path):
    path, report = receipt(tmp_path)
    report['baseline']['measurements'] = []
    report['baseline']['assessment'] = assess(DesignSpec.from_dict(report['spec']), [])
    report['baseline'].pop('objective_value', None)
    report['baseline'].pop('objective_breakdown', None)
    write(path, report)
    render(path, tmp_path / 'review')
    assert 'unavailable' in (tmp_path / 'review/report.md').read_text(encoding='utf-8')


def test_cli_json_is_manifest(tmp_path, run):
    import review
    path, _ = receipt(tmp_path)
    code, output, error = run(review.main, ['--report', str(path), '--out', str(tmp_path / 'review'), '--json'])
    assert code == 0, error
    assert json.loads(output)['receipt_sha256'] == sha256(path)


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / 'failure.json'
    path.write_text('{"error":"x","error":"y"}')
    with pytest.raises(ValueError, match='duplicate'):
        render(path, tmp_path / 'review')


@pytest.mark.parametrize('minimum,accepted', [(.5, True), (.6, False)])
def test_real_optimization_validation_receipts_are_rendered(tmp_path, minimum, accepted):
    from test_optimization import run, setup
    from test_optimization_validation import ValidationLens, validation
    model, raw, backend = setup(tmp_path, ValidationLens)
    run(model, raw, tmp_path / 'evidence', backend, validation_spec=validation(minimum))
    manifest = render(tmp_path / 'evidence/report.json', tmp_path / 'review')
    assert manifest['accepted_candidate'] is accepted
    text = (tmp_path / 'review/report.html').read_text(encoding='utf-8')
    assert 'unseen-field' in text
    assert ('validation_failed' in text) is (not accepted)


def test_real_tolerance_receipt_is_rendered(tmp_path):
    from _lib.tolerancing import run_tolerance_job
    from test_tolerancing import AffineBackend
    model = tmp_path / 'source.json'
    model.write_text('{"radius_mm":10,"thickness_mm":2}')
    spec = DesignSpec.from_dict({'schema': '1', 'fields': [1], 'wavelengths': [1],
        'requirements': [{'id': 'efl', 'metric': 'efl_mm', 'unit': 'mm', 'max': 10.5}]})
    config = {'schema': '1', 'samples': 3, 'seed': 1, 'perturbations': [
        {'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform', 'half_width_mm': 1}]}
    run_tolerance_job(model, spec, tmp_path / 'evidence', AffineBackend, config)
    manifest = render(tmp_path / 'evidence/report.json', tmp_path / 'review')
    assert manifest['accepted_candidate'] is False and manifest['status'] == 'completed'


def test_native_settings_identity_is_checked_and_physical_values_displayed(tmp_path):
    path, report = receipt(tmp_path)
    row = report['baseline']['measurements'][0]
    row['settings'] = {'field': 1, 'wavelength': 1, 'field_xy_deg': [0, 12.5], 'wavelength_um': .78}
    write(path, report)
    render(path, tmp_path / 'review')
    text = (tmp_path / 'review/report.html').read_text(encoding='utf-8')
    assert '12.5' in text and '0.78' in text
    row['settings']['field'] = 2
    write(path, report)
    with pytest.raises(ValueError, match='identity'):
        render(path, tmp_path / 'invalid')


def test_objective_evidence_cannot_disagree_with_measurements(tmp_path):
    path, report = receipt(tmp_path, 'refocus')
    report['candidate']['objective_value'] = 12345
    write(path, report)
    with pytest.raises(ValueError, match='objective'):
        render(path, tmp_path / 'review')


@pytest.mark.parametrize('mutation', ['none', 'derivative', 'trial', 'ranking'])
def test_real_sensitivity_receipt_and_derived_data_integrity(tmp_path, mutation):
    from test_sensitivity import AnalyticLens, run, setup
    model, raw, backend = setup(tmp_path, AnalyticLens)
    report = run(model, raw, tmp_path / 'evidence', backend)
    if mutation == 'derivative':
        report['sensitivities'][0]['metrics'][0]['derivative_per_mm'] += 1
    elif mutation == 'trial':
        report['trials'][0]['direction'] = 1
    elif mutation == 'ranking':
        report['rankings'][0]['parameters'][0]['unit'] = 'mm'
    path = tmp_path / 'evidence/report.json'
    write(path, report)
    if mutation == 'none':
        result = render(path, tmp_path / 'review')
        assert result['status'] == 'completed' and not result['accepted_candidate']
        assert 'Sensitivity rankings' in (tmp_path / 'review/report.html').read_text(encoding='utf-8')
    else:
        with pytest.raises(ValueError, match='sensitivity'):
            render(path, tmp_path / 'review')


def test_tiny_sensitivity_step_cannot_claim_unchanged_model_readbacks(tmp_path):
    from test_sensitivity import AnalyticLens, run, setup
    model, raw, backend = setup(tmp_path, AnalyticLens)
    parameters = {'schema': '1', 'parameters': [
        {'surface': 1, 'parameter': 'radius_mm', 'step_mm': 1e-12}]}
    report = run(model, raw, tmp_path/'evidence', backend, parameters)
    for trial in report['trials']:
        trial['parameters_mm'][0] = 20
        trial['inspection']['surfaces'][1]['radius_mm'] = 20
    path = tmp_path/'evidence/report.json'
    write(path, report)
    with pytest.raises(ValueError, match='parameter|readback'):
        render(path, tmp_path/'review')


def test_sensitivity_receipt_rejects_unrepresentable_step_even_with_consistent_zero_effects(tmp_path):
    import copy

    from _lib.sensitivity import _difference
    from test_sensitivity import AnalyticLens, run, setup
    model, raw, backend = setup(tmp_path, AnalyticLens)
    parameters = {'schema': '1', 'parameters': [
        {'surface': 1, 'parameter': 'radius_mm', 'step_mm': .1}]}
    report = run(model, raw, tmp_path/'evidence', backend, parameters)
    step = 1e-30
    report['perturbations']['parameters'][0]['step_mm'] = step
    config_path = tmp_path/'evidence/perturbations.json'
    write(config_path, report['perturbations'])
    report['perturbations_sha256'] = sha256(config_path)
    baseline = report['baseline']
    for trial in report['trials']:
        identity = {k: trial[k] for k in ['kind', 'direction', 'parameter_index']}
        trial.clear()
        trial.update(copy.deepcopy(baseline), **identity, requested_parameters_mm=[20])
    sensitivity = report['sensitivities'][0]
    sensitivity['step_mm'] = step
    for metric, row in zip(sensitivity['metrics'], baseline['measurements']):
        metric.update(_difference(row['value'], row['value'], row['value'], step))
    value = baseline['objective_value']
    sensitivity['objective'].update(_difference(value, value, value, step))
    for ranking in report['rankings']:
        ranking['parameters'][0].update(step_mm=step, declared_step_effect=0.)
    path = tmp_path/'evidence/report.json'
    write(path, report)
    with pytest.raises(ValueError, match='step|distinct'):
        render(path, tmp_path/'review')


def test_axial_schematic_uses_known_thickness_and_native_field_inventory(tmp_path):
    path, report = receipt(tmp_path)
    inspection = report['baseline']['inspection']
    inspection['surfaces'] = [{'index': 0, 'thickness_mm': 'Infinity'},
        {'index': 1, 'thickness_mm': 5}, {'index': 2, 'thickness_mm': 10},
        {'index': 3, 'is_image': True}]
    inspection['invariants']['fields'] = [{'index': 1, 'x_deg': 0, 'y_deg': 9.75}]
    inspection['invariants']['wavelengths'] = [{'index': 1, 'um': .6328}]
    write(path, report)
    render(path, tmp_path / 'review')
    text = (tmp_path / 'review/report.html').read_text(encoding='utf-8')
    assert 'Axial surface vertex schematic' in text
    assert '9.75' in text and '0.6328' in text
    assert 'first real surface' in text


def test_standalone_receipt_validation_writes_nothing(tmp_path):
    from _lib.review_report import validate_review_receipt
    path, _ = receipt(tmp_path)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    validated = validate_review_receipt(path)
    assert validated['action'] == 'audit' and not validated['accepted_candidate']
    assert validated['receipt_sha256'] == sha256(path)
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


@pytest.mark.parametrize('action', ['inspect', 'edit', 'rejected_edit'])
def test_real_model_action_receipts(tmp_path, action):
    from _lib.model_actions import run_edit_job, run_inspect_job
    from test_model_actions import changes, setup
    model, raw, backend = setup(tmp_path)
    if action == 'inspect':
        run_inspect_job(model, tmp_path / 'evidence', lambda _: backend)
    else:
        if action == 'rejected_edit':
            raw['requirements'][0]['min'] = 1
        run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'evidence', lambda _: backend, changes())
    result = render(tmp_path / 'evidence/report.json', tmp_path / 'review')
    assert result['accepted_candidate'] is (action == 'edit')


@pytest.mark.parametrize('mutation', ['vector', 'fixed', 'source_snapshot_path', 'missing_changes'])
def test_edit_receipt_rejects_inconsistent_model_evidence(tmp_path, mutation):
    from _lib.model_actions import run_edit_job
    from test_model_actions import changes, setup
    model, raw, backend = setup(tmp_path)
    report = run_edit_job(model, DesignSpec.from_dict(raw), tmp_path / 'evidence', lambda _: backend, changes())
    if mutation == 'vector':
        report['candidate']['parameters_mm'][0] = 88
    elif mutation == 'fixed':
        report['candidate']['inspection']['invariants']['aperture_mm'] = 99
    elif mutation == 'source_snapshot_path':
        report['artifacts']['source_snapshot'] = str(model)
    else:
        del report['changes']
    path = tmp_path / 'evidence/report.json'
    write(path, report)
    with pytest.raises(ValueError):
        render(path, tmp_path / 'review')
