# optical-design skill — design spec

Date: 2026-09-12
Status: approved in brainstorming; awaiting implementation plan
Repo: `github.com/tangericm/optical-design` (MIT). npm: `optical-design` (free as of 2026-09-12).

## 1. Purpose

An open-source agent skill that gives a coding agent (Claude Code, Codex, Cursor, Hermes,
OpenCode, Copilot, and any Agent Skills-compatible harness) production-grade help with
optical design and optimization questions: resolution, PSF, MTF, wavefront error, Zernike
aberrations, Strehl, tolerancing, merit-function design. It ships deterministic Python
scripts so numbers come from code, not from the model, and it interoperates with
Ansys Zemax OpticStudio through ZOS-API while working fully without it.

Application domains with dedicated reference material in v1: **OCT, microscopy,
interferometry**. Astronomy is deferred (only the shared telescope resolution rules in the
core references).

## 2. Non-goals (v1)

- Non-sequential / illumination design, stray light, coatings, thin-film design.
- Mechanical/opto-mechanical design, thermal analysis.
- A new MCP server. Existing community ZOS-API MCP servers are noted in `references/opticstudio.md`;
  this skill drives OpticStudio through scripts instead. An MCP wrapper can be a later phase.
- Owning a ray tracer. Tier 1 delegates sequential ray tracing to `optiland`.
- Astronomy-specific references (seeing, obscuration budgets, segmented apertures).

## 3. Decisions taken during brainstorming

| Decision | Choice | Why |
|---|---|---|
| Runtime shape | Knowledge (SKILL.md + references) + deterministic scripts | Robust numbers need code; MCP adds hosting burden without adding knowledge |
| Compute layering | Tier 0 numpy/scipy, Tier 1 optiland, Tier 2 ZOSPy | Closed-form checks stay independent of any ray tracer; OpticStudio optional |
| Distribution | npm package + `npx skills add` + Claude plugin marketplace + Agent Plugins 1.0 `plugin.json` | Same proven pattern as skillcrit; cross-harness |
| Cross-harness | Spec-portable frontmatter only | Claude-only fields are stripped elsewhere and would confuse Codex/Cursor/Hermes |
| Python deps | PEP 723 inline metadata, `uv run` | No pre-install step; harness just copies files |
| ZOS-API bridge | ZOSPy 2.1.5 over pythonnet 3.1 | Probe on this machine: OpticStudio 2024 R1 Premium, Python 3.13.7, standalone mode works, FFT MTF returned data |
| Name | `optical-design` | Descriptive; free on npm and GitHub |

## 4. Repository layout

```
optical-design/
├── package.json                    # name optical-design, no bin, files: skills/ docs/ LICENSE SECURITY.md
├── plugin.json                     # Agent Plugins 1.0 schema (Cursor/Codex/others)
├── .claude-plugin/marketplace.json # Claude Code marketplace entry
├── skills/optical-design/
│   ├── SKILL.md                    # < 400 lines
│   ├── LICENSE
│   ├── references/                 # one level deep, each < 300 lines, ToC at top
│   ├── scripts/                    # Python; every script `--help`, `--json`
│   │   └── _lib/                   # shared: units, schema, zernike tables, io
│   ├── assets/                     # sample prescriptions + glass subset
│   └── evals/evals.json            # skill-creator eval format
├── tests/
│   ├── python/                     # pytest; markers: tier0, tier1, zos
│   └── node/                       # frontmatter + packaging checks (vitest)
├── docs/
│   ├── install.md                  # per-harness install paths
│   ├── compatibility.md            # claimed vs observed table (skillcrit style)
│   ├── tiers.md                    # what each tier needs and returns
│   ├── verification.md             # local ZOS cross-check results per release
│   └── superpowers/specs/, plans/
├── CHANGELOG.md, SECURITY.md, CONTRIBUTING.md, LICENSE, README.md
└── .github/workflows/ci.yml
```

## 5. Frontmatter (portable)

```yaml
---
name: optical-design
description: >
  Analyze and optimize optical systems: resolution limits, PSF/MTF, wavefront error,
  Zernike and Seidel aberrations, Strehl, depth of focus, Gaussian beams, tolerancing and
  merit-function design. Use when the user asks about lens or imaging system performance,
  OCT/microscopy/interferometer optics, Zemax OpticStudio files (.zmx) or ZOS-API analyses,
  or wants numbers checked against diffraction limits — even if they do not name a tool.
license: MIT
compatibility: Requires Python 3.11+ and uv. Tier 1 needs optiland (auto-installed). Tier 2 needs Windows + Ansys Zemax OpticStudio Professional/Premium (ZOS-API).
metadata:
  author: Eric Tang
  repo: https://github.com/tangericm/optical-design
  version: "0.1.0"
---
```

