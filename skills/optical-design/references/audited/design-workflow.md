# Sequential design workflow

## Native and portable execution

Run from the skill directory, or use absolute script/model/spec paths. Optional engines
run in uv's isolated dependency environment. Python 3.11 is the verified Windows runtime.

```powershell
uv run scripts/zos.py check --json
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py inspect --backend zos --model assets/defocused-singlet.zmx --out inspect-native --json
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py audit --backend zos --model assets/defocused-singlet.zmx --spec assets/refocus-spec.json --out audit-native --json
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py refocus --backend zos --model assets/defocused-singlet.zmx --spec assets/refocus-spec.json --out focus-native --json
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py refocus --backend optiland --model assets/portable-singlet.json --spec assets/refocus-spec.json --out focus-portable --json
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py tolerance --backend optiland --model focus-portable/candidate-model.json --spec assets/refocus-spec.json --tolerances assets/tolerances-example.json --out tolerance-portable --json
```

An output directory must be new or empty. `working.*` is an input copy; `baseline-model.*`
and `candidate-model.*` are engine-native models, while `baseline.json`, `report.json`,
`report.md`, and `failure.json` contain evidence. Tolerance writes its own report with nominal,
sensitivity, raw Monte Carlo trials and yield. Never treat a surviving candidate file as an
accepted result unless the report is successful and `saved_candidate_verified` is true.
The source file is never the target of an engine save. Native jobs own a standalone session;
they do not attach to an open editor. Native tool calls can block past a cooperative deadline.

## Complete engineering loop

1. Inspect the saved model without a specification. Record its SHA-256 and actual
   surface inventory, pupil, fields, wavelengths, units and fixed shape data.
   Inspection completion is not a performance verdict.
2. Freeze explicit hard requirements, analysis settings and optional merit. Use scalar
   merit for one metric, or weighted RMS target residuals for multiple conditions/units.
   Freeze any separate validation specification before selecting a candidate.
3. Apply expected-value edits or run a bounded focus/parameter search. Inspect the
   actual receipt, requirements and saved-model verification before chaining a candidate.
4. Run local sensitivity at meaningful declared steps on the selected saved model.
   Use tolerance only with explicit distributions, sample count and seed.
5. Check the selected model against the frozen validation conditions. Integrated
   optimization validation rejects a failing winner; for edits/refocus, use separate
   audit jobs on baseline and candidate and retain their exact hashes. If validation
   fails, report the design as failing those conditions. Iteration against these results
   makes them design feedback rather than an untouched holdout.
6. Render relevant verified receipts into HTML/Markdown review packages. Preserve
   model lineage, objective terms, per-condition failures and sensitivity limits. The
   schematic is prescription geometry, not a traced ray plot or physical measurement.

Use the [installed-skill workflow evals](../../evals/README.md) for executable steps and
pass/fail evidence criteria. Shipped assets are synthetic examples, never inferred
requirements for an unrelated optical system.

## Explicit prescription changes

`inspect` takes `--backend`, `--model`, and `--out`, with no `--spec`. `edit` takes a
specification plus a `--changes` file:

```json
{"schema":"1","changes":[
  {"surface":2,"parameter":"thickness_mm","expected_mm":60,"value_mm":46.82}
]}
```

`expected_mm` comes from the inspected source, not a guessed design value. Only real
non-image radius/thickness cells are adjustable. A stale expected value, ignored edit,
coupled setter, fixed-state mutation, or invalid physical domain aborts the job. Failed
requirements preserve a rejected artifact rather than an accepted candidate. Explicit
edit acceptance checks requirements and saved reload; it does not imply improvement.

```powershell
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py inspect --backend optiland --model assets/portable-singlet.json --out inspect-portable --json
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py edit --backend optiland --model assets/portable-singlet.json --spec assets/full-workflow/composite-spec.json --changes assets/full-workflow/changes.json --out edit-portable --json
```

Read `edit-portable/report.json` before selecting its saved candidate. The example
change targets only the bundled original prescription. Reapplying it to an already
edited model must fail its stale expected-value check.

For local sensitivity use `design.py sensitivity --perturbations <file>` with a design
specification. Configuration is schema 1 with `parameters`, each containing `surface`,
`parameter` and positive `step_mm`. Baseline plus both sides of every parameter share
one analysis budget. See [sensitivity](sensitivity.md) for derivative units, nonlinearity
interpretation and metric-specific rankings.

```powershell
uv run scripts/review.py --report edit-portable/report.json --out edit-review --json
```

Review validates receipt inputs and artifacts without opening an optical engine.
Rendering success is independent of the underlying optical outcome.

## Specification contract

`assets/refocus-spec.json` is a runnable example, with `schema: "1"`.

