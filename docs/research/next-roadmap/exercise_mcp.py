"""Run a real copied-model optical job through the official MCP stdio client."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import mcp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


async def exercise(args):
    params = mcp.StdioServerParameters(command=sys.executable, args=[
        str(ROOT/'skills/optical-design/scripts/server.py'), '--workspace', str(HERE/args.name),
        '--input-root', str(ROOT)], env=dict(os.environ))
    request = {'action': 'audit', 'backend': args.backend}
    for name, path in [('model', args.model), ('spec', args.spec)]:
        source = Path(path).resolve(strict=True)
        request[name] = str(source)
        request[name+'_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    started_at = time.time()
    async with mcp.Client(params, read_timeout_seconds=30) as client:
        listed = await client.list_tools()
        capabilities = (await client.call_tool('capabilities')).structured_content
        started = await client.call_tool('start', {'request': request})
        if started.is_error:
            raise RuntimeError(str(started))
        job_id = started.structured_content['job_id']
        while time.time()-started_at < 600:
            state = (await client.call_tool('status', {'job_id': job_id})).structured_content
            if state['state'] != 'running':
                break
            await asyncio.sleep(.25)
        else:
            await client.call_tool('cancel', {'job_id': job_id})
            raise TimeoutError('MCP optical demonstration timed out')
        outcome = (await client.call_tool('results', {'job_id': job_id})).structured_content
        evidence = {'tools': [t.name for t in listed.tools], 'capabilities': capabilities,
                    'request': request, 'outcome': outcome, 'elapsed_s': time.time()-started_at}
        (HERE/(args.name+'-client.json')).write_bytes((json.dumps(evidence, indent=2, allow_nan=False)+'\n').encode('utf-8'))
        if outcome['state'] != 'completed' or not outcome['optical_accepted']:
            raise RuntimeError(f'MCP job failed acceptance: {outcome}')
        print(json.dumps({'job_id': job_id, 'state': outcome['state'], 'optical_accepted': outcome['optical_accepted']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['optiland', 'zos'], required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--spec', default=str(ROOT/'skills/optical-design/assets/optimization-spec.json'))
    parser.add_argument('--name', required=True)
    asyncio.run(exercise(parser.parse_args()))
