import { describe, expect, it } from "vitest";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(__dirname, "..", "..");
const read = (p: string) => JSON.parse(fs.readFileSync(path.join(root, p), "utf8"));

describe("distribution manifests", () => {
  it("package.json has the required identity", () => {
    const pkg = read("package.json");
    expect(pkg.name).toBe("optical-design");
    expect(pkg.license).toBe("MIT");
    expect(pkg.engines.node).toBe(">=22");
    expect(pkg.bin).toBeUndefined();
    expect(pkg.files).toContain("skills");
  });
  it("plugin manifests agree with package.json", () => {
    const pkg = read("package.json");
    const agentPlugin = read("plugin.json");
    const claudePlugin = read(".claude-plugin/plugin.json");
    const marketplace = read(".claude-plugin/marketplace.json");
    expect(agentPlugin.name).toBe("optical-design");
    expect(agentPlugin.version).toBe(pkg.version);
    expect(claudePlugin.version).toBe(pkg.version);
    expect(claudePlugin.skills).toBe("./skills/");
    expect(marketplace.plugins[0].name).toBe("optical-design");
    expect(marketplace.plugins[0].source).toBe("./");
  });
  it("npm pack ships the skill and nothing local", () => {
    const result = spawnSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], {
      cwd: root, encoding: "utf8", shell: process.platform === "win32"
    });
    expect(result.status).toBe(0);
    const files: string[] = JSON.parse(result.stdout)[0].files.map((f: { path: string }) => f.path);
    for (const required of ["skills/optical-design/SKILL.md", "skills/optical-design/LICENSE", "LICENSE", "README.md", "SECURITY.md"]) {
      expect(files, `missing ${required}`).toContain(required);
    }
    expect(files.some(f => /^(tests|node_modules|docs\/superpowers|\.github)\//u.test(f))).toBe(false);
  });
});
