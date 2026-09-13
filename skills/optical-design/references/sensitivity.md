# Local prescription sensitivity

Sensitivity measures response to explicit symmetric radius/thickness steps around
a saved baseline. It does not optimize, accept a changed prescription, infer a
manufacturing distribution, or estimate yield. Hard requirement failures remain
visible even when the sensitivity job itself completes.

The engineering interface is
`run_sensitivity_job(model, spec, out, factory, perturbations, *, cancelled=None)`.
The design specification supplies requirements, analysis conditions, an optional
scalar or composite objective, and the shared analysis/time budget.

```json
{
  "schema": "1",
  "parameters": [
    {"surface": 1, "parameter": "radius_mm", "step_mm": 0.1},
    {"surface": 2, "parameter": "thickness_mm", "step_mm": 0.01}
  ]
}
```

Declare 1–16 unique surface/parameter pairs. Surface indices must identify real
non-object, non-image surfaces. Supported cells are `radius_mm` and `thickness_mm`.
Steps must be positive finite numbers producing distinct floating-point values.
Both thickness trials must be strictly positive; radius trials must retain the
baseline sign, excluding zero/plane curvature. Steps are never clipped or fitted.
At least `1 + 2 * parameter_count` evaluations must fit the supplied budget.

Every trial reloads the inspected, saved baseline, changes one cell, and verifies
the entire declared parameter vector plus all fixed inspection state before and
after analysis. This catches ignored edits, coupled setters, changed conics or
asphere coefficients, and analysis-induced model mutation. Derived axial motion
from a declared thickness change is checked against that exact thickness change.
The dedicated parameter getter must also agree with the inspection inventory.
Readback absolute tolerance is the smaller of `max(abs(requested)*1e-12, 1e-12)` mm
and `step_mm*1e-6`; nonzero steps must cause an actual change.

For baseline metric `m0`, minus/plus measurements `m-` and `m+`, and declared step
`h` in mm, the report gives:

| Field | Definition | Unit |
|---|---|---|
| `derivative_per_mm` | `(m+ - m-)/(2h)` | metric unit/mm |
| `declared_step_effect` | `abs(derivative_per_mm*h)` | metric unit |
| `minus_delta`, `plus_delta` | `m- - m0`, `m+ - m0` | metric unit |
| `max_absolute_step_effect` | `max(abs(minus_delta), abs(plus_delta))` | metric unit |
| `second_difference` | `m+ - 2m0 + m-` | metric unit |
| `second_derivative_per_mm2` | `second_difference/h²` | metric unit/mm² |
| `nonlinearity_indicator` | `abs(second_difference)/(abs(minus_delta)+abs(plus_delta))` | dimensionless |

The nonlinearity indicator is zero when both measured deltas are zero. A symmetric
quadratic response at a stationary point has zero central derivative but nonzero
second difference and maximum absolute step effect. Thus derivative rankings alone
do not describe the entire finite-step response. The indicator is descriptive;
there is no universal pass threshold or proof of convergence as the step shrinks.

`sensitivities` contains one record per declared parameter, with per-metric
identities, units, and the quantities above. If an objective exists, its value is
computed through the common objective evaluator and an `objective` record contains
the same quantities. Composite merit values are dimensionless. No accepted
candidate is emitted.

`rankings` orders parameters by descending `declared_step_effect` separately for
each exact metric identity and unit. Field, wavelength, frequency and axis remain
part of identity. Rankings depend on the declared steps; they cannot compare
different metrics or units, and are not a universal parameter importance score.

All returned metrics must be finite, unique, available and correctly unit-labeled;
every required metric and optional objective must be available. Baseline and trial
metric identities and analysis metadata must agree. The portable FFT frequency
grid range may change physically with prescription and is retained as evidence,
but is excluded from metadata equality. Requested frequency, interpolation and
all other analysis settings remain fixed. Missing data aborts the job.

Outputs include `report.json`, `spec.json`, `perturbations.json`, `baseline.json`,
the source snapshot, and saved baseline model. The report binds the source,
baseline and input snapshots with SHA-256 hashes. `history` includes baseline and
successful trials; `trials` includes actual vectors, inspections, measurements,
parameter indices and directions. `evaluations` counts attempted analyses,
including failed or late calls. Invalid/incomplete analyses do not enter successful
history, and execution failures retain `failure.json` with partial evidence.

Time/cancellation checks occur between engine calls; a blocking call can exceed
the deadline. Baseline restoration and engine teardown run outside exhausted
budgets. A successful receipt requires unchanged source/snapshots, verified
restoration and successful teardown. Original user model bytes are never edited.
