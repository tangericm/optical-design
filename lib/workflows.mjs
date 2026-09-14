import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { assertNoLinks, contained, normalizeSystemPath, statOptional } from './filesystem.mjs';

export function runProcess(command, args, options = {}) {
  return spawnSync(command, args, {
    encoding: 'utf8', shell: false, windowsHide: true, maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }, ...options,
  });
}

export async function doctor(context, { engineCheck = false } = {}) {
  const run = context.run ?? runProcess;
  const uv = await run('uv', ['--version'], { timeout: 10000 });
  const uvVersion = uv.status === 0 ? /^uv\s+(\d+\.\d+\.\d+(?:[-+][\w.-]+)?)/.exec(String(uv.stdout).trim())?.[1] : undefined;
  const nodeReady = Number(process.versions.node.split('.')[0]) >= 22;
  const portable = { status: 'untested', message: 'Optiland has not been imported or exercised. Use doctor --engine-check to test it (may download Python and pinned dependencies).' };
  if (engineCheck && uvVersion) {
    context.progress?.('Checking Optiland 0.6.2 (may download Python and dependencies)...');
    const result = await run('uv', ['run', '--python', '3.11', '--with', 'optiland==0.6.2', 'python', '-B', '-c',
      'from importlib.metadata import version; from optiland.optic import Optic; lens = Optic(); lens.add_surface(index=0, radius=float("inf"), thickness=float("inf")); lens.add_surface(index=1, radius=50, thickness=5, material="N-BK7"); lens.add_surface(index=2, radius=-50, thickness=50); lens.add_surface(index=3); lens.set_aperture(aperture_type="EPD", value=10); lens.add_wavelength(value=0.55, is_primary=True); assert version("optiland") == "0.6.2"; assert 40 < float(lens.paraxial.f2()) < 60; print("optical-design engine check passed")'], { timeout: 300000 });
    portable.status = result.status === 0 && String(result.stdout).includes('optical-design engine check passed') ? 'ready' : 'failed';
    portable.message = portable.status === 'ready' ? 'Optiland 0.6.2 imported and a paraxial singlet calculation passed.' : 'Optiland check failed. Run the walkthrough for retained diagnostic logs.';
  } else if (engineCheck) {
    portable.status = 'failed';
    portable.message = 'Cannot check Optiland because uv is unavailable.';
  }
  return {
    ok: nodeReady && Boolean(uvVersion) && portable.status !== 'failed', operation: 'doctor',
    node: { ready: nodeReady, version: process.versions.node, requirement: '>=22' },
    uv: { ready: Boolean(uvVersion), ...(uvVersion ? { version: uvVersion } : { message: 'uv unavailable or version check failed. Install uv and reopen your terminal.' }) },
    portable,
    native: 'Native OpticStudio: untested. Requires Windows, installed OpticStudio, and a valid API license. Run the installed scripts/zos.py check --json for a separate native probe.',
  };
}

export async function demo(out, context) {
  const output = await normalizeSystemPath(path.resolve(context.cwd, out));
  await assertNoLinks(output);
  if (await statOptional(output)) throw new Error('Demo output already exists. Choose a new directory.');
  const source = await normalizeSystemPath(path.resolve(context.packageRoot, 'skills/optical-design'));
  if (output === source || contained(source, output)) throw new Error('Output must be outside the bundled skill directory.');
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

export async function walkthrough(out, context) {
  const output = await normalizeSystemPath(path.resolve(context.cwd, out));
  const source = await normalizeSystemPath(path.resolve(context.packageRoot, 'skills/optical-design'));
  if (output === source || contained(source, output)) throw new Error('Output must be outside the bundled skill directory.');
  await assertNoLinks(output);
  if (await statOptional(output)) throw new Error('Walkthrough output already exists. Choose a new directory.');
  const script = path.join(source, 'scripts/walkthrough.py');
  await assertNoLinks(script);
  context.progress?.('Walkthrough: running (first use may download Python and pinned dependencies)...');
  const result = await (context.run ?? runProcess)('uv', ['run', '--python', '3.11', script, '--out', output, '--json'], { cwd: context.cwd });
  // Python owns creation of the new output directory and preserves partial work.
  if ((await statOptional(output))?.isDirectory()) {
    for (const stream of ['stdout', 'stderr']) {
      const log = path.join(output, `walkthrough.${stream}.log`);
      await assertNoLinks(log);
      await writeFile(log, String(result[stream] ?? '').slice(-1024 * 1024), { flag: 'wx' });
    }
  }
  if (result.error || result.status !== 0) throw new Error(`Walkthrough failed (${result.error?.code ?? `exit ${result.status ?? 'unknown'}`}). Partial evidence, if created, is at ${output}. ${String(result.stderr ?? '').slice(-2000)}`);
  let evidence;
  try { evidence = JSON.parse(result.stdout).results; } catch { throw new Error('Walkthrough returned invalid JSON.'); }
  for (const name of ['review', 'summary', 'candidate']) {
    const filename = evidence?.[name];
    if (typeof filename !== 'string' || !path.isAbsolute(filename) || !contained(output, filename)) throw new Error(`Walkthrough returned an invalid ${name} path.`);
    await assertNoLinks(filename);
    if (!(await statOptional(filename))?.isFile()) throw new Error(`Walkthrough ${name} is missing.`);
  }
  return { ok: true, operation: 'walkthrough', output, ...evidence };
}
