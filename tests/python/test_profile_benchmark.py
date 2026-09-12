import copy
import hashlib
import json
from pathlib import Path

import pytest
from _lib.profile_benchmark import validate_case


def huygens_case():
    return {'id': 'hx', 'method': 'huygens', 'axis': 'x', 'field': 1, 'wavelength': 0,
            'pupil': 512, 'image': 128, 'delta_um': 6, 'polarization': True,
            'reference': 'Planar'}


def test_huygens_requires_explicit_physical_settings():
    assert validate_case(huygens_case())['wavelength'] == 0
    case = huygens_case()
    del case['polarization']
    with pytest.raises(ValueError):
        validate_case(case)


@pytest.mark.parametrize('key,value', [('axis', 'z'), ('delta_um', 0), ('pupil', 100),
                                      ('field', True), ('wavelength', -1), ('reference', 'auto'),
                                      ('polarization', 1), ('image', 8192)])
def test_invalid_native_case_rejected(key, value):
    case = huygens_case()
    case[key] = value
    with pytest.raises(ValueError):
        validate_case(case)


def test_unknown_native_case_keys_rejected():
    case = huygens_case()
    case['save'] = 'source.zmx'
    with pytest.raises(ValueError):
        validate_case(case)


def pop_case():
    return {'id': 'p9', 'method': 'pop', 'field': 1, 'wavelength': 9, 'sampling': 1024,
            'window_mm': .4, 'waist_x_mm': .0025, 'waist_y_mm': .0025,
            'start_surface': 1, 'end_surface': 28, 'polarization': True, 'separate_xy': True,
            'power_w': 1, 'resampling': [{'surface': 4, 'width_mm': 8}]}


def test_pop_rejects_polychromatic_single_call_and_ambiguous_launch():
    assert validate_case(pop_case())['power_w'] == 1
    for key, value in [('wavelength', 0), ('waist_y_mm', 0), ('power_w', -1), ('resampling', [{'surface': 0, 'width_mm': 8}])]:
        case = copy.deepcopy(pop_case())
        case[key] = value
        with pytest.raises(ValueError):
            validate_case(case)


class ProfileBackend:
    def __init__(self, path):
        self.path = Path(path)
        self.setting = 'baseline'
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def inspect(self):
        return {'engine': {'name': 'analytic fixture', 'version': '1'}, 'setting': self.setting}

    def restore(self):
        self.setting = 'baseline'

    def evaluate(self, case):
        self.setting = case['id']
        axes = [case['axis']] if case['method'] == 'huygens' else ['x', 'y']
        return {'case': case, 'profiles': {axis: {'x_mm': [-1., 0., 1.], 'intensity': [0., 1., 0.],
                                                'profile_kind': 'cut', 'intensity_unit': 'relative' if case['method'] == 'huygens' else 'W/mm^2'} for axis in axes},
                **({'power_w': .8} if case['method'] == 'pop' else {})}


@pytest.fixture
def benchmark_setup(tmp_path):
    source = tmp_path / 'lens.zmx'
    source.write_bytes(b'original model')
    reference = tmp_path / 'reference.json'
    reference.write_text(json.dumps({'records': [{'model_id': 'lens', 'case_id': 'hx',
                                                 'profiles': {'x': {'x_mm': [-1., 0., 1.], 'intensity': [0., 1., 0.]}}}]}))
    manifest = {'schema_version': 1, 'name': 'regression',
                'models': [{'id': 'lens', 'path': 'lens.zmx', 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}],
                'cases': [huygens_case()],
                'reference': {'path': 'reference.json', 'sha256': hashlib.sha256(reference.read_bytes()).hexdigest()},
                'comparison': {'rtol': 1e-6, 'atol': 1e-9}}
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest))
    return source, reference, manifest, manifest_path


