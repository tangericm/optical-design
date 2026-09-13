# Production distribution implementation plan

> Use subagent-driven development for bounded independent implementation and a final review.

**Goal:** Ship optical-design 1.1.0 with a versioned npm installer, native plugin packaging,
a recognizable public identity, and approachable onboarding.

**Architecture:** A dependency-free Node CLI copies the single bundled optical skill;
native client manifests reference that same skill. Existing Python engines remain fixed.
**Tech stack:** Node >=22, existing Python/uv optical tools, GitHub Markdown, SVG/PNG.
**Spec:** ../specs/2026-09-13-distribution-design.md

## Global constraints

Preserve user files and historical evidence. No lifecycle side effects. No claims of
marketplace acceptance without proof. No optical algorithm changes. Version 1.1.0.

## Task 1: npm command

Files: bin/optical-design.mjs, lib/*.mjs, tests/node/installer.test.ts.
Interfaces: CLI install/update/uninstall --agent NAME [--global] [--json]; doctor;
demo --out NEWDIR; --help; --version. Root supplies package bin/files entries.

- [x] Write and run failing ownership/conflict/path/CLI tests against temporary roots.
- [x] Implement atomic managed copies, explicit scope, backups, and conservative removal.
- [x] Implement doctor and uv demo with true exit/status checking.
- [x] Run focused tests and report exact commands, ownership format, and limitations.

## Task 2: original identity

Files: assets/brand/*, assets/icon.png, assets/logo.png, assets/logo-dark.png, DESIGN.md.
Interfaces: README header image assets/brand/header.svg; plugin PNGs under assets/.

- [x] Create scalable lens/focus logo and a compact README header.
- [x] Render and inspect light/dark and small-size variants in one batched pass.
- [x] Record palette, asset usage, and honest illustrative status in DESIGN.md.

## Task 3: native packaging and onboarding

Files: .codex-plugin/plugin.json, .agents/plugins/marketplace.json, .cursor-plugin/plugin.json,
existing manifests, package.json/lock, README.md, docs/*, .github/ISSUE_TEMPLATE/*.

- [x] Validate current client schemas and document actual install commands.
- [x] Add Codex repository marketplace and native manifest; retain shared skill.
- [x] Update all version metadata and pack allowlist; extend actual tarball checks.
- [x] Add a reference glossary, runnable example, and existing-prescription workflow; no lesson framing.
- [x] Validate client installs in temporary configuration roots and verify documentation links.

## Task 4: verification and publication

- [x] Review combined installer, manifests, ownership safety, and public claims independently.
- [x] Run local Node tests, packed clean installation, and the optical demo. Cross-platform Python and Node checks follow in CI.
- [x] Push reviewed commit and require cross-platform CI success.
- [x] Publish npm 1.1.0 after npm authentication; verify registry integrity and fresh npx use.
- [x] Publish GitHub release and record native marketplace availability accurately.

## Execution ledger

- Initial documentation checkpoint: 0494d86, seven packaging tests and portable quickstart passed.
- npm authentication initially unavailable (ENEEDAUTH); user asked to sign in through npm.
- Ownership: Task 1 owns bin/lib/installer tests; Task 2 owns assets and DESIGN.md;
  root owns packaging/docs/release. No shared implementation files between tasks.

- User confirmed npm login; `npm whoami` returned `etang`.
- Independent installer review found two issues, fixed with regression tests: own-property
  inventory for `__proto__` filenames and verified Darwin system alias normalization.
  Follow-up review found no blocking findings. Local Node: 42 passed, one Darwin skip.
- Packed demo passed real Optiland 0.6.2 refocus acceptance, saved-model verification,
  and HTML review creation. Progress is visible and per-step diagnostic logs are retained.
- Native Claude 1.1.0 lifecycle passed in isolated configuration. Codex 0.140.0 ignores
  a local root marketplace source, so the source uses the official repository URL shape.
  URL install fetched remote 1.0.0; final 1.1.0 source verification follows publication.
- Public-repository research is in `docs/research/distribution/`: six skill comparables,
  two optical repositories, MecAgent positioning, and official distribution guidance.
  Applied task-based navigation, relative owned images, observable results, direct support
  links, and a real synthetic-model figure. No student/course product scope was added.

- Released commit `82c7ef735c881b2d178e1786f719605989c0d0c4` as GitHub v1.1.0 and npm
  optical-design@1.1.0. All 11 jobs in CI run 34789239224 passed. The user completed npm's
  separate publish authorization. Registry integrity matched the tested tarball.
- Fresh public npm installs passed for all five agents; the downloaded demo passed optical
  acceptance and saved-model checks. Codex installed native 1.1.0 from GitHub, with all 76
  skill files matching, and removed it successfully in isolated configuration.
- GitHub and npm README image loading and documentation routing were verified in Chrome.
  GitHub About, homepage, and ten topics were updated. The social-preview asset is ready,
  but upload remains blocked by the browser extension's file access setting. No public
  curated catalog acceptance or Cursor UI installation is claimed.
- Publication receipt and checksums are attached to the GitHub release. This ledger update
  follows publication; it does not alter the tagged/published package bytes.
