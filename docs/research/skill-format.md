# What makes a production-grade, widely-adopted Agent Skill

Sources checked locally: Anthropic `skill-creator` plugin (`<home>\.claude\plugins\marketplaces\claude-plugins-official\plugins\skill-creator\skills\skill-creator\SKILL.md` + `references/schemas.md`), superpowers `writing-skills` SKILL.md (v6.3.0), mattpocock-skills `writing-for-agents` + `SKILL-MECHANICS.md`. Web: agentskills.io/specification, github.com/anthropics/skills, code.claude.com/docs/en/skills, vercel-labs/skills + skills.sh, obra/superpowers README.

---

## 1. Frontmatter spec

### Agent Skills open standard (agentskills.io/specification) — the portable baseline
| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1–64 chars, lowercase unicode alphanumeric + hyphens only, no leading/trailing/consecutive hyphens, **must match parent directory name** |
| `description` | Yes | 1–1024 chars, non-empty; must state both *what it does* and *when to use it*; should include specific trigger keywords |
| `license` | No | license name or pointer to bundled LICENSE file |
| `compatibility` | No | ≤500 chars; environment/tooling requirements (e.g. "Requires git, docker, jq, internet") |
| `metadata` | No | free-form string→string map, keys should be namespaced to avoid collisions |
| `allowed-tools` | No, experimental | space-separated pre-approved tool list, e.g. `Bash(git:*) Read` |

Source: https://agentskills.io/specification

Validator exists: `skills-ref validate ./my-skill` (github.com/agentskills/agentskills/tree/main/skills-ref).

