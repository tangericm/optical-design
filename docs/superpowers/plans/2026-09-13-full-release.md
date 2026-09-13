# Full Sequential Imaging Release Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for independent
> tasks, with scoped review and broad final review. Continue through completion gates.

**Goal:** Complete the selected sequential-imaging copilot workflow before stable release.
**Architecture:** Extend the existing contract/backends/jobs, preserving CLI/MCP ownership.
**Tech stack:** Python 3.11, NumPy/SciPy, pinned Optiland/ZOSPy/pythonnet/MCP, standalone HTML.
**Spec:** `docs/superpowers/specs/2026-09-13-full-release.md`.

## Global constraints

Use the spec's exact runtime pins, typed data-only requests and source-copy invariants.
Root owns shared CLI/MCP/release integration and every native engine run. Agents do not
launch native engines concurrently or edit shared release files. Do not commit another
worker's changes. Tests precede production changes; scientific results require live evidence.

## Task 1 — Composite merit (independent)

Files: `_lib/design_contract.py`, `_lib/optiland_backend.py`, `_lib/optimization.py`,
`_lib/design_jobs.py`, `_lib/compensation.py`, tests and `references/merit-functions.md`.

- [ ] Tests: multiple units/scales, weights, invalid terms, missing/duplicate/wrong-unit
  measurements, overflow, legacy compatibility, analytic multi-condition optimum and reload.
- [ ] Add objective_metrics / objective breakdown APIs and weighted RMS evaluation.
- [ ] Both backends request all objective measurements; all job families use same evaluator.
- [ ] Preserve per-term evidence in baseline/candidate/history where objective evaluated.
- [ ] Focused tests, review and live two-engine examples (root).

## Task 2 — Review packages (independent)

Files: new `_lib/review_report.py`, `scripts/review.py`, tests, `references/review-reports.md`.

- [ ] Tests for valid/failed/rejected receipts, hash/path mismatch, duplicate/missing data,
  HTML escaping and truthful baseline/candidate status.
- [ ] Render new output directory with report.html, report.md, provenance manifest.
- [ ] Include metric comparison, requirement failures, parameter changes, field/wavelength
  plots, sensitivity when present and labeled schematic (never invented ray tracing).
- [ ] Test installed CLI and visually inspect representative reports (root).

## Task 3 — Sensitivity (independent)

Files: new `_lib/sensitivity.py`, tests, `references/sensitivity.md`.

Interface: `run_sensitivity_job(model, spec, out, factory, perturbations, *, cancelled=None)`.
Returns action sensitivity/status completed, standard source/baseline artifacts, baseline,
trial measurements and per-metric sensitivities/rankings. No accepted changed candidate.

- [ ] Analytic derivative, finite-step effects, nonlinear response, invalid steps, ignored
  edits, state mutation, unavailable metrics, budgets, cancellation, restoration/reload tests.
- [ ] Central differences at declared ±step, actual parameter/invariant readbacks, retain
  both trial rows, rank only within identical metrics or one defined objective.
- [ ] Use shared budgets; restoration outside deadlines; failure receipt on execution error.
- [ ] Root integrates CLI/MCP and exercises both engines.

## Task 4 — Native conics and even aspheres (root)

Files: `_lib/zos_backend.py`, native contract tests and fixtures/reference.

- [ ] Inspect installed API metadata; read all shape coefficients and coefficient solves.
- [ ] Tests for unsupported types/solves, coefficient mutation, sag conventions and reload.
- [ ] Enable only verified centered refractive shapes; existing edits preserve full shape.
- [ ] Live audit/optimization and saved reload on synthetic conic/asphere cases.

## Task 5 — Inspection and explicit edits (root)

Files: new `_lib/model_actions.py`, tests, `references/model-actions.md`.

- [ ] Inspection without spec: copied model snapshot, physical model inventory and hashes.
- [ ] Explicit edits with expected original values; full parameter/invariant readback;
  evaluate against spec, save/reload and assess. Failed requirements retain rejected artifact.
- [ ] Tests cover stale changes, invalid cells/values, loss of invariants, restoration and
  teardown, source protection and accepted/rejected actual engine cases.

## Task 6 — CLI/MCP and agent workflow integration (root)

Files: design.py, server.py, _lib/tool_jobs.py, _lib/native_worker.py, SKILL.md and examples.

- [ ] Add inspect/edit/sensitivity actions and strict matching input pairs/hashes.
- [ ] Job result validation binds action, inputs/spec/config, evidence and acceptance.
- [ ] Actual MCP calls for each new action and invalid/stale/cancelled cases.
- [ ] Update skill routing, complete two unseen engineering workflow scenarios, report
  scientific limitations and leave unsupported configurations explicit.

## Task 7 — Full verification and release

- [ ] Record live composite/native shape/model-action/sensitivity/report evidence.
- [ ] Independent scoped reviews and final branch review; fix findings.
- [ ] Full Python/package tests; fresh skill install and portable/MCP smoke tests.
- [ ] Update compatibility, full release docs/version, distributable artifact checks.
- [ ] Integrate locally; publish authorized GitHub release; hosted CI passes.
- [ ] Verify public `npx skills add` installation and run installed numerical/portable tools.

## Ledger

- Initial state: 2992500, dev.5; 614 passed/1 platform skip in last live-enabled suite.
- User selected complete sequential imaging scope; synthesis/non-sequential excluded.
- Ruling: existing source-preserving standalone workflow remains the session model; adding
  unrestricted GUI editing would require a different state/ownership contract.
- Ruling: centered conics/even aspheres expand native model analysis; shape coefficients
  remain fixed while radius/thickness are adjusted. Unsupported prescriptions remain explicit.
