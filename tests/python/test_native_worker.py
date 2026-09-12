import json

from _lib.native_worker import run_worker


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
