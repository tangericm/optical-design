# Bounded optimization and refocus

`design.py optimize` searches one through four explicit radius/thickness variables in the
supported centered spherical sequential adapters. It uses the same standalone native
worker boundary as audit/refocus when `--backend zos` is selected. The portable backend
uses Optiland 0.6.2. No engine optimizer, arbitrary generated code, inferred variables,
surface topology changes, or editor attachment is involved.

```powershell
uv run --with optiland==0.6.2 skills/optical-design/scripts/design.py optimize `
  --backend optiland --model skills/optical-design/assets/portable-singlet.json `
  --spec skills/optical-design/assets/optimization-spec.json `
  --variables skills/optical-design/assets/variables-example.json --out optimization --json
```

For licensed Windows native execution, replace the optional dependency with
`--with zospy==2.1.5 --with pythonnet==3.1.0`, select `--backend zos`, and provide the
supported `.zmx` or `.zos` model. The output directory must be new or empty.
`--variables` is required only for `optimize`; other actions reject it.

The separate variables JSON has exactly this shape:

```json
{
  "schema": "1",
  "variables": [
    {"surface": 1, "parameter": "radius_mm", "min_mm": 48, "max_mm": 52},
    {"surface": 2, "parameter": "thickness_mm", "min_mm": 44, "max_mm": 51}
  ]
}
```

Indices refer to real native surfaces, excluding object and image. Each surface/parameter
pair must be unique. Bounds and interval widths must be finite, with `min_mm < max_mm`.
Thickness intervals are strictly positive; radius intervals cannot include or cross zero.
Only `radius_mm` and `thickness_mm` are accepted. The unchanged baseline may lie outside
the search bounds; all applied search and accepted candidate values must lie inside them.
The design spec supplies one explicit objective, its direction, minimum gain in objective
units, all hard requirements, identical analysis settings, and evaluation/time budgets.
The optional refocus `focus` interval is not an optimization variable declaration.

Search normalizes each interval to `[0,1]`, evaluates the clipped nominal vector and
midpoint, then uses bounded coordinate polling and simultaneous pattern moves. It halves
the normalized step when no ranked improvement is found. Feasible samples rank ahead
of infeasible ones; before feasibility, normalized requirement violations guide search.
An independent best-feasible record prevents a better objective with failed requirements
from replacing an acceptable candidate. This is a deterministic local search, not a global
optimum proof. A small evaluation budget may provide only coarse exploration.

Every point reloads and inspects the baseline before applying all setters. All declared
parameters are read back after every setter has finished and again after optical evaluation.
Readback tolerance is `1e-12` relative and `1e-12 mm` absolute; a requested nonzero delta
must also produce an actual change. Fixed fields, wavelengths, aperture, materials, surface
properties and undeclared prescription cells are compared against their initial inspection.
The portable adapter exposes all axial positions, including the image: only translations
equal to the cumulative preceding declared thickness changes are allowed.

At most `budget.max_evaluations` optical analyses run, counting the baseline, failed attempts,
and candidate verifications. Two evaluations are reserved for repeating the best candidate
and evaluating its saved/reloaded model. Acceptance requires every hard requirement to pass
and objective gain to strictly exceed `minimum_gain` in both verifications. Every saved
parameter must reproduce, and the reloaded objective must agree with the pre-save objective
within `1e-5` relative / `1e-8` absolute tolerance. Infeasible or unavailable required metrics
can never earn acceptance. An analysis error aborts the job with failure evidence.

The time budget and cancellation callback are checked before and after backend operations.
Native calls can exceed the cooperative deadline while blocked; late results are rejected.
Mandatory baseline recovery runs outside the exhausted budget. The source is never edited;
a hash change caused externally fails acceptance and preserves the source snapshot for review.
A report is written only after successful restoration and engine teardown. Failures retain
`failure.json` with restoration, source and attempted-evaluation evidence.

`report.json` contains the full history, parameter vectors, measurements, hard-constraint
assessments, normalized search termination, engine inspection, settings and artifact hashes.
`status: improved` requires `saved_candidate_verified: true`; `no_acceptable_improvement`
contains no accepted candidate. CLI exit codes are 0 for improvement, 1 for no acceptable
improvement, 2 for argument misuse, 3 for missing dependencies and 4 for job failure.

An optimizer improves its specified merit function. A local minimum is not a proof of
global optimality or compliance with requirements absent from that function. OpticStudio's
sequential tutorial demonstrates choosing variables, building a merit function and then
evaluating the resulting system.
[Ansys singlet optimization](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization).

Use this project's conservative sequence:

1. Preserve the original model. Snapshot prescription, fields, wavelengths, apertures,
   materials, configurations and analysis settings; hash the source and specification.
2. Evaluate the unchanged baseline. Stop if required metrics are unavailable or the
   selected backend cannot represent the model.
3. Declare one objective, its direction, minimum useful gain and all hard constraints.
   Give every adjustable variable a physical interval and set an evaluation/time budget.
4. Start with bounded focus travel when appropriate. A focus adjustment must not silently
   change conjugates, field definitions, aperture, wavelength weights or required magnification.
5. Compare candidate and baseline with identical settings. Check hard constraints
   independently of the aggregate score; include all specified fields and wavelengths.
6. Save the best valid candidate separately, reload it and re-evaluate. Report budget
   exhaustion, restoration failures and no-improvement outcomes explicitly.

These are workflow requirements, not a guarantee that every backend supports each operation.
Inspect the runtime capability result and the saved job evidence before claiming execution.
Do not reuse historical connectivity as proof of a current licensed session.

Distinguish equivalence from improvement. A favorable large change can fail an equivalence
test; conversely, numerical agreement with a baseline does not prove a useful improvement.
Use independent validation metrics or held-out field/wavelength samples where the model
supports them, and compare the observed gain with numerical convergence variation.

After nominal improvement, run the declared manufacturing/assembly model rather than
assuming nominal merit-function gain establishes yield. See [tolerance evidence](tolerancing.md).

Primary link checked 2026-09-12. The bounded search and acceptance rules are project policy.
