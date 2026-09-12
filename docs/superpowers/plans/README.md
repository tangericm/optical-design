# optical-design implementation roadmap

Spec: `docs/superpowers/specs/2026-09-12-optical-design-skill-design.md`.
The spec has six phases. Each phase is its own plan and ships working, tested software.
Plans 2–6 are written when their phase starts, against the code that actually landed.

| Plan | Phase | Delivers | Status |
|---|---|---|---|
| `2026-09-12-plan-1-scaffold-tier0.md` | 1 | Repo scaffold, npm/plugin packaging, Tier 0 scripts (`resolve`, `zernike`, `wavefront`, `interfero`, `compare`), pytest + vitest, CI, SKILL.md draft | written |
| plan-2-core-references | 2 | 11 core references with citations, worked examples tied to tests, second-agent fact check | pending |
| plan-3-tier1-optiland | 3 | `trace.py` (load/paraxial/seidel/spot/rayfan/wavefront/zernike/psf/mtf/sensitivity/edit/optimize/export), fixtures, tests | pending |
| plan-4-design-guidance | 4 | 5 guidance references, `design.py` (audit/suggest/budget/spec), `catalog.py`, `compare.py --report`, flawed-doublet fixture | pending |
| plan-5-tier2-zospy | 5 | `zos.py` (check/open/analyze/edit/merit/optimize/export), Tier 1↔2 cross-check, `docs/verification.md` | pending |
| plan-6-release | 6 | Final SKILL.md (five modes), evals, harness install trials, docs, 0.1.0 release | pending |

Model routing for execution (from spec §11): top tier for plan writing, review gates, and audit;
Sonnet for implementing tasks; Haiku for mechanical tasks (manifests, ToCs, CHANGELOG).
