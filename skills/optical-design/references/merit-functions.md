# Explicit scalar and composite merit

Every objective uses supported measured metrics with their exact field, wavelength,
frequency and axis identity. Requirements remain separate hard acceptance gates. An
improved merit value cannot make a failed, unavailable or incomparable requirement pass.

Existing scalar objectives retain their schema, direction and physical units:

```json
{"metric": "rms_spot_um", "field": 1, "wavelength": 1, "direction": "minimize"}
```

For several conditions or mixed units, use an explicit dimensionless composite objective:

```json
{
  "direction": "minimize",
  "aggregation": "weighted_rms",
  "terms": [
    {"metric": "efl_mm", "unit": "mm", "target": 50, "scale": 2, "weight": 1},
    {"metric": "rms_spot_um", "field": 1, "wavelength": 1,
     "unit": "um", "target": 0, "scale": 10, "weight": 3},
    {"metric": "mtf", "field": 2, "wavelength": 1, "frequency": 50,
     "axis": "sagittal", "unit": "1", "target": 0.8, "scale": 0.1, "weight": 2}
  ]
}
```

The enclosing specification must include all requested field/wavelength indices and
frequencies. Indices are positive, 1-based engine indices. Each term requires an exact
supported unit, finite target, positive finite scale in that unit, and positive finite
weight. The merit is:

`sqrt(sum(weight_i * ((value_i - target_i) / scale_i)^2) / sum(weight_i))`

Scales express the engineer's chosen significance of a deviation; weights adjust the
relative emphasis after normalization. Targets express equality: values above and below
an MTF target both incur a residual. Use a separate minimum MTF requirement when a lower
bound is intended. Composite direction is always `minimize`; `minimum_gain` is dimensionless.
Scalar `minimum_gain` retains the scalar metric's units. Neither objective is a global
optimality guarantee, and local search may find no acceptable improvement.

For EFL 54 mm against 50 mm with scale 2 mm and weight 1, and spot 10 um against zero
with scale 10 um and weight 3, residuals are 2 and 1. Merit is `sqrt(7/4)`.

Reports retain `objective_value` and `objective_breakdown` wherever merit is evaluated.
The breakdown contains aggregation, direction, overall value/unit, and ordered terms
with measured values and identities. Composite terms additionally contain target, scale,
weight, signed `normalized_residual`, and `weighted_residual`. The Euclidean norm of the
weighted residuals equals the merit; their signs preserve deviation direction. Repeated
metric terms may express distinct targets and reuse one measurement. Measurement identities
must remain unique, and missing, nonfinite or wrong-unit objective measurements fail.

The implementation uses square-root weight ratios and a stable Euclidean norm to avoid
overflow from summing large weights or squaring large residuals. Even subnormal positive
weights are retained where the final floating-point contribution is representable.
Nonfinite arithmetic in a residual or final merit is rejected. Native analysis methods and
portable approximations retain their existing limitations; merit normalization does not
establish agreement between optical engines or between Huygens and POP.

Python consumers use `DesignSpec.objective_metrics` for all objective metric requests,
`objective_breakdown(spec, measurements)` for evidence and
`objective_value(spec, measurements)` for the scalar merit. An absent objective yields an
empty metric request list; requesting a merit value without an objective fails explicitly.
