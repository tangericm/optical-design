import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { assertNoLinks, normalizeSystemPath, statOptional } from './filesystem.mjs';

export function runProcess(command, args, options = {}) {
  return spawnSync(command, args, {
    encoding: 'utf8', shell: false, windowsHide: true, maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }, ...options,
  });
}

export async function doctor(context) {
  const run = context.run ?? runProcess;
  const uv = await run('uv', ['--version'], { timeout: 10000 });
  const uvVersion = uv.status === 0 ? /^uv\s+(\d+\.\d+\.\d+(?:[-+][\w.-]+)?)/.exec(String(uv.stdout).trim())?.[1] : undefined;
  const nodeReady = Number(process.versions.node.split('.')[0]) >= 22;
  return {
    ok: nodeReady && Boolean(uvVersion), operation: 'doctor',
    node: { ready: nodeReady, version: process.versions.node, requirement: '>=22' },
    uv: { ready: Boolean(uvVersion), ...(uvVersion ? { version: uvVersion } : { message: 'uv unavailable or version check failed. Install uv and reopen your terminal.' }) },
    native: 'Native OpticStudio requires Windows, an installed OpticStudio, and a valid API license. Portable demo does not require OpticStudio.',
  };
}

export async function demo(out, context) {
  const output = await normalizeSystemPath(path.resolve(context.cwd, out));
  await assertNoLinks(output);
  if (await statOptional(output)) throw new Error('Demo output already exists. Choose a new directory.');
  const source = await normalizeSystemPath(path.resolve(context.packageRoot, 'skills/optical-design'));
  await assertNoLinks(source);
  for (const relative of ['scripts/resolve.py', 'scripts/design.py', 'scripts/review.py', 'assets/portable-singlet.json', 'assets/refocus-spec.json']) {
    await assertNoLinks(path.join(source, relative));
  }
  const focus = path.join(output, 'quickstart-focus');
  const review = path.join(output, 'quickstart-review');
  // Do not create arbitrary missing ancestors; the requested parent must exist.
  await mkdir(output);
  const run = context.run ?? runProcess;
  async function step(label, args) {
    context.progress?.(`${label}: running (first use may download dependencies)...`);
    const result = await run('uv', args, { cwd: output });
    const logBase = path.join(output, label.toLowerCase());
    for (const stream of ['stdout', 'stderr']) {
      const log = `${logBase}.${stream}.log`;
      await assertNoLinks(log);
      await writeFile(log, String(result[stream] ?? '').slice(-1024 * 1024), { flag: 'wx' });
    }
    if (result.error || result.status !== 0) throw new Error(`${label} failed (${result.error?.code ?? `exit ${result.status ?? 'unknown'}`}). See ${logBase}.stderr.log; partial evidence retained at ${output}`);
    return result;
  }
  const calculator = await step('Calculator', ['run', path.join(source, 'scripts/resolve.py'), 'airy', '--wavelength-um', '0.55', '--fnum', '4', '--json']);
  await step('Refocus', ['run', '--python', '3.11', '--with', 'optiland==0.6.2', path.join(source, 'scripts/design.py'), 'refocus', '--backend', 'optiland', '--model', path.join(source, 'assets/portable-singlet.json'), '--spec', path.join(source, 'assets/refocus-spec.json'), '--out', focus, '--json']);
  const reportPath = path.join(focus, 'report.json');
  await assertNoLinks(reportPath);
  const report = JSON.parse(await readFile(reportPath, 'utf8'));
  if (report.status !== 'improved' || report.saved_candidate_verified !== true) throw new Error(`Optical acceptance or saved candidate verification failed. Inspect ${reportPath}`);
  await step('Review', ['run', path.join(source, 'scripts/review.py'), '--report', reportPath, '--out', review, '--json']);
  const html = path.join(review, 'report.html');
  await assertNoLinks(html);
  if (!(await statOptional(html))?.isFile()) throw new Error('Review failed: report.html is missing');
  let calculation;
  try { calculation = JSON.parse(calculator.stdout); } catch { throw new Error('Calculator failed: invalid JSON output'); }
  return { ok: true, operation: 'demo', output, calculation, status: report.status, saved_candidate_verified: true, report: reportPath, review: html };
}
