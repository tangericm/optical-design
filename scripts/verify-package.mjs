#!/usr/bin/env node
// Pack the tarball, install it into a throwaway consumer, assert the skill files arrive intact.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const source = fileURLToPath(new URL("../", import.meta.url));
const npmCli = process.env.npm_execpath;
assert.ok(npmCli && fs.existsSync(npmCli), "Run with: npm run verify:package");
const root = fs.mkdtempSync(path.join(os.tmpdir(), "optical-design-package-"));
function run(cwd, args) {
  const r = spawnSync(process.execPath, args, { cwd, encoding: "utf8", timeout: 120_000 });
  assert.ifError(r.error);
  assert.equal(r.status, 0, r.stderr || r.stdout);
  return r.stdout;
}
try {
  const [pack] = JSON.parse(run(source, [npmCli, "pack", "--json", "--ignore-scripts", "--pack-destination", root]));
  const files = pack.files.map(f => f.path);
  for (const required of ["skills/optical-design/SKILL.md", "skills/optical-design/LICENSE",
    "skills/optical-design/scripts/_lib/cli.py", "skills/optical-design/scripts/resolve.py",
    "skills/optical-design/scripts/zernike.py", "skills/optical-design/scripts/wavefront.py",
    "skills/optical-design/scripts/interfero.py", "skills/optical-design/scripts/compare.py",
    "skills/optical-design/scripts/design.py", "skills/optical-design/scripts/zos.py",
    "skills/optical-design/scripts/catalog.py", "skills/optical-design/scripts/_lib/design_jobs.py",
    "skills/optical-design/scripts/_lib/zos_backend.py", "skills/optical-design/scripts/_lib/optiland_backend.py",
    "skills/optical-design/scripts/_lib/tolerancing.py", "skills/optical-design/references/design-workflow.md",
    "skills/optical-design/assets/refocus-spec.json", "skills/optical-design/assets/portable-singlet.json",
    "docs/tiers.md", "docs/install.md", "LICENSE", "README.md", "SECURITY.md"]) {
    assert.ok(files.includes(required), `Missing package file: ${required}`);
  }
  assert.ok(files.every(f => !/^(?:tests|node_modules|docs\/superpowers|docs\/research|\.github)\//u.test(f)), "Package contains local files");
  assert.ok(files.every(f => !/(^|\/)__pycache__\/|\.pyc$/u.test(f)), "Package contains python bytecode");
  assert.ok(files.every(f => !/\.(?:ZDA|zda|bak)$/u.test(f)), "Package contains native analysis caches/backups");
  const consumer = path.join(root, "consumer");
  fs.mkdirSync(consumer);
  fs.writeFileSync(path.join(consumer, "package.json"), JSON.stringify({ name: "consumer", private: true }));
  run(consumer, [npmCli, "install", "--ignore-scripts", "--no-audit", "--no-fund", path.join(root, pack.filename)]);
  const skill = path.join(consumer, "node_modules", "optical-design", "skills", "optical-design", "SKILL.md");
  assert.ok(fs.readFileSync(skill, "utf8").startsWith("---\nname: optical-design"));
  console.log("verify-package: ok");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
