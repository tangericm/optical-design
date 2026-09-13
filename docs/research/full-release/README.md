# Sequential imaging workflow: full-release evidence

The implementation follows the [full-release contract](../../superpowers/specs/2026-09-13-full-release.md).
This directory retains actual engine/CLI/MCP receipts, including rejected attempts. Synthetic
fixtures demonstrate the supported workflow; they do not establish arbitrary prescription
coverage, a global optimum or physical validation of a manufactured system.

The final local suite passed 837 tests with two platform skips (Windows symbolic-link
capability and the POSIX-only process observer).
Optiland 0.6.2, MCP 2.2.0 and native OpticStudio checks were enabled. The seven npm tests,
Ruff, skill lint and local package installation also passed. Hosted CI and public installation
are separate publication gates. [The source CI gate](ci-source-gate.json) passed all nine
jobs after the POSIX test observer fix; [the initial CI failure](ci-initial.json) is retained.

## Composite merit across nine conditions

The fixed specification combines centroid RMS spot at three fields and three wavelengths,
with equal weights and a 30 um scale. Every individual spot must remain below 120 um;
focal length and track are separately constrained. Two bounded radius/thickness variables
were searched for 41 evaluations per engine. The inputs and criteria were written before
either run. Merit values are dimensionless and are compared within each engine.

| Engine | Baseline merit | Saved candidate merit | Radius / image gap (mm) |
|---|---:|---:|---|
| Optiland 0.6.2 | 33.833235 | 1.312395 | 51.9375 / 47.5 |
| OpticStudio 2024 R1 | 34.854713 | 1.363050 | 52 / 47.5 |

Both saved/reloaded candidates satisfy the declared requirements. Native radius reaches its
upper bound: this is a bounded local result, not evidence of a global optimum. See
[portable receipt](composite-optiland/report.json), [native receipt](composite-zos/report.json)
and [reproducer](run_composite.py). Existing stricter expanded-field requirements from dev.5
remain unchanged and failed; these are different predeclared demonstration specifications.
The same jobs were repeated against the frozen implementation in [final composite evidence](final-composite/composite-results.json).

## Native model shapes

Two centered fixtures add a Standard conic or an EvenAspheric surface. All eight coefficients
(A2 through A16) are read back and preserved. The asphere fixture includes nonzero A4, A6 and
A16 so high-order retention is exercised. [Shape evidence](shape-fixtures.json) compares eight
native sag values against the analytic conic-plus-polynomial formula. Live regression tests
also change radius and thickness, save/reload, recheck sag and detect an undeclared A16 change.
Shape coefficients stay fixed during the supported optimization workflow.

## Actual MCP and installed workflows

[Final MCP receipts](final-mcp/mcp-results.json) record 16 official SDK 2.2.0 jobs across both
engines: inspection, refocus, explicit edit using the verified focus gap, sensitivity,
finer-sampling audit, tolerance, composite optimization with separate validation, and a
rejected edit. All produce review packages. Every start is also attempted with an incorrect
model hash and rejects. [Earlier integration receipts](mcp-results.json) remain preserved.
The server receives the trusted local host environment for native licensing; environment
contents are never serialized. Each process owns copies of its input models.

The first explicit edit tried a gap from a different optimized prescription. It failed the
unchanged spot/MTF limits; [the initial log](mcp-initial-rejected.log) and owned job artifacts
are retained. The successful workflow obtains focus from that model's own verified refocus.
Changing the gap back to 60 mm produces an ordinary rejected optical result on both engines.

[Portable workflow](portable-workflow-01/workflow-summary.json) executes the shipped example,
including finer-sampling validation and expected stale-edit/configuration failures.
The [final installed-client gate](installed-release.json) uses the same shipped runner after
an isolated skills installation: version 1.0.0, 14 calls, 78/78 source and installed file hashes
matching, and no installed-file changes during execution.
These are executable workflow checks, not an autonomous external-client benchmark.

## Evidence limits

The review renderer checks local hashes, identities and numerical receipt consistency. It
does not rerun optics or authenticate third-party engine claims. HTML output has automated
structure/escaping tests; browser visual inspection was blocked by the browser URL policy
for local files and was not bypassed. No visual screenshot acceptance is claimed.

The real OCT Stock design still has approximately 22% Huygens/POP X-width disagreement.
This release preserves that unresolved result. Neither new merit functions nor native
asphere support establish physical acceptance of that optical design.

Independent scientific and integration reviews found and reproduced receipt-binding,
engine-teardown artifact mutation, mutable spec/buffer, overflow and tiny-step consistency
defects. Regression tests now reject those cases. A shared step-domain check keeps live
sensitivity and offline verification aligned. The first full-suite attempt also identified
five old skeletal test records lacking newly required input snapshots; those fixtures now
provide the complete original spec and variable records rather than bypassing validation.

Receipts retain original absolute paths in preserved evidence checkouts. Run
`uv run python docs/research/full-release/verify_evidence.py` there to recheck source/artifact
hashes and receipt consistency. This verification does not launch an engine.