Constraints: `name` matches directory; description ≤ 1024 chars, trigger-only, no workflow
summary; `compatibility` ≤ 500 chars.

## 6. SKILL.md content architecture

Sections, in order:

1. **What this skill does / does not** (10 lines). Not-for list: non-sequential/illumination,
   coatings, mechanical, general physics homework without a system.
2. **Workflow.** Classify the question → pick tier → run script → interpret with the matching
   reference → report with units and conventions stated.
   - Closed-form question (resolution, DOF, Gaussian beam, Strehl from RMS) → Tier 0.
   - Prescription available (.zmx/.seq/.len or surfaces typed by user) → Tier 1.
   - OpticStudio present and user wants the live file analyzed or optimized → Tier 2.
   - Always cross-check Tier 1/2 numbers against a Tier 0 diffraction limit.
3. **Preflight.** `uv --version`; `uv run scripts/zos.py check` before any Tier 2 claim.
   Never state that OpticStudio ran when `check` failed.
4. **Conventions.** Lengths in mm unless stated, wavelengths in µm, wavefront in waves at the
   stated λ, Zernike coefficients always reported with convention (Fringe/Noll/ANSI) and
   normalization radius. F/# vs NA conversion rule. Sign conventions pointer.
5. **Sanity rules** (the part agents most often get wrong):
   - Strehl and RMS WFE must agree with Maréchal within the approximation's validity.
   - Measured/simulated MTF never exceeds the diffraction-limited curve.
   - PSF sampling must satisfy Nyquist for the reported cutoff.
   - Report both geometric and diffraction numbers when they disagree, and say which governs.
   - Quote the source of every formula (reference file + section).
6. **Script index.** One line per script with when to use; `--help` for details.
7. **Reference index.** One line per reference file.
8. **Reporting template.** Short table: quantity, value, unit, method/tier, limit it is compared to.
9. **Red flags.** Rationalizations to refuse: "diffraction limit is close enough", "Zernike
   convention doesn't matter here", "I'll estimate the PSF instead of running the script".

## 7. References

| File | Contents |
|---|---|
| `aberrations.md` | Seidel S_I–S_V, wavefront ↔ transverse relation, field/aperture dependence, balancing, sign conventions, chromatic |
| `zernike.md` | Fringe/Standard(Noll)/ANSI ordering + normalization tables (first 37 terms), conversion rules, unit-circle radius pitfalls, RMS from coefficients |
| `psf-mtf-strehl.md` | Airy, Rayleigh/Sparrow/Abbe/Dawes, MTF cutoff, Maréchal, extended Strehl, sampling/Nyquist, obscuration effect |
| `resolution-dof.md` | NA/F# relations, DOF conventions (±2λF² half-range vs 4λF² full-range, with citation), Gaussian beam relations, pixel matching |
| `oct.md` | axial/lateral resolution, confocal parameter, line-field beam shaping, spectrometer/k-linearization, dispersion, sensitivity roll-off |
| `microscopy.md` | objectives (infinity-corrected, tube lens), coverslip/immersion, illumination NA, confocal/2P scaling, Nyquist sampling |
| `interferometry.md` | Fizeau/Twyman-Green, N-step PSI algorithms, fringe → wavefront, cavity/retrace error, test-plate matching, Zernike fitting of measurements |
| `optimization.md` | merit-function design, OpticStudio operand names, variables/constraints, local vs hammer vs global, stopping rules |
| `tolerancing.md` | sensitivity vs Monte Carlo, compensators, typical budgets, reading yield |
| `opticstudio.md` | ZOS-API tiers/modes, analysis → ZOSPy mapping, .zmx structure, glass catalogs, unit traps, ZPL vs API, existing MCP servers |
| `glossary.md` | terms and symbols |

Rules: each formula carries a cited source, validity range, and a worked example that is also
a test in `tests/python/`. Tables over prose. No reference points to another reference.

## 8. Scripts

Shared contract:

- Invocation `uv run scripts/<name>.py <subcommand> [args] [--json]`.
- `--json` → single JSON object on stdout matching `_lib/schema.py` (`{tool, tier, inputs,
  results, units, method, warnings}`); without it, a human-readable table.
- Exit codes: 0 ok; 2 usage; 3 tier dependency missing (message names the dependency and how to
  get it); 4 analysis failed.
- Every subcommand has `--help` with one example.
- PEP 723 header pins deps per script (`numpy`, `scipy`; `optiland` for trace.py; `zospy`
  for zos.py). Windows-only marker on zos.py.