def test_benchmark_copies_checks_restoration_and_compares_raw_profiles(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    source, _, _, manifest_path = benchmark_setup
    instances = []

    def factory(path):
        b = ProfileBackend(path)
        instances.append(b)
        return b

    out = tmp_path / 'out'
    report = run_benchmark(manifest_path, out, factory)
    assert report['status'] == 'benchmark_passed' and report['reference_validated']
    assert report['records'][0]['comparison']['passes'] is True
    assert report['records'][0]['diagnostics']['x']
    assert instances[0].closed and instances[0].setting == 'baseline'
    assert instances[0].path != source and instances[0].path.read_bytes() == source.read_bytes()
    assert report['models'][0]['source_sha256'] == report['models'][0]['copied_sha256']
    assert report['source_unchanged'] is True
    assert json.loads((out / 'report.json').read_text())['status'] == 'benchmark_passed'


def test_without_reference_is_completed_but_unvalidated(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, manifest, path = benchmark_setup
    del manifest['reference'], manifest['comparison']
    path.write_text(json.dumps(manifest))
    report = run_benchmark(path, tmp_path / 'out', ProfileBackend)
    assert report['status'] == 'completed' and report['reference_validated'] is False
    assert report['records'][0]['comparison'] is None


@pytest.mark.parametrize('change', ['model_hash', 'reference_hash', 'unknown', 'duplicate_model', 'duplicate_case', 'bad_tolerance', 'missing_axis', 'missing_record'])
def test_invalid_manifest_or_reference_never_opens_engine(benchmark_setup, tmp_path, change):
    from _lib.profile_benchmark import run_benchmark

    _, reference, manifest, path = benchmark_setup
    if change == 'model_hash':
        manifest['models'][0]['sha256'] = '0' * 64
    elif change == 'reference_hash':
        manifest['reference']['sha256'] = '0' * 64
    elif change == 'unknown':
        manifest['save_original'] = True
    elif change == 'duplicate_model':
        manifest['models'] *= 2
    elif change == 'duplicate_case':
        manifest['cases'] *= 2
    elif change == 'bad_tolerance':
        manifest['comparison']['rtol'] = -1
    else:
        data = {'records': []} if change == 'missing_record' else {'records': [{'model_id': 'lens', 'case_id': 'hx', 'profiles': {}}]}
        reference.write_text(json.dumps(data))
        manifest['reference']['sha256'] = hashlib.sha256(reference.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest))
    opened = []
    with pytest.raises(ValueError):
        run_benchmark(path, tmp_path / 'out', lambda p: opened.append(p))
    assert not opened


@pytest.mark.parametrize('kind', ['intensity', 'grid'])
def test_wrong_absolute_intensity_or_coordinates_cannot_pass(benchmark_setup, tmp_path, kind):
    from _lib.profile_benchmark import run_benchmark

    _, _, _, path = benchmark_setup

    class Different(ProfileBackend):
        def evaluate(self, case):
            result = super().evaluate(case)
            result['profiles']['x']['intensity' if kind == 'intensity' else 'x_mm'] = [0., 2., 0.] if kind == 'intensity' else [-2., 0., 2.]
            return result

    report = run_benchmark(path, tmp_path / 'out', Different)
    assert report['status'] == 'benchmark_failed'
    assert report['records'][0]['comparison']['passes'] is False


def test_failed_restore_leaves_failure_receipt_no_acceptance(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, _, path = benchmark_setup

    class BrokenRestore(ProfileBackend):
        def restore(self):
            pass

    out = tmp_path / 'out'
    with pytest.raises(RuntimeError, match='restor'):
        run_benchmark(path, out, BrokenRestore)
    assert (out / 'failure.json').exists()
    assert not (out / 'report.json').exists()


def test_failure_after_first_case_cannot_pass_partial_benchmark(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, manifest, path = benchmark_setup
    del manifest['reference'], manifest['comparison']
    manifest['cases'].append({**huygens_case(), 'id': 'broken'})
    path.write_text(json.dumps(manifest))

    class BrokenSecond(ProfileBackend):
        def evaluate(self, case):
            if case['id'] == 'broken':
                raise RuntimeError('native analysis failed')
            return super().evaluate(case)

    out = tmp_path / 'out'
    with pytest.raises(RuntimeError, match='native analysis failed'):
        run_benchmark(path, out, BrokenSecond)
    failure = json.loads((out / 'failure.json').read_text())
    assert failure['status'] == 'failed' and failure['completed_records'] == 1
    assert list((out / 'raw').glob('*.json'))


@pytest.mark.parametrize('status,code', [('benchmark_passed', 0), ('benchmark_failed', 1)])
def test_native_worker_accepts_benchmark_status_contract(tmp_path, capsys, status, code):
    from _lib.native_worker import run_worker

    path = tmp_path / 'worker.py'
    payload = {'report': {'status': status}, 'as_json': True, 'summary': status}
    path.write_text('import os,sys,json\nfrom pathlib import Path\n'
                    f'Path(os.environ["OPTICAL_DESIGN_WORKER_RESULT"]).write_text(json.dumps({payload!r}))\n'
                    f'sys.exit({code})\n')
    assert run_worker(path, []) == code
    assert json.loads(capsys.readouterr().out)['status'] == status


def test_pop_power_reference_is_checked_without_profile_renormalization(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, reference, manifest, path = benchmark_setup
    manifest['cases'] = [pop_case()]
    reference.write_text(json.dumps({'records': [{'model_id': 'lens', 'case_id': 'p9', 'power_w': .7,
                                                 'profiles': {axis: {'x_mm': [-1., 0., 1.], 'intensity': [0., 1., 0.]} for axis in ['x', 'y']}}]}))
    manifest['reference']['sha256'] = hashlib.sha256(reference.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest))
    report = run_benchmark(path, tmp_path / 'out', ProfileBackend)
    comparison = report['records'][0]['comparison']
    assert report['status'] == 'benchmark_failed' and comparison['power']['passes'] is False
    assert comparison['power']['actual_w'] == .8
    assert all(row['passes'] for row in comparison['axes'].values())


def test_failure_receipt_includes_final_source_preservation(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, _, path = benchmark_setup

    class Failure(ProfileBackend):
        def evaluate(self, case):
            raise RuntimeError('broken analysis')

    out = tmp_path / 'out'
    with pytest.raises(RuntimeError):
        run_benchmark(path, out, Failure)
    failure = json.loads((out / 'failure.json').read_text())
    assert failure['source_unchanged'] is True
    assert failure['source_checks'] == {'lens': True}


def test_manifest_disappearance_leaves_failure_receipt(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, _, path = benchmark_setup

    class RemovesManifest(ProfileBackend):
        def evaluate(self, case):
            result = super().evaluate(case)
            path.unlink()
            return result

    out = tmp_path / 'out'
    with pytest.raises(RuntimeError, match='preservation'):
        run_benchmark(path, out, RemovesManifest)
    assert json.loads((out / 'failure.json').read_text())['source_unchanged'] is False


def test_composite_ids_cannot_collide_raw_artifact_names(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, manifest, path = benchmark_setup
    del manifest['reference'], manifest['comparison']
    manifest['models'] = [{**manifest['models'][0], 'id': name} for name in ['a', 'a--b']]
    manifest['cases'] = [{**huygens_case(), 'id': name} for name in ['b--c', 'c']]
    path.write_text(json.dumps(manifest))
    report = run_benchmark(path, tmp_path / 'out', ProfileBackend)
    names = [row['raw_file'] for row in report['records']]
    assert len(set(names)) == 4
    for row in report['records']:
        assert json.loads(Path(row['raw_file']).read_text())['case']['id'] == row['case_id']


@pytest.mark.parametrize('namespace', ['models', 'cases'])
def test_case_insensitive_identifier_collisions_rejected_before_engine(benchmark_setup, tmp_path, namespace):
    from _lib.profile_benchmark import run_benchmark

    _, _, manifest, path = benchmark_setup
    del manifest['reference'], manifest['comparison']
    original = manifest[namespace][0]
    manifest[namespace] = [{**original, 'id': 'stock'}, {**original, 'id': 'STOCK'}]
    path.write_text(json.dumps(manifest))
    opened = []
    with pytest.raises(ValueError, match='duplicate'):
        run_benchmark(path, tmp_path / 'out', lambda p: opened.append(p))
    assert not opened


@pytest.mark.parametrize('mutation', ['rewrite', 'delete'])
def test_all_raw_hashes_rechecked_before_final_receipt(benchmark_setup, tmp_path, mutation):
    from _lib.profile_benchmark import run_benchmark

    _, _, manifest, path = benchmark_setup
    del manifest['reference'], manifest['comparison']
    manifest['cases'].append({**huygens_case(), 'id': 'second'})
    path.write_text(json.dumps(manifest))
    out = tmp_path / 'out'

    class MutatesPreviousArtifact(ProfileBackend):
        def evaluate(self, case):
            result = super().evaluate(case)
            if case['id'] == 'second':
                first = next((out / 'raw').glob('*.json'))
                if mutation == 'rewrite':
                    first.write_text('{"unexpected":"replacement"}')
                else:
                    first.unlink()
            return result

    with pytest.raises(RuntimeError, match='raw.*preservation'):
        run_benchmark(path, out, MutatesPreviousArtifact)
    assert not (out / 'report.json').exists()
    failure = json.loads((out / 'failure.json').read_text())
    assert failure['status'] == 'failed' and failure['source_unchanged'] is True


def test_raw_hash_binds_evaluated_result_before_backend_restoration(benchmark_setup, tmp_path):
    from _lib.profile_benchmark import run_benchmark

    _, _, _, path = benchmark_setup
    out = tmp_path / 'out'

    class MutatesCurrentArtifact(ProfileBackend):
        def restore(self):
            super().restore()
            for raw in (out / 'raw').glob('*.json'):
                raw.write_text('{"unexpected":"replacement"}')

    with pytest.raises(RuntimeError, match='raw.*preservation'):
        run_benchmark(path, out, MutatesCurrentArtifact)
    assert not (out / 'report.json').exists()
    assert json.loads((out / 'failure.json').read_text())['status'] == 'failed'
