"""Actual MCP client: inspect/edit/sensitivity/review and rejected edits, both engines."""
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

import mcp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    HERE = HERE / sys.argv[1]
    HERE.mkdir(exist_ok=False)
ASSETS = ROOT/'skills/optical-design/assets'
SERVER = ROOT/'skills/optical-design/scripts/server.py'


async def exercise():
    params = mcp.StdioServerParameters(command=sys.executable, args=[str(SERVER),
        '--workspace', str(HERE/'mcp-jobs'), '--input-root', str(ASSETS),
        '--input-root', str(HERE)], env=dict(os.environ))
    summary = {}
    async with mcp.Client(params, read_timeout_seconds=120) as client:
        async def job(action, engine, model, **configs):
            request = {'action': action, 'backend': engine}
            for name, path in dict(model=model, **configs).items():
                request[name] = str(path)
                request[name+'_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            stale = dict(request, model_sha256='0'*64)
            assert (await client.call_tool('start', {'request': stale})).is_error
            result = await client.call_tool('start', {'request': request})
            assert not result.is_error, result
            identity = result.structured_content['job_id']
            for _ in range(900):
                state = (await client.call_tool('status', {'job_id': identity})).structured_content
                if state['state'] != 'running':
                    break
                await asyncio.sleep(.2)
            assert state['state'] == 'completed', state
            report = (await client.call_tool('results', {'job_id': identity})).structured_content['report']
            review = await client.call_tool('review', {'job_id': identity})
            assert not review.is_error, review
            summary[engine+'-'+action+('-rejected' if report['status']=='requirements_not_met' else '')] = {
                'job_id': identity, 'status': report['status'], 'optical_accepted': state['optical_accepted'],
                'report': str(Path(state['output'])/'report.json'), 'review': review.structured_content}
            print(engine, action, report['status'], flush=True)
            return report

        perturbations = HERE/'perturbations.json'
        perturbations.write_bytes(json.dumps({'schema': '1', 'parameters': [
            {'surface': 1, 'parameter': 'radius_mm', 'step_mm': .01},
            {'surface': 2, 'parameter': 'thickness_mm', 'step_mm': .01}]}).encode())
        tolerances = HERE/'tolerances.json'
        tolerances.write_bytes(json.dumps({'schema': '1', 'samples': 4, 'seed': 20260913,
            'timeout_s': 300, 'perturbations': [
                {'surface': 1, 'parameter': 'radius_mm', 'distribution': 'uniform', 'half_width_mm': .01}]}).encode())
        spec = ASSETS/'refocus-spec.json'
        for engine, model in [('optiland', ASSETS/'portable-singlet.json'),
                              ('zos', ASSETS/'aspheric-singlet.zmx')]:
            inspection = await job('inspect', engine, model)
            if engine == 'zos':
                assert len(inspection['baseline']['inspection']['surfaces'][1]['asphere_coefficients']) == 8
            refocused = await job('refocus', engine, model, spec=spec)
            assert refocused['status'] == 'improved'
            gap = refocused['candidate']['inspection']['focus_mm']
            edits = HERE/f'edits-{engine}.json'
            edits.write_bytes(json.dumps({'schema': '1', 'changes': [
                {'surface': 2, 'parameter': 'thickness_mm', 'expected_mm': 60, 'value_mm': gap}]}).encode())
            reject = HERE/f'reject-edits-{engine}.json'
            reject.write_bytes(json.dumps({'schema': '1', 'changes': [
                {'surface': 2, 'parameter': 'thickness_mm', 'expected_mm': gap, 'value_mm': 60}]}).encode())
            edited = await job('edit', engine, model, spec=spec, changes=edits)
            assert edited['status'] == 'applied'
            candidate = Path(edited['artifacts']['candidate_model'])
            sensitivity = await job('sensitivity', engine, candidate, spec=spec, perturbations=perturbations)
            assert len(sensitivity['sensitivities']) == 2
            audited = await job('audit', engine, candidate, spec=ASSETS/'validation-spec.json')
            assert audited['status'] == 'requirements_met'
            await job('tolerance', engine, candidate, spec=spec, tolerances=tolerances)
            optimized = await job('optimize', engine, model, spec=ASSETS/'full-workflow/composite-spec.json',
                                  variables=ASSETS/'variables-example.json', validation_spec=ASSETS/'validation-spec.json')
            assert optimized['status'] == 'improved' and optimized['validation']['status'] == 'passed'
            rejected = await job('edit', engine, candidate, spec=spec, changes=reject)
            assert rejected['status'] == 'requirements_not_met' and rejected['candidate'] is None
    (HERE/'mcp-results.json').write_bytes((json.dumps(summary, indent=2)+'\n').encode())


if __name__ == '__main__':
    asyncio.run(exercise())
