# Compatibility

## Unreleased adoption repairs

The source checkout adds the guided walkthrough, installation lifecycle repairs, shared
import-fidelity assessment and corrected first-order/report contracts. Runtime pins remain
Optiland 0.6.2 and the native versions recorded below. `bfl_mm` now means back focal length,
not the final air gap; use `image_distance_mm` for that previous value. Explicit paraxial
metric names retain documented legacy aliases. Versioned reviews accept legacy summaries
where unambiguous, but reject contradictory pass flags and invalid numerical requirements.

The npm version and published v2.0.0 tag remain unchanged until a new release is cut.
Use this checkout to exercise unreleased commands. These repairs do not establish new
OpticStudio-version or agent-host compatibility; the historical records below retain
their original version scope.

### Verification of these repairs

On Windows with Python 3.11 and Optiland 0.6.2, the portable Python suite passed
**941 tests**, with one skip and six native tests deselected. Execution was split
between the broad suite (887 passes), all recipe tests (15), report renderer (37),
and walkthrough tests (2). The Node suite passed **56 tests**, with one platform skip.
Type checking, Ruff, skill lint, and documentation file links passed.

The npm tarball was installed into a fresh consumer. Managed installation, update,
and uninstall passed for all five supported agent destinations. The installed Codex
copy ran the calculator and real walkthrough; its candidate and review remained
after uninstall. The packed audited demo also passed. These are installer and tool
checks, not new verification inside every agent host.

The walkthrough measured every configured field/wavelength pair after save/reload;
its plots were visually checked with matching before/after axes. New regressions
cover unsupported import content, non-mm gates, corrected BFL, overflow and invalid
requirements, conflicting report evidence, and ownership-preserving cleanup.

No new cross-model benchmark, beginner participant pilot, marketplace acceptance,
or native optical-engine compatibility result is claimed. The evaluation protocol
and public development cases are ready for those separate studies.

## 2.0.0

The 2.0.0 reframing changes documentation, adds the recipes, forms, evals and three thin
scripts (`inspect_zmx.py`, `first_order.py`, `render_review.py`), and leaves the audited
mode's optical algorithms and engine pins unchanged, so the 1.1.0 verification below still
describes them. New scripts are covered by the Optiland-tier tests in CI.

