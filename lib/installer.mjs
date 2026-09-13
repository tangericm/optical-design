import { mkdir, readFile, writeFile, rename, rmdir } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { assertNoLinks, contained, normalizeSystemPath, RECEIPT, removeOwnedTree, safeMkdir, snapshot, statOptional } from './filesystem.mjs';

export const AGENTS = Object.freeze({
  'claude-code': ['.claude/skills', '.claude/skills'],
  codex: ['.agents/skills', '.agents/skills'],
  cursor: ['.cursor/skills', '.cursor/skills'],
  opencode: ['.opencode/skills', '.config/opencode/skills'],
  hermes: ['.hermes/skills', '.hermes/skills'],
});

export async function packageVersion(packageRoot) {
  return JSON.parse(await readFile(path.join(packageRoot, 'package.json'), 'utf8')).version;
}

function sameTree(a, b) {
  const files = Object.keys(a.files).sort();
  return JSON.stringify(files) === JSON.stringify(Object.keys(b.files).sort()) &&
    files.every(name => a.files[name] === b.files[name]) &&
    JSON.stringify(a.directories) === JSON.stringify(b.directories);
}

async function verifyManaged(destination) {
  await assertNoLinks(destination);
  if (!(await statOptional(path.join(destination, RECEIPT)))) throw new Error('Unmanaged installation: no ownership manifest. Files preserved.');
  await assertNoLinks(path.join(destination, RECEIPT));
  let receipt;
  try { receipt = JSON.parse(await readFile(path.join(destination, RECEIPT), 'utf8')); }
  catch { throw new Error('Invalid installation manifest. Files preserved.'); }
  if (receipt.schema !== 1 || receipt.package !== 'optical-design' || typeof receipt.version !== 'string' ||
      !receipt.files || typeof receipt.files !== 'object' || Array.isArray(receipt.files) ||
      !Array.isArray(receipt.directories)) throw new Error('Invalid installation manifest. Files preserved.');
  const actual = await snapshot(destination, { omitReceipt: true });
  if (!sameTree(actual, receipt)) throw new Error('Managed installation changed or edited (including new files). Files preserved.');
  return receipt;
}

async function stageBundle(source, stage, version) {
  const before = await snapshot(source);
  if (Object.hasOwn(before.files, RECEIPT) || before.directories.includes(RECEIPT)) throw new Error('Bundled source contains a reserved installation manifest');
  if (!Object.hasOwn(before.files, 'SKILL.md')) throw new Error('Bundled SKILL.md is missing');
  await mkdir(stage);
  for (const directory of before.directories) await mkdir(path.join(stage, directory), { recursive: true });
  for (const filename of Object.keys(before.files)) {
    await assertNoLinks(path.join(source, filename));
    await writeFile(path.join(stage, filename), await readFile(path.join(source, filename)), { flag: 'wx' });
  }
  if (!sameTree(before, await snapshot(stage)) || !sameTree(before, await snapshot(source))) throw new Error('Bundled source changed while copying');
  await writeFile(path.join(stage, RECEIPT), `${JSON.stringify({ schema: 1, package: 'optical-design', version, ...before }, null, 2)}\n`, { flag: 'wx' });
}

export async function manage(operation, options, context) {
  if (!['install', 'update', 'uninstall'].includes(operation)) throw new Error('Unknown installation operation');
  if (!Object.hasOwn(AGENTS, options.agent)) throw new Error(`Unknown agent. Choose ${Object.keys(AGENTS).join(', ')}`);
  const scope = options.global ? 'global' : 'project';
  const root = await normalizeSystemPath(options.global ? context.home : context.cwd);
  const destination = path.join(root, AGENTS[options.agent][options.global ? 1 : 0], 'optical-design');
  const parent = path.dirname(destination);
  const source = await normalizeSystemPath(path.resolve(context.packageRoot, 'skills/optical-design'));
  if (!contained(root, destination)) throw new Error('Unsafe installation destination');
  if (source === destination || contained(source, destination) || contained(destination, source)) throw new Error('Installation destination must not overlap or be inside bundled source');
  await assertNoLinks(destination);
  if (operation === 'install' && await statOptional(destination)) throw new Error('Installation already exists. Use update for an intact managed installation.');
  if (operation !== 'install') await verifyManaged(destination);
  // Validate the bundle before creating destination parents.
  if (operation !== 'uninstall') await snapshot(source);
  await safeMkdir(parent);
  const lock = path.join(parent, '.optical-design.lock');
  await assertNoLinks(lock);
  try { await mkdir(lock); }
  catch (error) { if (error.code === 'EEXIST') throw new Error(`Another operation or a stale lock exists: ${lock}`); throw error; }
  let stage;
  let backup;
  try {
    await assertNoLinks(destination);
    if (operation === 'install' && await statOptional(destination)) throw new Error('Installation already exists');
    if (operation !== 'install') await verifyManaged(destination);
    const version = await packageVersion(context.packageRoot);
    if (operation === 'uninstall') {
      const removal = path.join(parent, `.optical-design.remove-${randomUUID()}`);
      await rename(destination, removal);
      try {
        await verifyManaged(removal);
        await removeOwnedTree(parent, removal);
      } catch (error) {
        // Preserve any remaining files for recovery if deletion was interrupted.
        error.message += ` Recovery directory: ${removal}`;
        throw error;
      }
      return { ok: true, operation, agent: options.agent, scope, destination, version };
    }
    stage = path.join(parent, `.optical-design.stage-${randomUUID()}`);
    await stageBundle(source, stage, version);
    await assertNoLinks(destination);
    if (operation === 'update') {
      await verifyManaged(destination);
      backup = path.join(parent, `.optical-design.backup-${randomUUID()}`);
      await rename(destination, backup);
    } else if (await statOptional(destination)) throw new Error('Installation already exists');
    try { await rename(stage, destination); stage = undefined; }
    catch (error) {
      if (backup && !(await statOptional(destination))) { await rename(backup, destination); backup = undefined; }
      throw error;
    }
    return { ok: true, operation, agent: options.agent, scope, destination, version, ...(backup ? { backup } : {}) };
  } finally {
    try {
      if (stage && await statOptional(stage)) await removeOwnedTree(parent, stage);
    } finally { await assertNoLinks(lock); await rmdir(lock); }
  }
}
