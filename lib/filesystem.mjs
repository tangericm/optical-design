import { lstat, mkdir, readdir, readFile, unlink, rmdir, realpath } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

export const RECEIPT = '.optical-design-install.json';
export const OWNED_DIRECTORY = /^\.optical-design\.(stage|remove|backup)-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

// macOS exposes system-owned /var and /tmp through /private. Normalize only these
// verified aliases before both containment checks and link rejection, never user links.
export async function normalizeSystemPath(filename) {
  const absolute = path.resolve(filename);
  if (process.platform !== 'darwin') return absolute;
  for (const alias of ['/var', '/tmp']) {
    if (absolute !== alias && !absolute.startsWith(`${alias}/`)) continue;
    if (await realpath(alias) === `/private${alias}`) return `/private${absolute}`;
  }
  return absolute;
}

export async function statOptional(filename) {
  try { return await lstat(filename); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

export function contained(root, target) {
  const relative = path.relative(path.resolve(root), path.resolve(target));
  return relative !== '' && relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
}

// Inspect every existing ancestor, including the final component. Junctions are links too.
export async function assertNoLinks(filename) {
  const absolute = await normalizeSystemPath(filename);
  const base = path.parse(absolute).root;
  let current = base;
  for (const part of absolute.slice(base.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    const info = await statOptional(current);
    if (info?.isSymbolicLink()) throw new Error(`Refusing symbolic link or symlink: ${current}`);
    if (info && current !== absolute && !info.isDirectory()) throw new Error(`Not a directory: ${current}`);
  }
}

export async function safeMkdir(directory) {
  await assertNoLinks(directory);
  await mkdir(directory, { recursive: true });
  await assertNoLinks(directory);
}

export async function snapshot(directory, { omitReceipt = false } = {}) {
  await assertNoLinks(directory);
  const info = await statOptional(directory);
  if (!info?.isDirectory()) throw new Error(`Expected a directory: ${directory}`);
  const files = Object.create(null);
  const directories = [];
  async function visit(folder, prefix = '') {
    for (const name of (await readdir(folder)).sort()) {
      const relative = prefix ? `${prefix}/${name}` : name;
      const absolute = path.join(folder, name);
      const entry = await lstat(absolute);
      if (entry.isSymbolicLink()) throw new Error(`Refusing symbolic link or symlink: ${absolute}`);
      if (omitReceipt && relative === RECEIPT) {
        if (!entry.isFile()) throw new Error('Invalid installation manifest');
        continue;
      }
      if (entry.isDirectory()) { directories.push(relative); await visit(absolute, relative); }
      else if (entry.isFile()) files[relative] = createHash('sha256').update(await readFile(absolute)).digest('hex');
      else throw new Error(`Refusing special file: ${absolute}`);
    }
  }
  await visit(directory);
  return { files, directories: directories.sort() };
}

// Only call for an exact generated sibling name. Enumerate first; never recursive-rm.
export async function removeOwnedTree(parent, directory) {
  if (!contained(parent, directory) || path.dirname(directory) !== path.resolve(parent) ||
      !OWNED_DIRECTORY.test(path.basename(directory))) {
    throw new Error('Unsafe cleanup path');
  }
  const tree = await snapshot(directory);
  for (const relative of Object.keys(tree.files)) {
    const filename = path.join(directory, relative);
    await assertNoLinks(filename);
    await unlink(filename);
  }
  for (const relative of tree.directories.sort((a, b) => b.split('/').length - a.split('/').length)) {
    await assertNoLinks(path.join(directory, relative));
    await rmdir(path.join(directory, relative));
  }
  await rmdir(directory);
}
