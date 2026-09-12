import { describe, expect, it } from "vitest";
import matter from "gray-matter";
import fs from "node:fs";
import path from "node:path";

const skillDir = path.resolve(__dirname, "..", "..", "skills", "optical-design");
const raw = fs.readFileSync(path.join(skillDir, "SKILL.md"), "utf8");
const parsed = matter(raw);
const allowed = ["name", "description", "license", "compatibility", "metadata"];

describe("SKILL.md frontmatter (Agent Skills spec)", () => {
  it("uses only portable fields", () => {
    for (const key of Object.keys(parsed.data)) expect(allowed, `field ${key}`).toContain(key);
  });
  it("name matches the directory and description is within limits", () => {
    expect(parsed.data.name).toBe("optical-design");
    expect(typeof parsed.data.description).toBe("string");
    expect(parsed.data.description.length).toBeGreaterThan(100);
    expect(parsed.data.description.length).toBeLessThanOrEqual(1024);
    expect(parsed.data.compatibility.length).toBeLessThanOrEqual(500);
    expect(parsed.data.license).toBe("MIT");
    expect(parsed.data.metadata.version).toBe(JSON.parse(fs.readFileSync(path.resolve(skillDir, "..", "..", "package.json"), "utf8")).version);
  });
  it("body stays under 400 lines and references shipped scripts only", () => {
    const lines = parsed.content.split("\n");
    expect(lines.length).toBeLessThan(400);
    const scripts = fs.readdirSync(path.join(skillDir, "scripts")).filter(f => f.endsWith(".py"));
    for (const m of parsed.content.matchAll(/scripts\/([a-z_]+\.py)/gu)) expect(scripts, m[1]).toContain(m[1]);
  });
});
