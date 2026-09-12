# Remaining Optical Copilot Roadmap

> For agentic workers: use subagent-driven-development and independent review. The user
> authorized continuation of the remaining roadmap. Continue through all four deliverables.

**Goal:** Deliver bounded multivariable optimization, explicit focus-compensated tolerance
evidence, an interactive tool interface, and controlled investigation of the OCT discrepancy.

**Architecture:** Reuse the typed design/backend contracts and owned CLI workers. Keep each
new job source-preserving, budgeted and independently verifiable. A thin MCP interface
dispatches the same CLIs rather than implementing a second optical execution engine.

**Stack:** Python 3.11+, existing NumPy/SciPy, pinned optional engines, official MCP Python SDK.

## Scope and design decisions

The first two plans are complete. This plan covers the later roadmap, not another rerun of
the 75-case baseline. Native and portable optimization remain limited to the validated
centered spherical sequential adapters. Radius and thickness are explicit bounded variables;
arbitrary generated code, surface topology changes and GUI attachment are outside this slice.

Compensation means an explicit bounded final-air-gap search for each perturbed trial.
Report uncompensated and compensated outcomes on identical draws, failure counts, evaluation
budgets and conditional Wilson intervals. Do not label this a manufacturing yield guarantee.

Interactive tools expose capabilities and owned job start/status/cancel/results over stdio.
Constrain writes to a declared workspace and input reads to declared roots. Serialize jobs;
never accept shell text, attach to an editor or terminate unrelated processes. Use the same
native subprocess boundary as the CLI. Job completion and optical acceptance are separate.

The OCT work is a read-only computational investigation on copies, not a prescription change.
Isolate Huygens pupil/image controls and POP physical pitch/window changes at 840 nm; retain
native readbacks, common profile support and source hashes. Missing measured source/cube data
remain explicit validation limits. Do not use this model as optimizer acceptance evidence.

## Task 1: Bounded multivariable optimization

Files: new `_lib/optimization.py`, CLI integration in `scripts/design.py`, focused tests and
`references/optimization.md`. Reuse get/set_parameter, inspect, evaluate, save/load and assess.

- [x] Write failing analytic tests for a coupled two-variable optimum, bounds, infeasible
  candidates, ignored/coupled edits, fixed invariants, budgets, failure restoration and reload.
- [x] Implement `run_optimization_job(model, spec, out, factory, variables)` with strict
  radius_mm/thickness_mm variable declarations, finite bounds, small dimensionality, normalized
  bounded search, best feasible retention and verified saved-candidate improvement.
- [x] Expose `design.py optimize --variables variables.json` through existing native isolation.
- [x] Verify a genuine two-variable native and portable example; review independently.

## Task 2: Explicit compensation

Files: `_lib/tolerancing.py`, optional new `_lib/compensation.py`, tolerance tests and reference.

- [x] Write failing tests where perturbation worsens a known focus metric and bounded focus
  compensation recovers it, plus bound/readback/budget/failure and baseline-reset regressions.
- [x] Add optional strict `compensator` configuration; absence preserves current behavior.
  Keep nominal and each trial's uncompensated evidence and best accepted compensated result.
- [x] Report paired Monte Carlo outcomes, actual search settings/evaluations and failures.
- [x] Run live native/portable demonstrations on identical seeds; review independently.

## Task 3: Interactive tool transport

Files: new `_lib/tool_jobs.py`, `scripts/server.py`, focused tests, new interactive reference.

- [x] Research the official MCP SDK API and pin a verified version.
- [x] Write failing tests for operation allowlists, workspace/input-root confinement, stale
  model hashes, one active job, job identity, exit/receipt agreement, cancellation and cleanup.
- [x] Implement capabilities/start/status/cancel/results operations using allowlisted argv
  and owned CLI processes. Confine artifacts and retain logs; reject partial acceptance.
- [x] Exercise actual MCP client/server calls and a real optical job through the interface.

