# Optical copilot 0.1.0-dev.3: implementation and evidence

This release completes the bounded continuation plan: multivariable optimization,
explicit focus compensation, an interactive MCP interface, and the controlled OCT
numerical investigation. It is a development release, with the supported prescription
scope still limited to centered spherical/plane sequential systems for design edits.

## Delivered workflows

| Workflow | Evidence | Result |
|---|---|---|
| Two-variable native optimization | [Native receipt](optimize-native/report.json) | RMS spot radius 1019.44 → 15.59 µm; 81 evaluations |
| Two-variable portable optimization | [Portable receipt](optimize-portable/report.json) | RMS spot radius 989.54 → 14.63 µm; 81 evaluations |
| Native focus compensation | [Native tolerance receipt](compensate-native/report.json) | Same eight seeded draws: 1/8 → 8/8 passing |
| Portable focus compensation | [Portable tolerance receipt](compensate-portable/report.json) | Same eight seeded draws: 2/8 → 8/8 passing |
| Interactive portable audit | [Official MCP client receipt](mcp-portable-client.json) | Completed and optically accepted |
| Interactive native audit | [Official MCP client receipt](mcp-native-inherited-client.json) | Completed and optically accepted |
| Stock OCT numerical controls | [Experiment and interpretation](optical-controls.md) | Five new cases; approximately 22% method discrepancy persists |

Both optimization examples varied the first radius and final air gap, passed all
declared requirements, reproduced saved/reloaded candidates, restored their baselines,
and preserved their source files. They demonstrate two adjustable variables; they do
not demonstrate global optimality, asphere/glass optimization or arbitrary lens design.
The native and portable engines use different spot/pupil sampling implementations.

Each compensated tolerance job ran 300 analyses. The eight perturbation draws are
identical across engines; zero analysis failures occurred. The conditional Wilson
95% interval for 8/8 is approximately [0.676, 1.000]. This is a small workflow
demonstration under an explicit independent radius perturbation model, not a
manufacturing yield guarantee. Uncompensated and compensated outcomes remain paired
in each report.

## Reproduce the workflows

From the repository root:

```powershell
uv run --with optiland==0.6.2 skills/optical-design/scripts/design.py optimize --backend optiland --model skills/optical-design/assets/portable-singlet.json --spec skills/optical-design/assets/optimization-spec.json --variables skills/optical-design/assets/variables-example.json --out new-optimization --json
uv run --with optiland==0.6.2 skills/optical-design/scripts/design.py tolerance --backend optiland --model new-optimization/candidate-model.json --spec skills/optical-design/assets/compensation-spec.json --tolerances skills/optical-design/assets/compensated-tolerances-example.json --out new-compensation --json
```

Native: replace the dependency with `--with zospy==2.1.5 --with pythonnet==3.1.0`,
select `--backend zos`, and use `assets/defocused-singlet.zmx` then the native `.zmx`
candidate. The full relative asset directory is `skills/optical-design/assets/`.
Each run requires a new/empty output directory.

Read the shipped [optimization contract](../../../skills/optical-design/references/optimization.md),
[compensation contract](../../../skills/optical-design/references/tolerancing.md),
and [MCP setup](../../../skills/optical-design/references/interactive.md) for parameters
and bounds. `exercise_mcp.py` is a reproducible official-client optical audit example.
It passes the trusted local host environment at server launch and never stores it.

The earlier native MCP attempts are deliberately retained with failed receipts.
SDK-default and partially forwarded environments produced a license startup failure;
full trusted host inheritance succeeded with the same gated Windows Job Object and
owned scratch path. The exact missing environment prerequisite was not isolated.
No job claimed acceptance after a launch failure.

## Verification and review

[verified-workflows.json](verified-workflows.json) contains source/artifact checks,
the actual two-variable vectors, paired statistics, MCP receipt hashes and the final
implementation file hashes. Regenerate with `uv run python docs/research/next-roadmap/verify_release_evidence.py`.
For the science reduction, use `uv run --with matplotlib python docs/research/next-roadmap/reduce_controls.py`.
These verify retained local evidence; they do not launch the original optical model.

The final Python suite with Optiland 0.6.2, MCP 2.2.0 and live native tests enabled
passed 585 tests; one Windows symbolic-link capability test skipped. Seven npm
tests, skill lint, Ruff and local tarball installation passed. Separate native jobs
provide real-engine evidence. Live MCP cancellation removed the owned OpticStudio process,
preserved an unrelated process and the source hash, and exposed no accepted partial report. The external OCT repository's six preservation checks
passed, and its Git tree remained clean at the original commit.

Independent reviews covered optimization, compensation, transport security and the
scientific comparison. They prompted native-file identity checks, complete portable
axial readback, explicit scientific identity assertions, and clearer cancellation
documentation. Routing walkthroughs tested which workflow a request selects; they
are not an autonomous-design performance benchmark.

No prescriptions from the external OCT project are committed here. Their copied
models remain locally available at receipt paths. Keep the retained worktrees while
using absolute-path receipts. Research evidence is excluded from the npm package.
The software has not been published remotely and does not establish MecAgent parity,
production manufacturing readiness, measured OCT accuracy, collection efficiency or SNR.
