# Separate validation after optimization — 0.1.0-dev.4

Recorded September 12, 2026. A search winner must now pass an optional frozen validation
specification before the job exposes an accepted candidate. Both the original model and
the saved/reloaded winner are measured under that specification. Validation results do
not trigger another search. A completed requirements failure returns `validation_failed`
(CLI exit 1), clears the accepted candidate and retains `rejected-candidate-model` as evidence.

## Live results

These four synthetic singlet runs used the existing bounded two-variable search, with
sampling 64 for search and 256 for validation. Both validation specifications were
prepared before the runs. They differ in the RMS spot limit: 30 µm versus a deliberately
strict 10 µm. Each run used 81 total evaluations, including the final two validation calls.

| Engine / interface | Validation limit | Candidate validation RMS spot | Tangential MTF at 20 cyc/mm | Result |
|---|---:|---:|---:|---|
| OpticStudio / native CLI | 30 µm | 14.4519 µm | 0.417118 | Accepted |
| OpticStudio / native CLI | 10 µm | 14.4519 µm | 0.417118 | Rejected |
| Optiland / official MCP client | 30 µm | 13.8735 µm | 0.471920 | Accepted |
| Optiland / official MCP client | 10 µm | 13.8735 µm | 0.471920 | Rejected |

Within each engine, both runs selected the same radius/thickness vector. The rejection
check changed acceptance without feeding results back into the search. Both MCP jobs
completed successfully at the process level; only the passing case had
`optical_accepted: true`. Source hashes, restored baselines, saved models and receipt
consistency were verified. Native rejected model files are quarantined; regenerated
OpticStudio `.ZDA` caches are excluded from Git.

## Evidence and reproduction

- `native-pass/` and `native-reject/`: reports, model snapshots, canonical specifications,
  original baseline and accepted/rejected saved model. Matching CLI JSON and logs are
  retained alongside these directories.
- `mcp-validation.json`: actual official MCP client requests and results for both portable
  optimizations. `mcp/` retains owned input snapshots, outputs and process logs.
- `exercise_validation_mcp.py`: the client driver. It passes the trusted host environment
  into the local server without writing environment values to the evidence.
- `verified-evidence.json`: compact numerical results, report hashes and implementation
  hashes. `verify_evidence.py` checks these without launching an optical engine.
- `pytest-final.log`: final complete Python test run.

Run this verification from either retained checkout:

```powershell
uv run python docs/research/validation-release/verify_evidence.py
```

Native command used (use a fresh output directory for another run):

```powershell
uv run --with zospy==2.1.5 --with pythonnet==3.1.0 skills/optical-design/scripts/design.py optimize --backend zos --model skills/optical-design/assets/defocused-singlet.zmx --spec skills/optical-design/assets/optimization-spec.json --variables skills/optical-design/assets/variables-example.json --validation-spec skills/optical-design/assets/validation-spec.json --out docs/research/validation-release/native-pass --json
```

The rejected run substitutes `docs/research/validation-release/reject-spec.json` and a fresh
output directory. The portable driver runs with
`uv run --with optiland==0.6.2 --with mcp==2.2.0 python docs/research/validation-release/exercise_validation_mcp.py`.
Copy the driver and rejection spec to a new sibling evidence folder before repeating it,
so retained client results remain unchanged. Absolute paths in original receipts identify
the retained `optical-design-validation` worktree; the verifier maps them to its own checkout.

## Software verification

The final suite passed **610 tests**, with one Windows symbolic-link capability skip,
using Python 3.11.15, Optiland 0.6.2, MCP 2.2.0, ZOSPy 2.1.5 and pythonnet 3.1.0 with
`OPTICAL_DESIGN_LIVE=1`. Native runs used OpticStudio 2024 R1 / API 24.1.0 / Premium.
Seven package tests, Ruff, skill lint, package installation checks and `git diff --check`
passed. The feature adds 25 tests, including an analytic model whose extra field fails
after the search field improves, budget handling, cancellation, frozen-spec mutation,
missing measurements, CLI argument scope and MCP receipt integrity.

Independent review identified missing baseline validation evidence and mismatched
parameter-vector acceptance in the MCP receipt checker. Four failing mutation tests
reproduced these gaps. The checker now reassesses both measurements and links both
vectors to their original/saved model entries. Follow-up review found no additional
actionable regressions; its focused suite passed 95 tests with two optional skips.

## Scientific boundaries

This demonstrates separate numerical acceptance on one synthetic, on-axis prescription.
The extra-field rejection case is an analytic test, not a native off-axis demonstration.
Finer sampling alone does not establish convergence, independent physical validation,
manufacturing yield or an unbiased statistical holdout. Native spot ray density changes
from 8 to 32; portable sampling uses its own pupil construction, so the two engines' values
are not an equality oracle. The existing real OCT Huygens/POP discrepancy of approximately
22% remains unresolved; no new physical or real-prescription acceptance claim is made.

The separate validation stage is this project's acceptance policy. Ansys documents
merit-function optimization and examination of the resulting system in its
[singlet optimization tutorial](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization)
(checked September 12, 2026); this implementation does not attribute its separate-spec
gate to a built-in OpticStudio feature.
