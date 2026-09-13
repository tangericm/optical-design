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
  const r = spawnSync(process.execPath, args, { cwd, encoding: "utf8", timeout: 240_000 });
  assert.ifError(r.error);
  assert.equal(r.status, 0, r.stderr || r.stdout);
  return r.stdout;
}
try {
  const [pack] = JSON.parse(run(source, [npmCli, "pack", "--json", "--ignore-scripts", "--pack-destination", root]));
  const files = pack.files.map(f => f.path);
  for (const required of ["bin/optical-design.mjs", "lib/cli.mjs", "lib/installer.mjs", "lib/filesystem.mjs", "lib/workflows.mjs",
    ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".agents/plugins/marketplace.json", ".cursor-plugin/plugin.json", "plugin.json",
    "assets/icon.png", "assets/logo.png", "assets/logo-dark.png", "assets/brand/header.svg",
    "docs/README.md", "docs/cli.md", "docs/first-lens.md", "docs/glossary.md", "docs/professional-workflow.md",
    "skills/optical-design/SKILL.md", "skills/optical-design/LICENSE",
    "skills/optical-design/scripts/_lib/cli.py", "skills/optical-design/scripts/resolve.py",
    "skills/optical-design/scripts/zernike.py", "skills/optical-design/scripts/wavefront.py",
    "skills/optical-design/scripts/interfero.py", "skills/optical-design/scripts/compare.py",
    "skills/optical-design/scripts/design.py", "skills/optical-design/scripts/zos.py",
    "skills/optical-design/scripts/catalog.py", "skills/optical-design/scripts/_lib/design_jobs.py",
    "skills/optical-design/scripts/_lib/zos_backend.py", "skills/optical-design/scripts/_lib/optiland_backend.py",
    "skills/optical-design/scripts/_lib/tolerancing.py", "skills/optical-design/references/design-workflow.md",
    "skills/optical-design/scripts/benchmark.py", "skills/optical-design/scripts/_lib/profile_benchmark.py",
    "skills/optical-design/scripts/_lib/native_profiles.py", "skills/optical-design/scripts/_lib/profiles.py",
    "skills/optical-design/references/profile-benchmark.md",
    "skills/optical-design/scripts/_lib/optimization.py", "skills/optical-design/scripts/_lib/compensation.py", "skills/optical-design/scripts/_lib/tool_jobs.py",
    "skills/optical-design/scripts/server.py", "skills/optical-design/references/interactive.md",
    "skills/optical-design/scripts/review.py", "skills/optical-design/scripts/_lib/review_report.py",
    "skills/optical-design/scripts/_lib/model_actions.py", "skills/optical-design/scripts/_lib/sensitivity.py",
    "skills/optical-design/references/merit-functions.md", "skills/optical-design/references/model-actions.md",
    "skills/optical-design/references/sensitivity.md", "skills/optical-design/references/review-reports.md",
    "skills/optical-design/evals/run-portable-workflow.ps1", "skills/optical-design/evals/full-workflow.json",
    "skills/optical-design/assets/full-workflow/composite-spec.json", "skills/optical-design/assets/full-workflow/changes.json",
    "skills/optical-design/assets/full-workflow/perturbations.json",
    "skills/optical-design/assets/conic-singlet.zmx", "skills/optical-design/assets/aspheric-singlet.zmx",
    "skills/optical-design/references/optimization.md",
    "skills/optical-design/assets/compensation-spec.json", "skills/optical-design/assets/compensated-tolerances-example.json",
    "skills/optical-design/assets/validation-spec.json", "skills/optical-design/references/validation.md",
    "skills/optical-design/references/field-validation-example.md",
    "skills/optical-design/assets/field-validation/native.zmx", "skills/optical-design/assets/field-validation/portable.json",
    "skills/optical-design/assets/field-validation/search.json", "skills/optical-design/assets/field-validation/control.json",
    "skills/optical-design/assets/field-validation/validation.json",
    "skills/optical-design/assets/optimization-spec.json", "skills/optical-design/assets/variables-example.json",
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
  const version = JSON.parse(fs.readFileSync(path.join(source, "package.json"), "utf8")).version;
  const bin = path.join(consumer, "node_modules", "optical-design", "bin", "optical-design.mjs");
  assert.equal(run(consumer, [npmCli, "exec", "--offline", "--", "optical-design", "--version"]).trim(), version);
  for (const agent of ["claude-code", "codex", "cursor", "opencode", "hermes"]) {
    const project = path.join(root, `project-${agent}`);
    fs.mkdirSync(project);
    const installed = JSON.parse(run(project, [bin, "install", "--agent", agent, "--json"]));
    assert.equal(installed.version, version);
    assert.equal(fs.readFileSync(path.join(installed.destination, "SKILL.md"), "utf8"), fs.readFileSync(skill, "utf8"));
    const updated = JSON.parse(run(project, [bin, "update", "--agent", agent, "--json"]));
    assert.ok(fs.existsSync(path.join(updated.backup, "SKILL.md")), "Update backup missing");
    run(project, [bin, "uninstall", "--agent", agent, "--json"]);
    assert.ok(!fs.existsSync(installed.destination), "Uninstall did not remove managed installation");
  }
  if (process.argv.includes("--demo")) {
    const demo = JSON.parse(run(consumer, [bin, "demo", "--out", path.join(root, "demo"), "--json"]));
    assert.equal(demo.status, "improved");
    assert.equal(demo.saved_candidate_verified, true);
    assert.ok(fs.existsSync(demo.review));
    console.log("verify-package: packed portable demo passed");
  }
  console.log("verify-package: ok");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