Raw release evidence (job receipts, logs, rendered reviews) is retained in the repository
history at the [v1.0.0](https://github.com/tangericm/optical-design/tree/v1.0.0/docs/research)
and [v1.1.0](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research) tags rather
than on the main branch.

## 1.1.0 distribution verification

The distribution release preserves the 1.0.0 optical algorithms. On the Windows release
host, 42 Node tests passed with one Darwin-only test skipped. The packed npm artifact
passed clean install, update, and uninstall checks for all five installer targets, and
ran the portable demo through saved-candidate acceptance and HTML review generation.
The Codex manifest validator and skill lint passed.

Claude Code 2.1.260 installed and removed the local 1.1.0 plugin in a temporary
configuration. Codex 0.140.0 installed and removed version 1.1.0 from the published GitHub
marketplace; all 76 installed skill files matched the release source. Cursor's manifest is checked structurally;
this is not a verified Cursor UI installation or an accepted public catalog listing.

[All 11 release CI jobs passed](https://github.com/tangericm/optical-design/actions/runs/34789239224)
at commit `82c7ef735c881b2d178e1786f719605989c0d0c4`, including packed demo checks on
Windows, macOS, and Linux. npm 1.1.0 was published with integrity matching the verified
tarball. Fresh public npm installs passed for all five targets, and the downloaded package
completed the optical demo with saved-candidate verification. The
[1.1.0 release](https://github.com/tangericm/optical-design/releases/tag/v1.1.0) includes
the tarball, checksums, and a machine-readable verification receipt.

## 1.0.0 optical workflow evidence

Stable workflow evidence recorded September 13, 2026. Historical development records follow.

The 1.0.0 release adds inspect/edit, composite merit, local sensitivity and review packages
to the complete saved-prescription workflow. Native centered Standard conics and
EvenAspheric A2–A16 terms are retained, with independent native/analytic sag anchors and
saved-reload regression checks. These terms remain fixed during optimization. Portable
coverage remains its documented spherical/plane subset. New model types and API versions
still require explicit verification.

The final local suite passed **837 tests**, with two platform skips (Windows symbolic-link
capability and the POSIX-only process observer),
using Optiland 0.6.2, MCP 2.2.0 and enabled native OpticStudio tests. Seven npm tests, Ruff,
skill lint and tarball install checks passed. Isolated project-scoped `npx skills` installations
exercise the shipped workflow and compare every installed file hash with the release source.
These are scripted installed-workflow checks, not autonomous external-client benchmarks.

See [full-release receipts and limitations](https://github.com/tangericm/optical-design/blob/v1.0.0/docs/research/full-release/README.md), including
two-engine composite searches, actual MCP actions, failures retained as rejections and
source/artifact integrity checks. HTML has structural/escaping tests; browser visual review
was unavailable because local-file navigation was blocked by the browser policy.

| Surface | Evidence | Boundary |
|---|---|---|
| Windows, Python 3.11 | Full pytest suite, CLI examples, npm package checks | Other configured CI platforms were not rerun locally |
| OpticStudio 2024 R1, API 24.1.0, Premium | Fresh standalone connection; real audit/refocus/optimize/compensated tolerance; saved-model reload and source hashes | No live GUI attachment or broad prescription coverage |
| ZOSPy 2.1.5 / pythonnet 3.1.0 | Installed API calls exercised | Different suite/API versions need validation |
| Native profile benchmark | 75 Huygens/POP cases across three real OCT models; 135 profiles; two final-CLI smoke cases | Same-method reproduction, not independent physical acceptance or unrestricted model coverage |
| Optiland 0.6.2 | Native JSON, restricted ZMX regression fixtures, real audit/refocus/optimize/compensated tolerance | Full OpticStudio exports can be rejected; import is deliberately narrow |
| Agent skill entrypoint | Independent before/after behavioral scenarios for defocus, annular MTF, refocus and yield | Not an autonomous-design benchmark |
| npm tarball | Local pack/install verification | No registry publication in this development change |

The synthetic N-BK7 singlets are independently constructed from matching prescriptions.
Shared first-order and geometric spot checks are evidence; FFT MTF uses different pupil
sampling implementations. Numerical results from the current run are in the local
[`docs/research/copilot-live/` in the v1.1.0 tag](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research/copilot-live) evidence directory, which is excluded from distribution.

Any Agent Skills client can read the portable frontmatter. End-to-end installations in
every named client have not been tested. Pin the adapter versions and rerun capability
checks when moving to another machine.

The 0.1.0-dev.2 profile workflow retains reference comparisons, native setting readback,
source/dependency hashes and raw profiles in local [`docs/research/real-benchmark/` in the v1.1.0 tag](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research/real-benchmark) evidence.
Its Stock model still shows about 22% disagreement between Huygens and POP X full 1/e²
widths. The benchmark preserves that discrepancy. It does not relax the original spherical
optimization adapter or declare the design physically validated. The final software check
record is 451 Python tests passed (34 optional tests skipped), seven package tests passed,
and successful lint/package-install checks.

The 0.1.0-dev.3 workflows add explicit bounded radius/thickness optimization and
focus-compensated tolerancing on both engines. Two variables changed in each synthetic
81-evaluation optimization; all hard requirements and saved/reloaded candidates passed.
Eight identical seeded draws gave uncompensated/compensated passes of 1/8→8/8 native and
2/8→8/8 portable. These are small conditional demonstrations, not yield estimates for a
production optical assembly. Five additional Stock 840 nm controls leave the approximately
22% method discrepancy unresolved. See [`docs/research/next-roadmap/` in the v1.1.0 tag](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research/next-roadmap) for receipts and limits.

The official MCP Python SDK 2.2.0 stdio client/server and process-boundary tests ran on
Windows. Both portable and native optical acceptance were exercised through actual tool calls.
Native startup required the trusted host environment to be passed by the MCP client;
restricted-client failures remain preserved as rejected evidence.
The final suite with Optiland/MCP dependencies and native live checks enabled reports
585 passed and one Windows symbolic-link capability skip. Actual native MCP cancellation
removed the owned engine, preserved an unrelated process and rejected partial results.

The 0.1.0-dev.4 optimization workflow optionally checks the original baseline and saved
candidate against a frozen, separate requirements specification after search. Four live
synthetic-singlet runs exercised passing and deliberately rejected outcomes: native CLI
and portable optimization through the official MCP client. Search sampling was 64;
validation sampling was 256, with all 81 evaluations charged to one budget. This is a
separate numerical acceptance check, not a sampling-convergence or physical-validation
claim. See [`docs/research/validation-release/` in the v1.1.0 tag](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research/validation-release) for retained receipts and rejection artifacts.
The final suite reports 610 passed and one Windows symbolic-link capability skip; seven
package tests and lint/package-install checks also pass. The earlier real OCT method
discrepancy remains unresolved.

The 0.1.0-dev.5 prescription adapter corrects native RMS spot selection on multi-wavelength
models. StandardSpot now selects each field/wavelength explicitly and records its physical
identity; the regression oracle checks all nine cells against single-wavelength models.
Prior multi-wavelength RMS spot results from this adapter need rerunning. Its separate
Huygens/POP profile backend is unaffected. The shipped three-field/three-wavelength example
passes its search-condition control but fails the fixed expanded requirements on both
engines, with native CLI and portable MCP evidence in [`docs/research/field-validation/` in the v1.1.0 tag](https://github.com/tangericm/optical-design/tree/v1.1.0/docs/research/field-validation).
The final live-enabled suite reports 614 passed and one platform capability skip; seven
package tests and lint/package-install checks pass. Native analysis caches are explicitly
excluded from distribution even after running the live example in the checkout.