## Task 4: Optical experiment and release integration

Files: research evidence under `docs/research/next-roadmap/`; existing native profile adapter
only changes if a demonstrated requirement needs a tested extension.

- [x] Run matched 840 nm Huygens controls and POP sampling/window controls on copied Stock.
- [x] Quantify which changes affect widths, grid pitch and the method discrepancy; identify
  remaining source, intermediate-diffraction and measurement uncertainty without overclaiming.
- [x] Update routing, compatibility, package coverage, versions and reproducible examples.
- [x] Run meaningful full/optional/native/MCP checks; independent final review and local
  integration, preserving original optical models and the untracked initial audit directory.

## Verification / ledger

Baseline: main `dfb510a`; expected existing suite 451 passed, 34 optional skips. New worktree
`optical-design-next`, branch `feat/optical-copilot-next`. Root owns shared release files and
scientific experiments; implementers own disjoint task files and do not commit shared state.
Record red/green evidence and review decisions here as tasks finish. No remote publication.


## Execution ledger

- Task 1: initial 25 missing-feature failures, then passing analytic and edge tests;
  three additional axial/readback failures fixed. Independent review clean, 87 focused
  pinned-engine tests passed. Native and portable 81-evaluation examples changed both variables,
  passed hard requirements, reloaded saved candidates and preserved sources.
- Task 2: initial nine missing-config failures; compensation implemented and hardened against
  analysis mutation and axial corruption. Independent review clean, 102 focused tests passed.
  Identical eight seeded draws: native 1/8 to 8/8, portable 2/8 to 8/8; 300 analyses per job.
- Task 3: 30 transport/official MCP tests passed, one Windows symlink capability skip;
  independent security review clean under the documented trusted-local-writer threat model.
  Fixed SECURITY wording distinguishing cooperative CLI budgets from force-cancelled MCP jobs.
- Root native identity regression: two failing tests showed silent wrong-file loads accepted;
  fixed actual SystemFile verification; 11 tests passed, two live tests deferred to native gate.
- Scientific controls: five native cases completed, full copied-model/raw/dependency hashes
  verified independently. Pupil/image controls changed X width by <0.2%; tested POP controls
  by <0.5%. The approximately22% method discrepancy persists. Reducer review requested explicit
  unit, wavelength, model and control-identity checks; these were added and verified.
- Full optional-engine/MCP suite: 583 passed, three environment-dependent skips. Seven npm
  tests passed, skill lint and package installation passed; Ruff passed after import formatting.
- Routing walkthroughs checked optimize, compensated tolerance and unsupported OCT redesign;
  these are behavioral read/review scenarios, not autonomous-design performance benchmarks.
- Ruling: retain original broad six-phase proposal as history; use explicit validated backend
  APIs for this release rather than inventing generic commands without scientific acceptance.
- Ruling: baseline may be outside optimization bounds; every applied search/candidate vector
  must be inside them. This supports correcting the intentionally defocused example.
- Ruling: conditional small-sample compensation is evidence of workflow execution, not a
  manufacturing yield guarantee. Unmeasured OCT source/cube behavior remains an external limit.

- Final native/portable/MCP suite with OPTICAL_DESIGN_LIVE=1:585 passed, one Windows
  symlink-capability skip. Native MCP audit passed after explicit trusted host environment
  inheritance; exact omitted restricted-environment prerequisite remains unisolated.
- Native MCP cancellation verified on a running tolerance job: owned OpticStudio process
  gone, unrelated sleeper alive, source unchanged, cancelled state and report null.
- Native/portable receipt verifier and hardened optical reducer passed; external optical
  repository six preservation tests passed and Git tree remained unchanged.
- Ruling: local fast-forward integration follows the user's continued authorization and
  the established sequence. Preserve evidence worktrees and the untracked original audit;
  no push, remote publication, global tool configuration or model modification.