| Field | Contract |
|---|---|
| `fields`, `wavelengths` | Unique positive 1-based indices in the loaded engine model |
| `frequencies_cyc_per_mm` | Positive unique image-space frequencies, required for MTF requests |
| `requirements` | Nonempty list; unique `id`, supported `metric`, exact `unit`, `min` and/or `max` |
| `objective` | Scalar metric plus minimize/maximize direction, or `aggregation: weighted_rms`, `direction: minimize`, explicit `terms`; required for refocus, optimize and compensation |
| `focus` | `min_mm`, `max_mm`, strictly positive ordered final air-gap bounds |
| `budget` | `max_evaluations` 7–201; positive `timeout_s`; counts include verification |
| `analysis` | `sampling` 32/64/128/256; scalar `use_polarization: false` |
| `minimum_gain` | Nonnegative absolute change in scalar objective units or dimensionless composite merit, default 0.001 |

Metric names/units: `efl_mm` (mm), `f_number` (1), `total_track_mm` (mm),
`image_distance_mm` (mm), `rms_spot_um` (um), `mtf` (1). RMS and MTF also need `field` and
`wavelength`; MTF needs `frequency` and `axis: tangential|sagittal`. First-order focal length
and F-number use the primary wavelength. F-number is nominal paraxial, not working F-number.
`total_track_mm` excludes object distance. RMS is geometric spot **radius about the centroid**.
MTF is scalar FFT MTF with linear frequency interpolation and no extrapolation.

Composite terms carry exact metric identities/units, finite targets and positive scales
and weights. Merit is `sqrt(sum(w*((value-target)/scale)^2)/sum(w))`. A target is an equality
preference; use a hard minimum or maximum requirement for a one-sided constraint.
Reports retain each objective term. See [merit functions](../merit-functions.md).

The refocus workflow coarsely samples the declared interval, then refines near the best
coarse objective. It is a bounded local search and can miss another optimum or narrow
feasible interval. All evaluated candidates are in history. A candidate must improve the
objective and satisfy every requirement; baseline feasibility is reported separately.
Unknown keys, unsupported metric identities, missing metrics and incompatible units do not pass.

## Adapter boundaries

Both adapters support centered refractive systems with air object/image
spaces, angle fields and entrance pupil diameter. Native OpticStudio accepts Standard
spheres/planes/conics and EvenAspheric surfaces with fixed conic and even coefficients
A2 through A16. These shape cells are inspected/preserved, not optimization variables.
Native lens units must be mm; radius and
thickness solves must be fixed. Native field normalization must be radial, without declared
vignetting/tilts; explicit surface apertures and decenter/tilt are rejected. Native validation
includes a 17-ray pupil check per field/wavelength; it catches gross failures, not every
possible clipping event. Automatic apertures are not a mechanical clear-aperture specification.

Optiland supports its validated spherical/plane native JSON subset and a small explicitly whitelisted ZMX
text subset. Unknown directives and unsupported apertures/solves are rejected before import.
**A normal full OpticStudio export can be rejected.** This is not general ZMX/SEQ/LEN support.
Optiland always saves native JSON, including its native Infinity representation for object
distance/planes; evidence reports use strict JSON. The bundled models were independently
constructed from the same synthetic N-BK7 prescription, not imported interchangeably.

Native and portable pupil sampling differ. Shared first-order/spot agreement is useful
cross-validation; FFT MTF agreement is not assumed. Repeat with higher sampling when it
changes acceptance. Polarization, portable aspheres, coatings, coordinate breaks,
multi-configuration models, ghost/stray-light,
material/temperature tolerances and decenter/tilt tolerances are unsupported. Optional bounded
final-gap compensation is available; see [tolerancing](../tolerancing.md).

For multiple explicit radius/thickness variables, see [optimization](optimization.md).
Its normalized bounded search retains the best feasible candidate and verifies all edits,
fixed geometry and saved-model reload. For local interactive jobs, use the [MCP server](interactive.md).

## Comparison

`compare.py` checks numerical equivalence, not improvement. Its strict default requires
complete nonempty numeric coverage, compatible declared units and matching supplied
analysis identity. Missing units on both sides can only support an unlabeled numeric
comparison. `--shared-only` is exploratory and never certifies equivalence. Curve grids
must already match; no coordinate interpolation is performed by this command. Design-job
reports use their own named-metric requirement contract; inspect exact metric identities
and engine analysis settings rather than flattening entire histories into one comparison.

## Engine sources

- [ZOSPy 2.1.5](https://pypi.org/project/zospy/2.1.5/) and [Optiland 0.6.2](https://pypi.org/project/optiland/0.6.2/): pinned adapter dependencies.
- [Optiland spot analysis source](https://github.com/optiland/optiland/blob/v0.6.2/optiland/analysis/spot_diagram/core.py) and [FFT MTF source](https://github.com/optiland/optiland/blob/v0.6.2/optiland/mtf/fft.py): implementation conventions.
- [ZOS-API surface tilt example](https://community.zemax.com/zos-api-12/zos-api-using-tilt-682?sort=mostRecentFirst): Standard surfaces can carry separate tilt/decenter data.
