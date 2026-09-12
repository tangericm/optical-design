"""Exercise passed and rejected validation through the actual official MCP client."""
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
ASSETS = ROOT/'skills/optical-design/assets'


async def main():
    params = mcp.StdioServerParameters(command=sys.executable, args=[
        str(ROOT/'skills/optical-design/scripts/server.py'), '--workspace', str(HERE/'mcp'),
        '--input-root', str(ROOT)], env=dict(os.environ))
    evidence = {}
    async with mcp.Client(params, read_timeout_seconds=30) as client:
        for label, spec, accepted in [('pass', ASSETS/'validation-spec.json', True),
                                       ('reject', HERE/'reject-spec.json', False)]:
            request = {'action': 'optimize', 'backend': 'optiland'}
            for key, path in [('model', ASSETS/'portable-singlet.json'),
                              ('spec', ASSETS/'optimization-spec.json'),
                              ('variables', ASSETS/'variables-example.json'), ('validation_spec', spec)]:
                request[key] = str(path)
                request[key+'_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            response = await client.call_tool('start', {'request': request})
            assert not response.is_error, response
            identity = response.structured_content['job_id']
            deadline = time.monotonic()+600
            while time.monotonic() < deadline:
                state = (await client.call_tool('status', {'job_id': identity})).structured_content
                if state['state'] != 'running':
                    break
                await asyncio.sleep(.2)
            result = (await client.call_tool('results', {'job_id': identity})).structured_content
            evidence[label] = {'request': request, 'result': result}
            (HERE/'mcp-validation.json').write_bytes((json.dumps(evidence, indent=2, allow_nan=False)+'\n').encode('utf-8'))
            assert result['state'] == 'completed', result
            assert result['optical_accepted'] is accepted
            assert result['report']['status'] == ('improved' if accepted else 'validation_failed')
            assert result['report']['validation']['evaluations'] == 2
            print(label, result['report']['status'], 'evaluations', result['report']['evaluations'])


if __name__ == '__main__':
    asyncio.run(main())
