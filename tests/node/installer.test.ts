import { afterEach, beforeEach, describe, expect, test } from 'vitest';
import { mkdtemp, mkdir, writeFile, readFile, readdir, lstat, symlink, rm, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const repository = path.resolve(import.meta.dirname, '../..');
let root: string;
let context: any;
let api: any;
beforeEach(async () => {
  root = await realpath(await mkdtemp(path.join(tmpdir(), 'optical-installer-')));
  context = { packageRoot: path.join(root, 'package'), cwd: path.join(root, 'project'), home: path.join(root, 'home') };
  await Promise.all(Object.values(context).map((p: any) => mkdir(p, { recursive: true })));
  await mkdir(path.join(context.packageRoot, 'skills/optical-design/scripts'), { recursive: true });
  await writeFile(path.join(context.packageRoot, 'package.json'), JSON.stringify({ name: 'optical-design', version: '1.1.0' }));
  await writeFile(path.join(context.packageRoot, 'skills/optical-design/SKILL.md'), 'original skill');
  await writeFile(path.join(context.packageRoot, 'skills/optical-design/scripts/tool.py'), 'print(1)');
});
afterEach(async () => { await rm(root, { recursive: true, force: true }); });

test('CLI executable exists and gives useful help without installing', async () => {
  const result = spawnSync(process.execPath, [path.join(repository, 'bin/optical-design.mjs'), '--help'], { encoding: 'utf8', cwd: context.cwd });
  expect(result.status).toBe(0);
  expect(result.stdout).toContain('install --agent');
  expect(await readdir(context.cwd)).toEqual([]);
});

describe('managed installation', () => {
  beforeEach(async () => { api = await import('../../lib/installer.mjs'); });
  test('installed Airy calculator leaves no bytecode and permits update then uninstall', async () => {
    const source = path.join(context.packageRoot, 'skills/optical-design/scripts');
    await mkdir(path.join(source, '_lib'));
    for (const name of ['resolve.py', '_lib/__init__.py', '_lib/cli.py', '_lib/optics.py']) {
      await writeFile(path.join(source, name), await readFile(path.join(repository, 'skills/optical-design/scripts', name)));
    }
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const env = { ...process.env };
    delete env.PYTHONDONTWRITEBYTECODE;
    const calculation = spawnSync('uv', ['run', '--python', '3.11', path.join(destination, 'scripts/resolve.py'), 'airy', '--wavelength-um', '0.55', '--fnum', '4', '--json'], { cwd: context.cwd, env, encoding: 'utf8' });
    expect(calculation.status, calculation.stderr).toBe(0);
    expect(JSON.parse(calculation.stdout).results.airy_radius_um).toBeCloseTo(2.684);
    expect(await readdir(path.join(destination, 'scripts/_lib'))).not.toContain('__pycache__');
    await api.manage('update', { agent: 'codex' }, context);
    await api.manage('uninstall', { agent: 'codex' }, context);
    await expect(lstat(destination)).rejects.toMatchObject({ code: 'ENOENT' });
  });
  test.each(['update', 'uninstall'])('accepts actual CPython caches during %s but preserves project outputs', async operation => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const env = { ...process.env };
    delete env.PYTHONDONTWRITEBYTECODE;
    const result = spawnSync('uv', ['run', '--python', '3.11', 'python', '-c', 'import tool'], { cwd: path.join(destination, 'scripts'), env, encoding: 'utf8' });
    expect(result.status, result.stderr).toBe(0);
    expect((await readdir(path.join(destination, 'scripts/__pycache__'))).length).toBeGreaterThan(0);
    await writeFile(path.join(context.cwd, 'user-result.json'), 'keep my result');
    await api.manage(operation, { agent: 'codex' }, context);
    expect(await readFile(path.join(context.cwd, 'user-result.json'), 'utf8')).toBe('keep my result');
  });
  test.each(['edited-source', 'unknown-file', 'fake-pyc', 'linked-cache'])('preserves suspicious cache content: %s', async change => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const cache = path.join(destination, 'scripts/__pycache__');
    if (change === 'linked-cache') {
      await writeFile(path.join(context.home, 'keep'), 'outside');
      await symlink(context.home, cache, process.platform === 'win32' ? 'junction' : 'dir');
    } else {
      const env = { ...process.env };
      delete env.PYTHONDONTWRITEBYTECODE;
      const result = spawnSync('uv', ['run', '--python', '3.11', 'python', '-c', 'import tool'], { cwd: path.join(destination, 'scripts'), env, encoding: 'utf8' });
      expect(result.status, result.stderr).toBe(0);
      if (change === 'edited-source') await writeFile(path.join(destination, 'scripts/tool.py'), 'user edits');
      if (change === 'unknown-file') await writeFile(path.join(cache, 'notes.txt'), 'user notes');
      if (change === 'fake-pyc') await writeFile(path.join(cache, 'tool.cpython-312.pyc'), 'user notes');
    }
    for (const operation of ['update', 'uninstall']) await expect(api.manage(operation, { agent: 'codex' }, context)).rejects.toThrow(/changed|edited|symlink|symbolic/i);
    expect((await lstat(destination)).isDirectory()).toBe(true);
    if (change === 'linked-cache') expect(await readFile(path.join(context.home, 'keep'), 'utf8')).toBe('outside');
  });
  test('retains one intact backup and safely previews/prunes backups while preserving changes', async () => {
    await api.manage('install', { agent: 'codex' }, context);
    const first = await api.manage('update', { agent: 'codex' }, context);
    const second = await api.manage('update', { agent: 'codex' }, context);
    await expect(lstat(first.backup)).rejects.toMatchObject({ code: 'ENOENT' });
    await writeFile(path.join(second.backup, 'notes.txt'), 'keep notes');
    const third = await api.manage('update', { agent: 'codex' }, context);
    expect(third.preservedBackups).toContain(second.backup);
    const preview = await api.manage('prune-backups', { agent: 'codex' }, context);
    expect(preview.dryRun).toBe(true);
    expect(preview.removable).toEqual([third.backup]);
    expect((await lstat(third.backup)).isDirectory()).toBe(true);
    await api.manage('uninstall', { agent: 'codex' }, context);
    const cleaned = await api.manage('prune-backups', { agent: 'codex', apply: true }, context);
    expect(cleaned.removed).toEqual([third.backup]);
    expect(await readFile(path.join(second.backup, 'notes.txt'), 'utf8')).toBe('keep notes');
  });
  test('backup cleanup preserves linked and legacy backups', async () => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const previous = await api.manage('update', { agent: 'codex' }, context);
    const receiptPath = path.join(previous.backup, '.optical-design-install.json');
    const receipt = JSON.parse(await readFile(receiptPath, 'utf8'));
    delete receipt.installationDestination;
    await writeFile(receiptPath, JSON.stringify(receipt));
    const linked = path.join(path.dirname(destination), '.optical-design.backup-12345678-1234-4123-8123-123456789012');
    await symlink(context.home, linked, process.platform === 'win32' ? 'junction' : 'dir');
    await writeFile(path.join(context.home, 'keep.txt'), 'keep');
    const result = await api.manage('prune-backups', { agent: 'codex', apply: true }, context);
    expect(result.removed).toEqual([]);
    expect(result.preserved).toContain(previous.backup);
    expect(result.preserved).toContain(linked);
    expect(await readFile(path.join(context.home, 'keep.txt'), 'utf8')).toBe('keep');
  });
  test.each(['update', 'uninstall'])('preserves newly added __proto__ file before %s', async operation => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    await writeFile(path.join(destination, '__proto__'), 'user notes');
    await expect(api.manage(operation, { agent: 'codex' }, context)).rejects.toThrow(/changed|edited/i);
    expect(await readFile(path.join(destination, '__proto__'), 'utf8')).toBe('user notes');
    expect(await readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe('original skill');
  });
  test.skipIf(process.platform !== 'darwin')('accepts verified macOS temporary aliases without allowing source overlap', async () => {
    const aliasRoot = root.replace(/^\/private\/var\//, '/var/').replace(/^\/private\/tmp\//, '/tmp/');
    const result = await api.manage('install', { agent: 'codex' }, { ...context, cwd: path.join(aliasRoot, 'project') });
    expect(result.destination).toBe(path.join(context.cwd, '.agents/skills/optical-design'));
    const source = path.join(context.packageRoot, 'skills/optical-design');
    const aliasSource = source.replace(/^\/private\/var\//, '/var/').replace(/^\/private\/tmp\//, '/tmp/');
    await expect(api.manage('install', { agent: 'codex' }, { ...context, cwd: aliasSource })).rejects.toThrow(/overlap|inside/i);
  });
  test.each([
    ['claude-code', '.claude/skills', '.claude/skills'],
    ['codex', '.agents/skills', '.agents/skills'],
    ['cursor', '.cursor/skills', '.cursor/skills'],
    ['opencode', '.opencode/skills', '.config/opencode/skills'],
    ['hermes', '.hermes/skills', '.hermes/skills'],
  ])('copies the bundle into correct project and global %s locations', async (agent, project, global) => {
    for (const globalScope of [false, true]) {
      const result = await api.manage('install', { agent, global: globalScope }, context);
      expect(result.destination).toBe(path.join(globalScope ? context.home : context.cwd, globalScope ? global : project, 'optical-design'));
      expect(await readFile(path.join(result.destination, 'SKILL.md'), 'utf8')).toBe('original skill');
      expect(result.version).toBe('1.1.0');
      const manifest = JSON.parse(await readFile(path.join(result.destination, '.optical-design-install.json'), 'utf8'));
      expect(manifest.files['SKILL.md']).toMatch(/^[a-f0-9]{64}$/);
      await expect(api.manage('install', { agent, global: globalScope }, context)).rejects.toThrow(/already|exists/i);
    }
  });
  test('refuses unmanaged directories without changing their content', async () => {
    const dest = path.join(context.cwd, '.agents/skills/optical-design');
    await mkdir(dest, { recursive: true });
    await writeFile(path.join(dest, 'keep.txt'), 'mine');
    for (const operation of ['install', 'update', 'uninstall']) {
      await expect(api.manage(operation, { agent: 'codex' }, context)).rejects.toThrow(/unmanaged|exists/i);
    }
    expect(await readFile(path.join(dest, 'keep.txt'), 'utf8')).toBe('mine');
  });
  test.each(['edit', 'new-file', 'new-directory', 'missing-file', 'bad-manifest'])('preserves user changes: %s', async change => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    if (change === 'edit') await writeFile(path.join(destination, 'SKILL.md'), 'user edits');
    if (change === 'new-file') await writeFile(path.join(destination, 'mine.txt'), 'mine');
    if (change === 'new-directory') await mkdir(path.join(destination, 'mine'));
    if (change === 'missing-file') await rm(path.join(destination, 'SKILL.md'));
    if (change === 'bad-manifest') await writeFile(path.join(destination, '.optical-design-install.json'), '{');
    const before = await readdir(destination);
    for (const operation of ['update', 'uninstall']) await expect(api.manage(operation, { agent: 'codex' }, context)).rejects.toThrow(/changed|edited|manifest|intact/i);
    expect(await readdir(destination)).toEqual(before);
  });
  test('update preserves an intact backup and uninstall preserves neighboring files', async () => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    await writeFile(path.join(context.packageRoot, 'skills/optical-design/SKILL.md'), 'new skill');
    const updated = await api.manage('update', { agent: 'codex' }, context);
    expect(await readFile(path.join(updated.backup, 'SKILL.md'), 'utf8')).toBe('original skill');
    expect(await readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe('new skill');
    await writeFile(path.join(path.dirname(destination), 'neighbor'), 'keep');
    await api.manage('uninstall', { agent: 'codex' }, context);
    await expect(lstat(destination)).rejects.toMatchObject({ code: 'ENOENT' });
    expect(await readFile(path.join(path.dirname(destination), 'neighbor'), 'utf8')).toBe('keep');
    expect(await readFile(path.join(updated.backup, 'SKILL.md'), 'utf8')).toBe('original skill');
  });
  test('rejects traversal agents and overlapping bundle destinations', async () => {
    await expect(api.manage('install', { agent: '../escape' }, context)).rejects.toThrow(/agent/i);
    await expect(api.manage('install', { agent: 'codex' }, { ...context, cwd: path.join(context.packageRoot, 'skills/optical-design') })).rejects.toThrow(/overlap|inside/i);
  });
  test('rejects destination hierarchy and source directory symlinks', async () => {
    const outside = path.join(root, 'outside');
    await mkdir(outside);
    await symlink(outside, path.join(context.cwd, '.agents'), process.platform === 'win32' ? 'junction' : 'dir');
    await expect(api.manage('install', { agent: 'codex' }, context)).rejects.toThrow(/symlink|symbolic/i);
    expect(await readdir(outside)).toEqual([]);
    await symlink(outside, path.join(context.packageRoot, 'skills/optical-design/linked'), process.platform === 'win32' ? 'junction' : 'dir');
    await expect(api.manage('install', { agent: 'cursor' }, context)).rejects.toThrow(/symlink|symbolic/i);
  });
  test('rejects symlinks added to managed installations', async () => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    await symlink(context.home, path.join(destination, 'linked'), process.platform === 'win32' ? 'junction' : 'dir');
    await expect(api.manage('uninstall', { agent: 'codex' }, context)).rejects.toThrow(/symlink|symbolic/i);
  });
  test('preserves the installation and existing lock when another operation holds it', async () => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const lock = path.join(path.dirname(destination), '.optical-design.lock');
    await mkdir(lock);
    await expect(api.manage('uninstall', { agent: 'codex' }, context)).rejects.toThrow(/lock/i);
    expect((await lstat(lock)).isDirectory()).toBe(true);
    expect(await readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe('original skill');
  });
  test('malicious ownership paths cannot authorize deletion outside the installation', async () => {
    const { destination } = await api.manage('install', { agent: 'codex' }, context);
    const receipt = path.join(destination, '.optical-design-install.json');
    const manifest = JSON.parse(await readFile(receipt, 'utf8'));
    manifest.files['../../outside'] = manifest.files['SKILL.md'];
    await writeFile(receipt, JSON.stringify(manifest));
    await expect(api.manage('uninstall', { agent: 'codex' }, context)).rejects.toThrow(/changed|edited/i);
    expect(await readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe('original skill');
  });
});

