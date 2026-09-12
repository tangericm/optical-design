"""Actual official SDK client/server stdio roundtrip; no native engine needed."""
import asyncio
import hashlib
import sys
from pathlib import Path

import pytest

mcp = pytest.importorskip('mcp')
SERVER = Path(__file__).resolve().parents[2] / 'skills/optical-design/scripts/server.py'


def test_actual_stdio_client_tools_dispatch_and_rejection(tmp_path):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    model, spec = inputs / 'model.json', inputs / 'spec.json'
    model.write_text('{}')
    spec.write_text('{}')  # Invalid optical spec, expected safe CLI failure.
    sha = hashlib.sha256(b'{}').hexdigest()

    async def exercise():
        params = mcp.StdioServerParameters(command=sys.executable, args=[str(SERVER),
            '--workspace', str(tmp_path / 'workspace'), '--input-root', str(inputs)])
        async with mcp.Client(params, read_timeout_seconds=15) as client:
            listed = await client.list_tools()
            assert {tool.name for tool in listed.tools} == {'capabilities', 'start', 'status', 'cancel', 'results'}
            capabilities = await client.call_tool('capabilities')
            assert capabilities.structured_content['max_active_jobs'] == 1
            unknown = await client.call_tool('status', {'job_id': '../other'})
            assert unknown.is_error
            request = {'action': 'audit', 'backend': 'optiland', 'model': str(model), 'model_sha256': sha,
                           'spec': str(spec), 'spec_sha256': sha}
            rejected = await client.call_tool('start', {'request': dict(request, command='whoami')})
            assert rejected.is_error
            rejected = await client.call_tool('start', {'request': dict(request, model_sha256='0'*64)})
            assert rejected.is_error
            started = await client.call_tool('start', {'request': request})
            assert not started.is_error
            identity = started.structured_content['job_id']
            for _ in range(100):
                status = await client.call_tool('status', {'job_id': identity})
                if status.structured_content['state'] != 'running':
                    break
                await asyncio.sleep(.05)
            result = await client.call_tool('results', {'job_id': identity})
            assert result.structured_content['state'] == 'failed'
            assert result.structured_content['optical_accepted'] is False
            assert result.structured_content['report'] is None
            assert Path(result.structured_content['logs']['stderr']).read_text()
            cancelled = await client.call_tool('cancel', {'job_id': identity})
            assert cancelled.structured_content['state'] == 'failed'

    asyncio.run(exercise())
