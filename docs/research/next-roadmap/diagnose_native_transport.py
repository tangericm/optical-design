"""Host-only read-only probes; never expose configuration overrides as MCP tools."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'skills/optical-design/scripts'))
from _lib.tool_jobs import JobManager, _GATE, _WindowsJob, _hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['manager', 'owned', 'plain'])
    parser.add_argument('--temp', choices=['inherited', 'short', 'long'], default='inherited')
    parser.add_argument('--visible-console-policy', action='store_true')
    args = parser.parse_args()
    started = time.time()
    if args.mode == 'manager':
        model = HERE/'optimize-native/candidate-model.zmx'
        spec = ROOT/'skills/optical-design/assets/optimization-spec.json'
        manager = JobManager(HERE/'diagnostic-manager', [ROOT])
        try:
            identity = manager.start(action='audit', backend='zos', model=str(model),
                                     model_sha256=_hash(model), spec=str(spec), spec_sha256=_hash(spec))['job_id']
            while manager.status(identity)['state'] == 'running':
                time.sleep(.2)
            result = manager.results(identity)
        finally:
            manager.close()
    else:
        environment = dict(os.environ)
        temporary = None
        if args.temp != 'inherited':
            if args.temp == 'short':
                temporary = tempfile.TemporaryDirectory(prefix='opt-')
                scratch = Path(temporary.name)
            else:
                scratch = HERE/'diagnostic-scratch'/('a'*32)/'temp'
                scratch.mkdir(parents=True, exist_ok=True)
            environment.update(TEMP=str(scratch), TMP=str(scratch), TMPDIR=str(scratch))
        argv = [sys.executable, '-u', '-c', _GATE, str(ROOT/'skills/optical-design/scripts/zos.py'), 'check', '--json']
        tree = None
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=environment,
                                   creationflags=0 if args.visible_console_policy else subprocess.CREATE_NO_WINDOW)
        try:
            if args.mode == 'owned':
                tree = _WindowsJob(process.pid)
            stdout, stderr = process.communicate(b'G', timeout=90)
            result = {'exit': process.returncode, 'stdout': stdout.decode('utf-8', errors='replace'),
                      'stderr': stderr.decode('utf-8', errors='replace')}
        finally:
            if tree:
                tree.close()
            if process.poll() is None:
                process.kill()
                process.wait()
            if temporary:
                temporary.cleanup()
    evidence = {'probe': vars(args), 'elapsed_s': time.time()-started, 'result': result}
    name = f"diagnostic-{args.mode}-{args.temp}{'-console' if args.visible_console_policy else ''}.json"
    (HERE/name).write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