describe('CLI and execution', () => {
  beforeEach(async () => { api = await import('../../lib/cli.mjs'); });
  test.each([['install'], ['install', '--agent', '../escape'], ['doctor', '--global'], ['demo', '--out'], ['install', '--agent', 'codex', '--agent', 'cursor'], ['--version', 'extra']])('rejects invalid arguments %j', async (...args) => {
    await expect(api.execute(args, { ...context, isTTY: false })).rejects.toThrow();
  });
  test('noninteractive JSON CLI errors have nonzero status and parseable output', () => {
    const result = spawnSync(process.execPath, [path.join(repository, 'bin/optical-design.mjs'), 'install', '--json'], { encoding: 'utf8', cwd: context.cwd });
    expect(result.status).toBe(1);
    expect(JSON.parse(result.stdout).ok).toBe(false);
    expect(result.stderr).toBe('');
  });
  test('doctor reports missing uv as failure without dumping process output', async () => {
    const result = await api.execute(['doctor'], { ...context, run: () => ({ status: 1, stdout: 'secret', stderr: 'secret' }) });
    expect(result.ok).toBe(false);
    expect(JSON.stringify(result)).not.toContain('secret');
    expect(JSON.stringify(result)).toContain('OpticStudio');
  });
  test('doctor distinguishes setup from engine readiness and requires explicit engine probe', async () => {
    const calls: any[] = [];
    const run = (command: string, args: string[]) => { calls.push([command, args]); return { status: 0, stdout: calls.length === 1 ? 'uv 0.8.0' : 'optical-design engine check passed' }; };
    const setup = await api.execute(['doctor'], { ...context, run });
    expect(setup.ok).toBe(true);
    expect(setup.portable.status).toBe('untested');
    expect(setup.native).toContain('untested');
    expect(calls).toHaveLength(1);
    calls.length = 0;
    const checked = await api.execute(['doctor', '--engine-check'], { ...context, run });
    expect(checked.portable.status).toBe('ready');
    expect(calls).toHaveLength(2);
    expect(calls[1][1]).toContain('optiland==0.6.2');
  });
  test('doctor explicit engine failure makes doctor fail', async () => {
    let calls = 0;
    const result = await api.execute(['doctor', '--engine-check'], { ...context, run: () => ++calls === 1 ? { status: 0, stdout: 'uv 0.8.0' } : { status: 1, stdout: '', stderr: 'private diagnostic' } });
    expect(result.ok).toBe(false);
    expect(result.portable.status).toBe('failed');
    expect(JSON.stringify(result)).not.toContain('private diagnostic');
  });
  test('walkthrough resolves bundled script paths and validates returned evidence files', async () => {
    const output = path.join(context.cwd, 'walkthrough');
    const calls: any[] = [];
    const run = async (command: string, args: string[]) => {
      calls.push([command, args]);
      await mkdir(output);
      const results: Record<string, string> = {};
      for (const [name, file] of [['review', 'review.html'], ['summary', 'summary.json'], ['candidate', 'candidate.json']]) {
        results[name] = path.join(output, file);
        await writeFile(results[name], 'evidence');
      }
      return { status: 0, stdout: JSON.stringify({ results }), stderr: '' };
    };
    const result = await api.execute(['walkthrough', '--out', 'walkthrough'], { ...context, run });
    expect(result.ok).toBe(true);
    expect(result.review).toBe(path.join(output, 'review.html'));
    expect(calls[0][1]).toContain(path.join(context.packageRoot, 'skills/optical-design/scripts/walkthrough.py'));
    expect(await readFile(path.join(output, 'walkthrough.stderr.log'), 'utf8')).toBe('');
    await expect(api.execute(['walkthrough', '--out', output], context)).rejects.toThrow(/exists/i);
  });
  test.each(['demo', 'walkthrough'])('%s rejects output inside the skill', async command => {
    await expect(api.execute([command, '--out', path.join(context.packageRoot, 'skills/optical-design/output')], context)).rejects.toThrow(/outside/i);
  });
  test('demo rejects existing output and propagates process failure', async () => {
    await expect(api.execute(['demo', '--out', context.cwd], context)).rejects.toThrow(/exist/i);
    await expect(api.execute(['demo', '--out', 'new-demo'], { ...context, run: () => ({ status: 3, stdout: '', stderr: '' }) })).rejects.toThrow(/failed|exit/i);
  });
  test('demo rejects linked script inputs before creating output or spawning uv', async () => {
    const scripts = path.join(context.packageRoot, 'skills/optical-design/scripts');
    await rm(scripts, { recursive: true });
    await symlink(context.home, scripts, process.platform === 'win32' ? 'junction' : 'dir');
    let calls = 0;
    await expect(api.execute(['demo', '--out', 'linked-demo'], { ...context, run: () => { calls++; return { status: 1 }; } })).rejects.toThrow(/symlink|symbolic/i);
    expect(calls).toBe(0);
    expect(await readdir(context.cwd)).toEqual([]);
  });
  test.each([['failed', true], ['improved', false]])('demo refuses unsuccessful optical evidence: %s %s', async (status, verified) => {
    const out = path.join(context.cwd, 'new-demo');
    let calls = 0;
    const run = async () => {
      if (++calls === 2) {
        await mkdir(path.join(out, 'quickstart-focus'));
        await writeFile(path.join(out, 'quickstart-focus/report.json'), JSON.stringify({ status, saved_candidate_verified: verified }));
      }
      return { status: 0, stdout: '{}', stderr: '' };
    };
    await expect(api.execute(['demo', '--out', out], { ...context, run })).rejects.toThrow(/acceptance|verification/i);
    expect(calls).toBe(2);
  });
  test('demo uses absolute bundled paths and requires both optical acceptance checks', async () => {
    const out = path.join(context.cwd, 'new-demo');
    const calls: any[] = [];
    const run = async (command: string, args: string[]) => {
      calls.push([command, args]);
      if (calls.length === 2) {
        await mkdir(path.join(out, 'quickstart-focus'));
        await writeFile(path.join(out, 'quickstart-focus/report.json'), JSON.stringify({ status: 'improved', saved_candidate_verified: true }));
      }
      if (calls.length === 3) {
        await mkdir(path.join(out, 'quickstart-review'));
        await writeFile(path.join(out, 'quickstart-review/report.html'), '<html>review</html>');
      }
      return { status: 0, stdout: '{}', stderr: '' };
    };
    const result = await api.execute(['demo', '--out', out], { ...context, run });
    expect(result.ok).toBe(true);
    expect(calls).toHaveLength(3);
    expect(calls[1][1]).toContain('optiland==0.6.2');
    expect(calls[0][1]).toContain(path.join(context.packageRoot, 'skills/optical-design/scripts/resolve.py'));
    expect(calls[1][1]).toContain(path.join(context.packageRoot, 'skills/optical-design/assets/portable-singlet.json'));
    expect(result.review).toBe(path.join(out, 'quickstart-review/report.html'));
  });
  test('failed demo preserves actionable engine logs and reports progress', async () => {
    const out = path.join(context.cwd, 'failed-demo');
    const progress: string[] = [];
    const run = async () => ({ status: 1, stdout: '', stderr: 'Dependency download failed: connection unavailable' });
    await expect(api.execute(['demo', '--out', out], { ...context, run, progress: (message: string) => progress.push(message) }))
      .rejects.toThrow(/calculator\.stderr\.log/i);
    expect(await readFile(path.join(out, 'calculator.stderr.log'), 'utf8')).toContain('connection unavailable');
    expect(progress[0]).toContain('Calculator');
  });
});