### Claude Code superset (code.claude.com/docs/en/skills)
Adds many CC-specific fields on top of the spec baseline: `when_to_use` (extra trigger context, counts toward a combined 1,536-char cap with `description`), `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context: fork` (+ `agent`, `background`), `hooks`, `paths` (glob-scoped auto-activation), `shell`. **Important interoperability note:** only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` survive upload to claude.ai / the Skills API / `package_skill.py` — CC-only fields are stripped outside Claude Code. Source: https://code.claude.com/docs/en/skills

### Description-quality consensus (all three sources agree)
- Third person, starts with **"Use when..."** to front-load triggering conditions (superpowers `writing-skills`, local file).
- **Never summarize the skill's internal workflow in the description** — superpowers found this causes agents to act on the summary instead of reading the body (tested empirically: a workflow-summarizing description caused a two-stage review process to collapse into one stage). Description = trigger conditions only.
- Anthropic's own skill-creator explicitly recommends making descriptions "a little bit pushy" to counter observed under-triggering, e.g. adding "even if they don't explicitly ask for X."
- Keep under ~500 characters if possible even though the cap is 1024 (superpowers) / 1536 combined (CC `when_to_use`).
- `name` should be a gerund/verb-first phrase (`condition-based-waiting`, not `async-test-helpers`) for scan-ability.

---

## 2. Directory layout + progressive disclosure

Canonical layout (agentskills.io, anthropics/skills, skill-creator all match):
```
skill-name/
├── SKILL.md        # required: YAML frontmatter + markdown body
├── scripts/        # executable code — run, not read; self-contained, clear errors
├── references/     # docs loaded into context on demand (REFERENCE.md, domain-*.md)
└── assets/         # templates, fonts, icons, schemas used in *output*, not read as instructions
```

Three-level progressive-disclosure loading model (identical across agentskills.io spec and skill-creator):
1. **Metadata** (name + description) — always resident, ~100 tokens, for every skill regardless of activation.
2. **SKILL.md body** — loaded fully once the skill activates. Spec's own recommendation: **<5000 tokens**; both Anthropic's spec and skill-creator/writing-skills converge on **<500 lines** as the practical ceiling, "if approaching the limit, add a layer of hierarchy with a pointer to where to go next."
3. **Bundled resources** (scripts/references/assets) — pulled in only as needed; scripts execute without ever entering context at all. Reference files >300 lines should carry a table of contents (skill-creator).

Domain-variant organization pattern (skill-creator): put shared workflow in SKILL.md, branch per variant into `references/<variant>.md` (e.g. `references/aws.md`, `references/gcp.md`) so the agent loads only the relevant one.

File-reference rule (agentskills.io): keep references one level deep from SKILL.md — avoid chains of references pointing to references.

Source: https://agentskills.io/specification ; local skill-creator SKILL.md lines 73–110.

---

## 3. Checklist: features shared by top / production-grade skills

- [x] **"Use when..." description**, trigger-only, no workflow summary (superpowers, skill-creator)
- [x] **When-NOT-to-use / competing-skill disambiguation** baked into description via should-not-trigger near-miss testing (skill-creator description-optimization loop explicitly authors 8-10 "should-not-trigger" adversarial queries)
- [x] **Deterministic scripts for computation**, treated as black boxes agents run via `--help`, not files agents read line-by-line (webapp-testing skill: "Always run scripts with `--help` first"; skill-creator: "if all 3 test cases independently wrote the same helper script, bundle it")
- [x] **References split per subtopic**, loaded on demand, ToC for long files (pdf/docx/xlsx/mcp-builder all follow this — mcp-builder has `reference/mcp_best_practices.md`, `reference/node_mcp_server.md`, `reference/python_mcp_server.md`, `reference/evaluation.md`)
- [x] **Eval/test suite** — `evals/evals.json` with prompts + expectations, run against with-skill and baseline/without-skill subagents, graded, aggregated to `benchmark.json` (skill-creator schema; also required by CC's `claude plugin eval`)
- [x] **License field** — most anthropics/skills entries Apache-2.0; the four "document" skills (docx/pdf/pptx/xlsx) are explicitly source-available, not OSS, "shared as reference implementations" (github.com/anthropics/skills)
- [x] **Versioning in `metadata`** (spec allows arbitrary key-value, e.g. `metadata: {author, version}`) — UNVERIFIED whether widely used in practice; no CHANGELOG convention found in any source inspected
- [x] **CI/lint** — `skills-ref validate` exists as an external validator (agentskills.io); `claude plugin eval` can gate CI by exiting non-zero below a score threshold (code.claude.com docs / community write-ups). UNVERIFIED: no evidence any of the anthropics/skills repo's own skills run a CI-linked eval in their public CI — the repo's README references a template + "how to create custom skills" doc rather than an enforced pipeline.
- [x] **Prerequisites stated via `compatibility` field**, not prose install steps, when possible (agentskills.io examples: "Requires Python 3.14+ and uv"); webapp-testing instead assumes Playwright is present with no explicit install step — inconsistent in the wild.
- [x] **Testing via subagents with a baseline (no-skill) control** — both skill-creator (with_skill vs without_skill/old_skill subagent runs) and superpowers (RED phase = baseline subagent run without the skill, documenting verbatim rationalizations) independently converge on this exact pattern.
- [x] **TDD framing for skill authorship itself**: superpowers' "Iron Law — NO SKILL WITHOUT A FAILING TEST FIRST" — write pressure-scenario tests, watch baseline agent fail/violate, write minimal skill, re-test, refactor to close rationalization loopholes, maintain a "rationalization table" and "red flags" list for discipline-type skills.
- [x] **Match guidance form to failure type** (mattpocock writing-for-agents): prohibition+rationalization-table only for pressure/discipline failures; positive recipe/contract for shape failures; structural required-field for omission failures — using the wrong form (e.g. prohibitions for a shaping problem) empirically produces *worse* output than no guidance at all in their micro-tests.
- [x] **Cross-referencing convention**: name other skills explicitly with `REQUIRED SUB-SKILL:` / `REQUIRED BACKGROUND:` markers rather than `@file` force-loads (which burn context immediately) or ambiguous prose links (superpowers writing-skills).

---

## 4. Distribution options compared

| Option | Mechanism | Pros | Cons (esp. for domain-knowledge skill + Python compute scripts) |
|---|---|---|---|
| **npm package with `skills/` dir + `npx skills add owner/repo`** (vercel-labs/skills, skills.sh registry) | `npx skills add` resolves owner/repo like an npm package name; supports 75+ agent targets (OpenCode, Claude Code, Codex, Cursor, etc.); `--list` previews, `--skill name` installs one skill from a multi-skill repo | Cross-agent portability (not CC-locked); lightweight — just a git repo, no publish step to npm itself; skills.sh gives a public leaderboard/discovery surface and install telemetry | Registry/ecosystem still young (2026); no built-in eval/CI gate at install time; Python scripts must be self-contained (no npm dependency resolution for them) — the CLI just copies files, doesn't manage a Python venv |
| **Claude Code plugin marketplace** (`plugin.json` + `marketplace.json`, `/plugin install x@marketplace`) | Plugin bundles `skills/`, `agents/`, `hooks/`, `output-styles/`; skills namespaced as `/plugin-name:skill-name`; supports `claude plugin eval` for CI-gated scoring with/without the plugin | Deepest integration with CC-specific frontmatter (`context:fork`, `hooks`, `allowed-tools`, dynamic `!command` injection); official quality bar via anthropics/claude-plugins-official curation; native eval tooling | Claude-Code-only — fields like `context`, `hooks`, `model`, `effort` are stripped if the skill is later exported to claude.ai/Skills API or another agent runtime; heavier packaging (`.claude-plugin/` structure) |
| **MCP server** | Expose functionality as tools/resources over Model Context Protocol instead of markdown+scripts | Best fit when the "skill" is really a stateful service, needs auth, or must run outside the agent's local sandbox (matches this session's own experience: several plugin MCP servers required OAuth) | Not a Skill in the agentskills.io sense — no progressive disclosure, no natural-language instruction layer; agent must already know to call the right tool; heavier to build/host than a folder of markdown+scripts; overkill for pure domain knowledge |
| **anthropics/skills GitHub repo pattern** (public repo, Apache-2.0 or source-available, `template/` starter) | Direct git clone / manual copy into `~/.claude/skills/` or `.claude/skills/` | Simplest possible distribution, no tooling dependency; used by Anthropic itself for docx/pdf/pptx/xlsx/mcp-builder/webapp-testing | No install automation, no versioning/update mechanism, no cross-agent guarantee beyond the spec itself |

**Recommendation for a domain-knowledge skill that also ships Python compute scripts:** the Agent Skills spec's own `scripts/` convention (run, not read) plus either (a) the npm/`npx skills add` route for cross-agent reach, or (b) a Claude Code plugin if you want `claude plugin eval` CI gating and CC-specific features (fork context, hooks) — these are not mutually exclusive, since a plugin's `skills/` directory is spec-compliant and could also be listed on skills.sh.

Sources: https://github.com/vercel-labs/skills , https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem , https://code.claude.com/docs/en/skills , https://github.com/anthropics/skills

---

## 5. Eval / testing approaches

**Anthropic skill-creator loop** (authoritative, local file read in full):
1. Draft SKILL.md → write 2-3 realistic test prompts → save prompts-only to `evals/evals.json` (no assertions yet).
2. Spawn **both** a with-skill subagent and a baseline subagent (no-skill for new skills; old-version snapshot for edits) **in the same turn**, per test case.
3. While runs are in flight, draft verifiable assertions (avoid forcing assertions onto subjective/style outputs — use human qualitative review there instead).
4. Grade each run's assertions → `grading.json` (exact field names `text`/`passed`/`evidence` required by the viewer) → aggregate via `scripts.aggregate_benchmark` into `benchmark.json`/`benchmark.md` (pass-rate, time, tokens, mean±stddev, delta) → an analyst pass flags non-discriminating assertions and high-variance (flaky) evals.
5. Human review via a generated HTML viewer (`eval-viewer/generate_review.py`, static-file mode for headless/Cowork); feedback saved to `feedback.json` drives the next iteration.
6. Separate **description-optimization loop**: generate 20 adversarial trigger queries (8-10 should-trigger, 8-10 near-miss should-not-trigger), human-reviewed via an HTML export tool, then `scripts.run_loop` auto-iterates the description against a 60/40 train/test split (3 reps per query for reliability), selecting `best_description` by held-out test score to avoid overfitting.
Source: local `skill-creator/SKILL.md`.

**superpowers TDD-for-skills** (writing-skills SKILL.md, local file):
- RED: run a **pressure scenario** (combined time/sunk-cost/authority/exhaustion pressures) with a subagent that does **not** have the skill; record verbatim rationalizations/failures — this is the "failing test."
- GREEN: write the minimal skill addressing exactly those observed failures; re-run the same scenario with the skill; agent must comply.
- REFACTOR: new rationalizations found → add explicit named counters to a "rationalization table" and a "red flags" self-check list; repeat until bulletproof.
- Different skill *types* need different test shapes: discipline-enforcing skills → pressure scenarios; technique skills → application/edge-case scenarios; pattern skills → recognition + counter-example scenarios; reference skills → retrieval/gap scenarios.
- Micro-testing wording before full pressure runs: 1 fresh-context sample per call, always with a no-guidance control, 5+ reps, manually read every flagged match (counts alone overstate pass/fail) — cheaper iteration loop before the expensive full pressure-scenario gate.
- "Iron Law: NO SKILL WITHOUT A FAILING TEST FIRST" — applies to edits too, no exceptions for "just a small addition."

**`claude plugin eval` (Claude Code CLI)**: runs each `evals/evals.json` prompt in an isolated session with and without the plugin, scores with custom or auto-generated graders, exits non-zero below a threshold for CI gating. **Format is explicitly incompatible** with skill-creator's own `evals/evals.json` shape and with the claude.ai Skills API eval format (three separate, non-interoperable eval schemas currently exist). No public documentation page was found for this command as of the search — confirmed only via `--help` and third-party blog posts (matthewswong.com, aibuilders.blog). **Mark as UNVERIFIED**: exact CLI flags, threshold-setting syntax, and whether it is GA vs. early-access — could not confirm from official docs.

Source: https://www.matthewswong.com/en/blog/claude-code-plugin-eval-test-suite/ ; https://www.aibuilders.blog/p/how-to-build-a-claude-plugin-marketplace-evals (both UNVERIFIED against an official primary source).

---

## Notes on what could not be verified
- Whether any anthropics/skills repo skill actually runs `skills-ref validate` or any eval in a public CI pipeline — UNVERIFIED (repo README references a template and docs, not an enforced CI gate, per WebFetch summary).
- Exact `claude plugin eval` flags/thresholds/GA status — UNVERIFIED, no official docs page found.
- Whether `metadata.version` + a CHANGELOG file is a *common* convention among widely-installed skills, vs. just spec-permitted — UNVERIFIED; not observed in any of the four inspected anthropics/skills examples (mcp-builder, webapp-testing, pdf-family) or in skill-creator itself.
- vercel-labs/skills quality signals (evals/tests/CI badges on skills.sh listings) — WebSearch summary described the registry and install mechanics but did not confirm any quality-signal/badge system; treat "quality signals" claim as UNVERIFIED beyond install-count telemetry.
