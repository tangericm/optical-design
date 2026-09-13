"""Retain paired control/expanded validation runs on a predeclared synthetic model.

Run with pinned Optiland/MCP dependencies for --backend optiland, or ZOSPy/pythonnet
for --backend zos. This driver refuses to overwrite its result record.
"""
import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASSETS = ROOT/'skills/optical-design/assets'
EXAMPLE = ASSETS/'field-validation'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_bytes((json.dumps(data, indent=2, allow_nan=False)+'\n').encode('utf-8'))


async def portable(record):
    import mcp
    params = mcp.StdioServerParameters(command=sys.executable,
        args=[str(ROOT/'skills/optical-design/scripts/server.py'), '--workspace', str(HERE/'mcp'),
              '--input-root', str(ROOT)], env=dict(os.environ))
    evidence = {}
    async with mcp.Client(params, read_timeout_seconds=30) as client:
        for label in ('control', 'validation'):
            request = dict(action='optimize', backend='optiland')
            for key, path in [('model', EXAMPLE/'portable.json'), ('spec', EXAMPLE/'search.json'),
                ('variables', ASSETS/'variables-example.json'), ('validation_spec', EXAMPLE/f'{label}.json')]:
                request[key], request[key+'_sha256'] = str(path), digest(path)
            response = await client.call_tool('start', {'request': request})
            if response.is_error:
                raise RuntimeError(response)
            identity = response.structured_content['job_id']
            deadline = time.monotonic()+660
            while time.monotonic() < deadline:
                state = (await client.call_tool('status', {'job_id': identity})).structured_content
                if state['state'] != 'running':
                    break
                await asyncio.sleep(.2)
            else:
                await client.call_tool('cancel', {'job_id': identity})
                raise TimeoutError('MCP benchmark deadline')
            result = (await client.call_tool('results', {'job_id': identity})).structured_content
            evidence[label] = dict(request=request, result=result)
            write(record, evidence)
            print(label, result['state'], result.get('optical_accepted'), flush=True)
            if result['state'] != 'completed':
                raise RuntimeError(result.get('error'))


def native(record):
    evidence = {}
    for label in ('control', 'validation'):
        out = record.parent/f'native-{label}'
        args = [sys.executable, str(ROOT/'skills/optical-design/scripts/design.py'), 'optimize',
            '--backend', 'zos', '--model', str(EXAMPLE/'native.zmx'), '--spec', str(EXAMPLE/'search.json'),
            '--variables', str(ASSETS/'variables-example.json'), '--validation-spec', str(EXAMPLE/f'{label}.json'),
            '--out', str(out), '--json']
        result = subprocess.run(args, capture_output=True, timeout=660)
        (record.parent/f'native-{label}-stdout.json').write_bytes(result.stdout)
        (record.parent/f'native-{label}-stderr.log').write_bytes(result.stderr)
        evidence[label] = dict(argv=args, returncode=result.returncode, output=str(out))
        write(record, evidence)
        print(label, 'exit', result.returncode, flush=True)
        if result.returncode not in (0, 1):
            raise RuntimeError('Native execution failed; inspect retained logs/failure receipt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', required=True, choices=['optiland', 'zos'])
    args = parser.parse_args()
    record = (HERE/'corrected-native/zos-runs.json' if args.backend == 'zos'
              else HERE/f'{args.backend}-runs.json')
    if record.exists():
        raise FileExistsError(record)
    record.parent.mkdir(exist_ok=True)
    manifest = json.loads((HERE/'predeclared-inputs.json').read_text())
    for path, expected in manifest['inputs_sha256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError(f'Predeclared input changed: {path}')
    if args.backend == 'zos':
        native(record)
    else:
        asyncio.run(portable(record))


if __name__ == '__main__':
    main()
