# Inspect saved prescriptions and apply explicit changes

Inspection opens a disposable copy of a saved model, records its physical inventory,
saves and reloads a baseline, and verifies restoration. It requires no design
specification and runs no optical analyses. Its `inspected` status describes successful
inventory capture, not requirement acceptance. Surface shape and support boundaries
remain those of the selected backend.

Explicit edits require a design specification and this data-only configuration:

```json
{
  "schema": "1",
  "changes": [
    {"surface": 1, "parameter": "radius_mm", "expected_mm": 50, "value_mm": 52},
    {"surface": 2, "parameter": "thickness_mm", "expected_mm": 49.15, "value_mm": 49.25}
  ]
}
```

Declare 1–16 unique surface/parameter cells. Supported cells are finite, nonzero
`radius_mm` and finite, strictly positive `thickness_mm` on real non-image surfaces.
Object and image surfaces are excluded. Backend-specific unsupported cells still reject.
Asphere coefficients and conics remain fixed during these edits. Plane-radius changes
are outside this finite-value contract. A no-op value is permitted.

All expected originals are checked before any optical evaluation or setter. Comparison
uses relative tolerance `1e-12` and absolute tolerance `1e-12 mm`, also recorded in the
receipt. Obtain originals from a fresh inspection. A stale expected value aborts the
entire operation. After each setter, every declared cell is checked against the current
partial vector, preventing coupled changes from being hidden by subsequent setters.
Inspection values and backend getter values must agree with the request. All undeclared
prescription and invariant state must remain fixed; downstream axial translations must
match declared thickness changes.

The job evaluates the baseline and changed prescription, saves the proposed model,
reloads it, and evaluates it independently. Reload must preserve requested cells,
undeclared state, metric identities, units and values. Numerical metric comparison uses
relative tolerance `1e-5` and absolute tolerance `1e-8` in the metric's own units; crossing
a hard requirement on reload still fails. These three analyses share the specification's
evaluation/time budget. Inspection uses a 120-second cooperative time limit. Native calls
may block beyond a cooperative deadline; cancellation and elapsed time are checked around
engine calls. Recovery runs outside those limits.

`applied` means the saved/reloaded explicit candidate passes all hard requirements and
`saved_candidate_verified` is true. There is no optimization or minimum merit-gain gate.
An objective, when supplied, is reported with its complete term breakdown. A failed hard
requirement produces `requirements_not_met`, an empty accepted `candidate`, and a hashed
`rejected_candidate_model` with rejected evaluation evidence. It never produces accepted
candidate status. An execution, readback, source-integrity, restoration or teardown error
writes `failure.json` and prevents a success receipt.

Both jobs preserve the original source and retain a source snapshot and saved baseline
with hashes. Edit receipts additionally bind `spec.json` and `changes.json` to their hashes.
Hashes are pinned when each artifact is created and checked after teardown; altered
evidence cannot receive freshly computed hashes in a successful receipt. Measurement
buffers are copied at evaluation time so later engine calls cannot rewrite baseline rows.
Output directories must be new or empty. The owned backend is restored before teardown;
`report.json` is written only after successful teardown and source-integrity verification.

Python entry points are `run_inspect_job(model, out, factory, *, cancelled=None)`,
`run_edit_job(model, spec, out, factory, changes, *, cancelled=None)`, and
`validate_changes(raw)`. Both runners return report schema `1` for the shared CLI/MCP
execution boundary and review-package renderer. These operations act on saved copies,
not unrestricted mutation of an active GUI session.
