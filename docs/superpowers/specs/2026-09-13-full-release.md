# Sequential imaging copilot: full-release contract

The user explicitly selected a complete sequential-imaging copilot and requested actual
feature development before release. Packaging readiness is not feature completeness.
Base: 2992500 (0.1.0-dev.5). Target: first stable full workflow release, 1.0.0.

## Product boundary

Complete the engineer's saved-prescription workflow: inspect physical model state, define
requirements and a multi-condition merit function, perform explicit controlled changes,
optimize, identify sensitivity, validate independently, and produce a usable design-review
package. Expose engineering jobs through the same CLI and MCP execution boundary. OpticStudio
is the primary native application; portable Optiland remains independently usable.

Native coverage extends to centered Standard conics and Even Asphere refractive surfaces,
with complete conic/coefficient provenance and preservation during radius/thickness edits.
Unsupported surface types, coordinate breaks, multi-configuration models, coatings,
non-sequential systems and unverified optical conventions must fail explicitly. Asphere
coefficients remain fixed during this release's optimization; no arbitrary native merit
operand editor, lens synthesis, stray-light or thermal solver is implied. The user selected
sequential imaging rather than synthesis/non-sequential scope. Active GUI mutation remains
outside the owned standalone execution contract; jobs operate on saved model copies.

## Completion gates

1. Composite merit: dimensionless weighted RMS distance to explicit targets over multiple
   supported metrics/fields/wavelengths/axes, with scales, positive weights and term evidence.
   Single-metric specifications remain compatible. Hard requirements always gate acceptance.
2. Model inspection without invented requirements; explicit radius/thickness edits require
   expected original values, preserve undeclared state and save/reload a reviewed candidate.
3. Local sensitivity: symmetric declared radius/thickness steps, per-metric derivatives,
   finite-step effects and nonlinearity indicators, optional objective sensitivity; no
   cross-unit ranking or manufacturing yield claim.
4. Review package: verified receipt input, prescription changes, baseline/candidate metrics,
   full field/spectral checks, sensitivity where present, and an honest schematic layout.
   Standalone HTML and readable Markdown; escape untrusted text and preserve failure status.
5. Native conic/Even Asphere coverage with API readback, coefficient invariants, saved reload,
   independent geometry/numerical tests and live examples. Portable unsupported inputs reject.
6. Agent workflow: documented inspection → explicit changes/optimization → independent
   validation → sensitivity → report, with installed-client scenarios and evidence-backed
   suggestions. No unsupported command or guessed result in the skill routing.
7. Full verification: analytic regression anchors, native/portable and actual MCP jobs,
   failure restoration/cancellation/receipt checks, independent reviews, package/client
   installation and hosted CI. Preserve the unresolved real OCT method discrepancy.
8. Stable release: reconcile capability claims, freeze version and artifacts, publish the
   authorized GitHub release, then verify `npx skills add` against the public revision.

Each gate needs executable evidence; test count alone does not satisfy it. A failed physical
requirement stays failed. A design with insufficient supported degrees of freedom may have
no acceptable candidate. Completion never means all prescriptions can be optimized.

## Architecture and constraints

Python 3.11+, existing NumPy/SciPy; optional Optiland 0.6.2, ZOSPy 2.1.5/pythonnet 3.1.0,
MCP 2.2.0. Reuse typed contracts, owned workers, exact input snapshots, shared budgets and
source restoration. Do not add another LLM service or ray tracer. New jobs retain report
schema 1 with explicit action/status, source identity, baseline_model and hashes.

Composite objective shape: `direction: minimize`, `aggregation: weighted_rms`, `terms`.
Each term supplies the supported metric identity, exact unit, finite target, positive
scale in that unit, and positive weight. Merit is sqrt(sum(w*((value-target)/scale)^2)/sum(w)).
`minimum_gain` is dimensionless for this objective. Report every term and reject missing,
duplicate, nonfinite or wrong-unit measurements. Existing scalar objectives keep their units.

Sensitivity configuration: schema 1, `parameters`, each with surface, parameter and step_mm.
Edits configuration: schema 1, `changes`, each with surface, parameter, expected_mm, value_mm.
Supported adjustable cells remain radius_mm/thickness_mm on real non-image surfaces.
Expected value checks prevent stale edits. Typed operation plans contain data, never code.

No changes to the separate user optical repository or untracked original audit directory.
Retain evidence worktrees because recorded receipts reference them. Remote publication is
authorized by the user's request, but occurs only after feature and release gates pass.
