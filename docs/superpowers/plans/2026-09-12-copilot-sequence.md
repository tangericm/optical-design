# Optical Copilot Implementation Plan

> Execute the approved audit sequence with test-driven development and independent review. The user approved the audit report's architecture and delivery order on September 12, 2026.

**Goal:** Deliver trustworthy numerical tools and a usable sequential-design audit/refocus workflow, followed by bounded tolerancing, catalog ingestion, domain references, and a portable backend.

**Architecture:** Preserve the five Tier 0 CLIs. Add a shared backend protocol and a job runner that opens a copy of a model, snapshots its state, evaluates explicit requirements, and saves a candidate only when a constrained improvement is verified. The OpticStudio adapter owns one standalone application per job and closes it in `finally`. A portable Optiland adapter uses the same job contract. GUI attachment and unrestricted generated-code execution are excluded from this first supported workflow.

**Stack:** Python 3.11+, uv script environments, numpy/scipy, pinned ZOSPy and Optiland adapters, pytest; existing npm packaging and skill lint.

## 1. Numerical correctness

- [x] Write failing tests for translated/annular pupils, correct physical sampling, exact defocus Strehl, and matched-pupil diffraction MTF.
- [x] Fix `scripts/_lib/fourier.py`, `wfmap.py`, and `wavefront.py`; preserve explicit pupil geometry, reject invalid arrays and sampling, and report approximation/model limitations.
- [x] Write failing tests for strict comparison coverage, units, mismatched analysis identities, invalid tolerances, and empty results.
- [x] Implement strict comparison in `compare.py`, preserving an explicit legacy shared-leaf mode for exploratory comparison.
- [x] Write failing tests for negative/nonfinite RMS, inconsistent NA/F-number, zero beam quality, zero cavity tilt, and invalid pass/grid/fit values.
- [x] Fix validation in `cli.py`, `resolve.py`, `zernike.py`, and `interfero.py`; distinguish measurement semantics and record provenance.
- [x] Run the focused tests, then all Python tests and package checks.

## 2. Native optical-design audit

- [x] Implement and test a specification parser in `_lib/design_contract.py`: fields, wavelengths, hard constraints, metric identifiers, explicit units, allowed focus interval, and deterministic budget.
- [x] Define `_lib/backends.py` protocol with `inspect` (including focus position), `evaluate`, `set_focus`, `save`, and context-managed cleanup. Return the same named metrics with explicit analysis settings from each adapter.
- [x] Implement `_lib/zos_backend.py` using ZOSPy 2.1.5 and the installed API. `zos.py check` reports actual connection/version/license and errors; audit jobs open only a copy in standalone mode.
- [x] Add `_lib/design_jobs.py` to hash source/spec/artifacts, create immutable baseline/candidate paths, evaluate requirements, write JSON and Markdown reports, and reject overwrites of the source.
- [x] Add `design.py audit --model PATH --spec SPEC --out DIR --backend zos --json`; record unavailable metrics as unsupported rather than passing them.
- [x] Verify against a generated synthetic singlet and an actual standalone OpticStudio connection if available. Never substitute a fake backend result for live optical evidence.

## 3. Constrained improvement

- [x] Test a deterministic focus search using an analytic backend fixture with an independently specified optimum, acceptance thresholds, budget, cancellation/failure recovery, and fixed invariants.
- [x] Implement bounded refocus in the shared job runner. Require explicit allowed focus travel and requirements. Analyze baseline/candidate with identical settings, preserve the best valid result, and verify the saved/reloaded candidate.
- [x] Add `design.py refocus` with a bounded evaluation budget and wall-clock deadline; source model remains untouched. Save discarded candidate evidence and explain no-improvement outcomes.
- [x] Demonstrate live OpticStudio baseline, focus adjustment, MTF/spot gain, preserved prescription invariants, and saved-model reanalysis.

## 4. Domain depth and tolerance evidence

- [x] Add application references for specifications/conventions, PSF/MTF validity, microscopy, OCT, interferometry, optimization, and tolerancing, using sources verified in the audit and current adapter documentation.
- [x] Add bounded uncompensated radius/thickness sensitivity and seeded Monte Carlo for declared perturbations supported by the adapter; report distributions, seeds, failures, pass fraction, and Wilson interval. Reject unimplemented perturbations explicitly.
- [x] Add local catalog-index validation and ranking by explicit optical constraints. Index entries retain vendor/part/source/model identity and dates; no automatic purchase or unlicensed model redistribution.
- [x] Add representative executable tasks with deterministic expected outcomes and clear scope limits.

## 5. Portable adapter and release integration

- [x] Implement Optiland adapter against a pinned installed version; support native JSON and a verified restricted Zemax-import subset. Inspect and reject unsupported file features before calling the converter.
- [x] Cross-check shared first-order metrics and simple lens behavior between engines; document physical-analysis differences rather than force numerical equality.
- [x] Update SKILL.md, README, tier/compatibility/security documentation, script help/examples, and packaging tests to advertise only shipped and verified behavior.
- [x] Run full tests, lint, package verification, live demos, source-preservation checks, and an independent code/scientific review. Address actionable findings before integration.
- [ ] Integrate verified changes into the original local checkout while preserving its untracked audit artifacts. No remote publication is part of this task.

## Verification commands

```powershell
uv run pytest -q
uv run ruff check skills tests
npm test
npm run lint:skills
npm run verify:package
```

Live backends use isolated pinned environments; their reports include exact versions and original numeric results. A failed license check is a reported limitation, not evidence that the implementation has run successfully.

## Delivery decisions and explicit limits

- This sequence delivers the first bounded optical-copilot release, not MecAgent feature parity.
- Tolerancing is deliberately uncompensated. Refocus is independently available; nested focus
  compensation, manufacturing distributions/correlations, and broader alignment variables remain
  future work rather than being represented as certified yield.
- Optiland native JSON and an exact catalog/material ZMX subset are verified. Full OpticStudio
  exports are rejected where unsupported metadata/apertures would otherwise be silently dropped.
- Same-process native shutdown output corrupted JSON in a live test. The CLI now runs its native
  engine in an owned worker process and returns a result-file payload after shutdown, retaining
  native diagnostics on stderr. API-level use remains available for integration tests.
- Standalone ownership, cooperative deadlines, source/artifact hashes and baseline/candidate
  save/reload evidence are verified. No GUI attachment, MCP server or remote publication is included.

Evidence: `docs/research/copilot-live/evidence-summary.md`; behavioral evaluation and review
findings are recorded in `docs/research/copilot-live/implementation-review.md`.