- No harness-specific code. No network calls.

| Script | Tier | Subcommands |
|---|---|---|
| `resolve.py` | 0 | `airy`, `rayleigh`, `dof`, `gaussian` (w0/zR/θ/w(z)), `oct-axial`, `oct-lateral`, `micro` (0.61λ/NA + Nyquist pixel), `telescope` (Rayleigh/Dawes) |
| `zernike.py` | 0 | `convert` (fringe↔noll↔ansi), `rms` (coeffs → RMS, PV), `strehl` (Maréchal + extended), `seidel-from-zernike`, `fit` (map → coeffs) |
| `wavefront.py` | 0 | `psf` (map or Zernikes → FFT PSF, Strehl, encircled energy), `mtf` (with diffraction-limit overlay), `sample-check` |
| `interfero.py` | 0 | `psi` (N-step phase shift → phase), `unwrap`, `fringe-to-wfe`, `cavity` |
| `trace.py` | 1 | `load` (.zmx/.seq/.len → summary), `paraxial`, `seidel`, `spot`, `rayfan`, `wavefront`, `zernike`, `psf`, `mtf`, `sensitivity` |
| `zos.py` | 2 | `check`, `open`, `analyze <fft-psf\|huygens-psf\|mtf\|zernike-std\|zernike-fringe\|wavefront\|spot\|seidel\|pop>`, `merit`, `optimize`, `export` |
| `compare.py` | 0 | diff two JSON results with tolerances (tier1 vs tier2, before vs after) |

Tier 2 safety: `--mode standalone` default, `--mode extension` to attach to an open GUI.
Read-only by default; `optimize` and any write need `--write`, otherwise results go to a
save-as copy next to the original. `check` reports license edition, API version, mode.

## 9. Assets

- `singlet.zmx`, `doublet.zmx` (Tier 1/2 cross-check fixtures with known Seidel/Zernike values).
- `oct-sample-arm.zmx` (fiber → collimator → scan lens, anonymized from the line-field project).
- Minimal `.agf` glass subset (N-BK7, N-SF11, fused silica) for offline Tier 1 runs.
- Sample wavefront map and 4-step interferogram set for Tier 0 tests.

## 10. Testing and evals

- `pytest` markers `tier0` (always), `tier1` (installs optiland), `zos` (Windows + license; skipped in CI, run locally before release, results in `docs/verification.md`).
- Tier 0 tests pin textbook values: Airy 1.22λF#, Maréchal λ/14 → 0.80, Zernike table round trips, RMS from coefficients, PSI 4-step recovers known phase.
- Tier 1 tests: singlet Seidel vs analytic thin-lens, doublet Zernike vs stored reference.
- Tier 2 tests: same fixtures through OpticStudio; `compare.py` within tolerance.
- Node tests: frontmatter fields/limits, package `files`, plugin manifests valid JSON, `skills-ref validate`, `skillcrit lint` clean.
- Evals: `evals/evals.json`, ~12 prompts, 4 should-not-trigger; run with/without skill via subagents before 0.1.0 (skill-creator loop).
- CI: ubuntu/macos/windows × Python 3.11 and 3.13; Node 22 for packaging tests.

## 11. Delegation and model routing

| Work | Route |
|---|---|
| Spec, SKILL.md architecture, formula source-of-truth review, Tier 2 design, final audit | Highest tier (Fable 5.1; Opus 5 if usage exhausted) |
| Reference drafting from cited sources; script implementation per subcommand; tests; docs | Balanced (Sonnet), medium–high effort |
| ToCs, table formatting, packaging files, CHANGELOG, mechanical fixes | Economy (Haiku) |

Every reference file gets a fact-check pass by a second agent before final audit. Commits are
authored as Eric Tang only; no AI co-author trailers, subagents included.

## 12. Phases

1. Scaffold, packaging, Tier 0 scripts + tests, CI green.
2. References (11 files) with fact-check.
3. Tier 1 (optiland) scripts, fixtures, tests.
4. Tier 2 (ZOSPy) scripts, cross-check against Tier 1, `docs/verification.md`.
5. SKILL.md final, evals, harness install trials (Claude Code, Codex, Cursor; Hermes if available), docs, 0.1.0 release.

## 13. Open items

- Depth-of-focus prefactor convention: cite a primary textbook (Smith, *Modern Optical Engineering*) and encode both half-range and full-range explicitly.
- Confirm optiland `.zmx` import handles the line-field project files (aspheres, multi-config) before promising `.zmx` support beyond Standard/EvenAsph surfaces.
- Hermes install path and discovery behavior: documented from skillcrit's compatibility table, trial only if a Hermes install exists.
