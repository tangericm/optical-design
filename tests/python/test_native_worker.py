import json

from _lib.native_worker import run_worker


def test_native_validation_rejection_is_an_optical_outcome(tmp_path, capsys):
    worker = tmp_path / 'rejected.py'
    worker.write_text('import json,os,sys\n'
        'with open(os.environ["OPTICAL_DESIGN_WORKER_RESULT"],"w") as f:\n'
        ' json.dump({"report":{"status":"validation_failed"},"as_json":True,"summary":"rejected"},f)\n'
        'sys.exit(1)\n')
    assert run_worker(worker, []) == 1
    assert json.loads(capsys.readouterr().out)['status'] == 'validation_failed'


def test_native_shutdown_output_cannot_corrupt_json(tmp_path, capsys):
    worker = tmp_path / 'engine.py'
    worker.write_text('''import atexit,json,os
atexit.register(lambda: print('native shutdown message'))
with open(os.environ['OPTICAL_DESIGN_WORKER_RESULT'], 'w') as f:
 json.dump({'report': {'available': True}, 'as_json': True, 'summary': 'ok'}, f)
''')
    assert run_worker(worker, []) == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == {'available': True}
    assert 'native shutdown message' in output.err


def test_worker_without_result_is_failure(tmp_path, capsys):
    worker = tmp_path / 'engine.py'
    worker.write_text('print("engine terminated")')
    assert run_worker(worker, []) == 4
    assert not capsys.readouterr().out


def test_native_crash_after_payload_cannot_emit_or_retain_success(tmp_path, capsys):
    out = tmp_path / 'job'
    out.mkdir()
    report = {'status': 'improved', 'saved_candidate_verified': True}
    (out / 'report.json').write_text(json.dumps(report))
    worker = tmp_path / 'engine.py'
    worker.write_text('''import json,os
with open(os.environ['OPTICAL_DESIGN_WORKER_RESULT'],'w') as f:
 json.dump({'report': {'status':'improved','saved_candidate_verified':True}, 'as_json':True,'summary':'improved'},f)
os._exit(7)
''')
    assert run_worker(worker, ['--out', str(out)]) == 4
    assert not capsys.readouterr().out
    assert json.loads((out / 'report.json').read_text())['status'] == 'failed'
    assert (out / 'failure.json').exists()


def test_malformed_native_payload_is_reported_as_analysis_failure(tmp_path, capsys):
    worker = tmp_path / 'engine.py'
    worker.write_text('''import os
with open(os.environ['OPTICAL_DESIGN_WORKER_RESULT'],'w') as f: f.write('{')
''')
    assert run_worker(worker, []) == 4
    assert 'invalid' in capsys.readouterr().err.lower()


def test_native_crash_clears_benchmark_acceptance_without_erasing_provenance(tmp_path, capsys):
    out = tmp_path / 'job'
    out.mkdir()
    report = {'status': 'benchmark_passed', 'reference_validated': True,
              'saved_candidate_verified': True, 'reference_integrity_verified': True,
              'reference_supplied': True, 'source_unchanged': True}
    (out / 'report.json').write_text(json.dumps(report))
    worker = tmp_path / 'engine.py'
    payload = {'report': report, 'as_json': True, 'summary': 'benchmark_passed'}
    worker.write_text('import json,os\nfrom pathlib import Path\n'
                      f'Path(os.environ["OPTICAL_DESIGN_WORKER_RESULT"]).write_text(json.dumps({payload!r}))\n'
                      'os._exit(7)\n')
    assert run_worker(worker, ['--out', str(out)]) == 4
    assert not capsys.readouterr().out
    result = json.loads((out / 'report.json').read_text())
    assert result['status'] == 'failed'
    assert result['reference_validated'] is False and result['saved_candidate_verified'] is False
    assert result['source_unchanged'] is True and result['reference_integrity_verified'] is True
    assert json.loads((out / 'failure.json').read_text())['stage'] == 'native_process_shutdown'
