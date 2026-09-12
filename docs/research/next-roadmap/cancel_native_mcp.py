"""Cancel one live owned native tolerance job, preserving unrelated processes."""
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import mcp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def optical_processes():
    command = "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'OpticStudio|Zemax' } | Select-Object Name,ProcessId,ParentProcessId | ConvertTo-Json -Compress"
    result = subprocess.run(['powershell', '-NoProfile', '-Command', command], capture_output=True,
                            text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    rows = json.loads(result.stdout) if result.stdout.strip() else []
    return rows if isinstance(rows, list) else [rows]


async def main():
    before = optical_processes()
    unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(180)'],
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    params = mcp.StdioServerParameters(command=sys.executable, args=[
        str(ROOT/'skills/optical-design/scripts/server.py'), '--workspace', str(HERE/'mcp-native-cancel'),
        '--input-root', str(ROOT)], env=dict(os.environ))
    request = {'action': 'tolerance', 'backend': 'zos'}
    for key, path in [('model', HERE/'optimize-native/candidate-model.zmx'),
                      ('spec', ROOT/'skills/optical-design/assets/compensation-spec.json'),
                      ('tolerances', ROOT/'skills/optical-design/assets/compensated-tolerances-example.json')]:
        request[key] = str(path)
        request[key+'_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    started_at = time.time()
    try:
        async with mcp.Client(params, read_timeout_seconds=30) as client:
            started = await client.call_tool('start', {'request': request})
            if started.is_error:
                raise RuntimeError(str(started))
            identity = started.structured_content['job_id']
            output = Path(started.structured_content['output'])
            live = []
            for _ in range(120):
                state = (await client.call_tool('status', {'job_id': identity})).structured_content
                if state['state'] != 'running':
                    raise RuntimeError(f'job ended before cancellation probe: {state}')
                if (output/'nominal.json').exists():
                    live = optical_processes()
                    if live:
                        break
                await asyncio.sleep(.25)
            else:
                await client.call_tool('cancel', {'job_id': identity})
                raise TimeoutError('native job did not produce nominal evidence in time')
            cancelled = (await client.call_tool('cancel', {'job_id': identity})).structured_content
            result = (await client.call_tool('results', {'job_id': identity})).structured_content
            await asyncio.sleep(.5)
            after = optical_processes()
            baseline_ids = {p['ProcessId'] for p in before}
            new_ids = {p['ProcessId'] for p in live} - baseline_ids
            remaining = new_ids & {p['ProcessId'] for p in after}
            evidence = {'native_job_started': bool(new_ids), 'nominal_evidence_before_cancel': True,
                        'before_native_processes': before, 'live_native_processes': live,
                        'after_native_processes': after, 'owned_native_pids_remaining': sorted(remaining),
                        'unrelated_process_alive': unrelated.poll() is None,
                        'cancel': cancelled, 'results': result, 'elapsed_s': time.time()-started_at,
                        'source_unchanged': hashlib.sha256(Path(request['model']).read_bytes()).hexdigest() == request['model_sha256']}
            (HERE/'mcp-native-cancel-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
            assert result['state'] == 'cancelled' and result['report'] is None and not result['optical_accepted']
            assert evidence['source_unchanged'] and evidence['unrelated_process_alive'] and not remaining
            print(json.dumps(evidence, indent=2))
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


if __name__ == '__main__':
    asyncio.run(main())
