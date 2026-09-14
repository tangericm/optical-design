# Validate across fields and wavelengths

Use this example when a design passes its on-axis objective and you need to assess
performance elsewhere in the field or spectrum. It uses the existing optimization and
separate-validation workflow, with explicit requirements for every tested combination.

The synthetic N-BK7 singlet has a 10 mm entrance pupil, radii +50/-50 mm, 5 mm glass
thickness and an initially defocused 60 mm image gap. Both model formats define the
same fields and wavelengths:

| Index | Field Y angle | Wavelength | Primary wavelength? |
|---|---:|---:|---|
| 1 | 0° | 0.4861327 µm | No |
| 2 | 3° | 0.5500000 µm | Yes |
| 3 | 6° | 0.6562725 µm | No |

Field and wavelength indices are separate axes: the validation grid contains all nine
combinations, not just the three pairs on the table's rows. Search uses field 1 and
wavelength 2. Global focal-length checks use the model's primary wavelength, which is
deliberately not index 1. The example is a development fixture, not a proposed optical
product or a manufacturing prescription.

## Run the example

From the installed skill directory:

```powershell
uv run --with optiland==0.6.2 scripts/design.py optimize --backend optiland --model assets/field-validation/portable.json --spec assets/field-validation/search.json --variables assets/variables-example.json --validation-spec assets/field-validation/validation.json --out field-validation-run --json
```

For OpticStudio use `--with zospy==2.1.5 --with pythonnet==3.1.0`, `--backend zos`, and
`--model assets/field-validation/native.zmx`. Native execution starts an owned standalone
engine. Always choose a new output directory.

The optimization changes surface 1 radius and surface 2 thickness within the existing
variable bounds. Search and validation both use sampling 64. The separate validation
requires RMS spot radius ≤30 µm and both tangential and sagittal MTF ≥0.3 at 20 cyc/mm
for every field/wavelength pair, plus the focal-length and track limits. The evaluation
budget remains 81 calls, including two final validation calls; each validation call may
perform many per-condition native analyses.

To run the control, substitute `assets/field-validation/control.json`. It repeats the
search condition and original requirements. The expanded specification adds the other
conditions and the sagittal MTF requirements without loosening any limit. The fixed
candidate's full grid can also be audited with `design.py audit` and the validation spec.

## Interpret the result

Use dev.5 or later for native multi-wavelength RMS spot analysis. Earlier adapter versions
requested all wavelengths together and could label a combined result with an individual
wavelength. Dev.5 selects each field/wavelength explicitly and verifies the readback;
rerun earlier multi-wavelength RMS spot results before relying on them.

The retained development runs accept the control and reject the expanded specification
on both engines. A completed `validation_failed` result has CLI exit 1, no accepted
`candidate`, and a hashed `rejected-candidate-model` artifact. It is an informative optical
failure, not an execution error. MCP exposes it as a completed job with
`optical_accepted: false`. Inspect `report.validation.candidate.assessment.requirements`
for each failed condition and `measurements` for its value and settings.

When adapting this pattern:

1. Read the model's field angles, wavelength values, primary wavelength and units. Indices
   alone do not identify physical conditions. The spec cannot create missing fields or waves.
2. Define the required conditions and limits before search. Include an explicit requirement
   for each metric/field/wavelength/axis/frequency you intend to gate. Merely listing fields
   and wavelengths does not require every metric to pass at every combination.
3. Check every required measurement is available and has the intended identity. A null,
   missing or incomparable measurement cannot establish acceptance.
4. Preserve a rejection. Change the design or formulate a subsequent search deliberately;
   repeatedly adapting to validation results makes those conditions part of design iteration.

These are individual monochromatic results at several wavelengths, not a polychromatic
MTF or a weighted spectral average. The two engines use different pupil sampling, so
their values are not expected to agree exactly. The example establishes neither sampling
convergence nor physical performance; it does not resolve the separate OCT Huygens/POP
discrepancy. See [separate validation](validation.md) for budgets, restoration and failure rules.

Ansys describes separate spot-diagram results for field and wavelength combinations in
[Exploring Sequential Mode](https://optics.ansys.com/hc/en-us/articles/42661713256723-Exploring-Sequential-Mode-in-OpticStudio).
Optiland's [analysis framework](https://optiland.readthedocs.io/en/latest/developers_guide/analysis_framework.html)
describes field- and wavelength-based analysis. Documentation checked September 13, 2026;
the executable example is tested against the pinned versions above.
