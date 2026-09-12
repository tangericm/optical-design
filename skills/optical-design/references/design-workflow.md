# Sequential design workflow

## Native and portable execution

Run from the skill directory, or use absolute script/model/spec paths. Optional engines
run in uv's isolated dependency environment. Python 3.11 is the verified Windows runtime.

```powershell
uv run scripts/zos.py check --json
uv run --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py audit --backend zos --model assets/defocused-singlet.zmx --spec assets/refocus-spec.json --out audit-native --json
uv run --with zospy==2.1.5 --with pythonnet==3.1.0 scripts/design.py refocus --backend zos --model assets/defocused-singlet.zmx --spec assets/refocus-spec.json --out focus-native --json
uv run --with optiland==0.6.2 scripts/design.py refocus --backend optiland --model assets/portable-singlet.json --spec assets/refocus-spec.json --out focus-portable --json
uv run --with optiland==0.6.2 scripts/design.py tolerance --backend optiland --model focus-portable/candidate-model.json --spec assets/refocus-spec.json --tolerances assets/tolerances-example.json --out tolerance-portable --json
```

An output directory must be new or empty. `working.*` is an input copy; `baseline-model.*`
and `candidate-model.*` are engine-native models, while `baseline.json`, `report.json`,
`report.md`, and `failure.json` contain evidence. Tolerance writes its own report with nominal,
sensitivity, raw Monte Carlo trials and yield. Never treat a surviving candidate file as an
accepted result unless the report is successful and `saved_candidate_verified` is true.
The source file is never the target of an engine save. Native jobs own a standalone session;
they do not attach to an open editor. Native tool calls can block past a cooperative deadline.

## Specification contract

`assets/refocus-spec.json` is a runnable example, with `schema: "1"`.

| Field | Contract |
|---|---|
| `fields`, `wavelengths` | Unique positive 1-based indices in the loaded engine model |
| `frequencies_cyc_per_mm` | Positive unique image-space frequencies, required for MTF requests |
| `requirements` | Nonempty list; unique `id`, supported `metric`, exact `unit`, `min` and/or `max` |
| `objective` | One metric identity plus `direction: minimize` or `maximize`; required for refocus |
| `focus` | `min_mm`, `max_mm`, strictly positive ordered final air-gap bounds |
| `budget` | `max_evaluations` 7–201; positive `timeout_s`; counts include verification |
| `analysis` | `sampling` 32/64/128/256; scalar `use_polarization: false` |
| `minimum_gain` | Nonnegative absolute change in objective units, default 0.001 |

Metric names/units: `efl_mm` (mm), `f_number` (1), `total_track_mm` (mm),
`image_distance_mm` (mm), `rms_spot_um` (um), `mtf` (1). RMS and MTF also need `field` and
`wavelength`; MTF needs `frequency` and `axis: tangential|sagittal`. First-order focal length
and F-number use the primary wavelength. F-number is nominal paraxial, not working F-number.
`total_track_mm` excludes object distance. RMS is geometric spot **radius about the centroid**.
MTF is scalar FFT MTF with linear frequency interpolation and no extrapolation.

The current optimizer coarsely samples the declared interval, then refines near the best
coarse objective. It is a bounded local search and can miss another optimum or narrow
feasible interval. All evaluated candidates are in history. A candidate must improve the
objective and satisfy every requirement; baseline feasibility is reported separately.
Unknown keys, unsupported metric identities, missing metrics and incompatible units do not pass.

## Adapter boundaries

Both adapters support centered spherical/plane refractive systems with air object/image
spaces, angle fields and entrance pupil diameter. Native lens units must be mm; radius and
thickness solves must be fixed. Native field normalization must be radial, without declared
vignetting/tilts; explicit surface apertures and decenter/tilt are rejected. Native validation
includes a 17-ray pupil check per field/wavelength; it catches gross failures, not every
possible clipping event. Automatic apertures are not a mechanical clear-aperture specification.

Optiland supports its validated native JSON subset and a small explicitly whitelisted ZMX
text subset. Unknown directives and unsupported apertures/solves are rejected before import.
**A normal full OpticStudio export can be rejected.** This is not general ZMX/SEQ/LEN support.
Optiland always saves native JSON, including its native Infinity representation for object
distance/planes; evidence reports use strict JSON. The bundled models were independently
constructed from the same synthetic N-BK7 prescription, not imported interchangeably.

Native and portable pupil sampling differ. Shared first-order/spot agreement is useful
cross-validation; FFT MTF agreement is not assumed. Repeat with higher sampling when it
changes acceptance. Polarization, aspheres, multi-configuration models, ghost/stray-light,
material/temperature tolerances, decenter/tilt tolerances and compensators are unsupported.

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
