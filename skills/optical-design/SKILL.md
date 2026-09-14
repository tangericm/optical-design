---
name: optical-design
description: >
  Use whenever the user has a lens or optical system to design, analyze, optimize,
  tolerance or review: a .zmx, .zos or Optiland prescription; achromats, objectives,
  relays, tube lenses, scan lenses; microscopy or OCT optics; or questions about
  resolution, PSF, MTF, Strehl, Zernike, wavefront or interferometry results. Use it
  for lens-design questions even when no file is attached.
license: MIT
compatibility: Python 3.11+ and uv. Prescription work uses Optiland 0.6.2 through `uv run --with optiland==0.6.2`. Licensed OpticStudio through ZOSPy 2.1.5 on Windows is optional.
metadata:
  author: Eric Tang
  repo: https://github.com/tangericm/optical-design
  version: "3.0.0"
---

# optical-design

Help the user understand, design and improve lenses. Use the calculators for a numerical
question and Optiland recipes for prescription work. Explain the result in familiar
language first, then supply optical terms, units and measurement conditions. Match the
depth to the user; a beginner and an engineer need the same correct computations.

Resolve every relative script/reference/asset path below from the directory containing
this loaded `SKILL.md`, not the conversation's working directory. Invoke scripts by their
absolute paths. Keep this installed directory unchanged: write scripts, candidate lenses,
figures and notes in one new user-project output directory, outside the skill. Read the
specific recipe section needed for the task instead of loading every reference.

## Start here

| The user wants | Do | Read |
|---|---|---|
| To learn without a file | Run `scripts/walkthrough.py --out <new-project-output-directory>`, explain the layout and before/after spot | `walkthrough.py --help` |
| A number: resolution, depth of focus, Gaussian beam, OCT, camera sampling | `uv run scripts/resolve.py <subcommand> --json` | [microscopy](references/microscopy.md), [OCT](references/oct.md) |
| To understand a `.zmx` or Optiland JSON file | Inspect import fidelity, run `scripts/first_order.py`, then select layout, spot or fans | [analysis recipes](references/optiland-recipes.md#3-layout-plot), [diagnosis](references/diagnosis.md) |
| To improve a lens | First-order gate, freeze requirements, then least squares | [optimization recipe](references/optiland-recipes.md#9-build-and-run-an-optimization-problem), [merit functions](references/merit-functions.md), [aberrations](references/aberrations.md) |
| To start a new design | Pick a form by F-number, field and NA, scale it to the EFL | [forms library](assets/forms/README.md) |
| Yield or tolerances | Perturb and re-measure with a focus compensator | [tolerance recipe](references/optiland-recipes.md#12-tolerancing-perturb-compensate-sample-yield), [tolerancing](references/tolerancing.md) |
| To interpret wavefront or interferometer data | `scripts/zernike.py`, `scripts/wavefront.py`, `scripts/interfero.py` | [PSF/MTF](references/psf-mtf.md), [interferometry](references/interferometry.md) |
| A review to hand off | Write `summary.json` and PNGs, then `scripts/render_review.py` | [summary recipe](references/optiland-recipes.md#14-export-figures-and-a-summaryjson), `render_review.py --help` |
| A `.zos` file or licensed OpticStudio | Use the native audited adapter; Optiland snippets do not run through ZOSPy unchanged | [OpticStudio](references/opticstudio.md) |
| A hash-verified receipt for a bounded change | `scripts/design.py` audited mode | [audited mode](references/audited/README.md) |

Use `uv run --python 3.11 --with optiland==0.6.2 <absolute-script-path>` for portable
prescription work, including the walkthrough. Calculators and the renderer need no optical
engine. Run a script with `--help` when its arguments are not known. Scripts exit 0 on success, 1 on a failed gate or
requirement, 2 on usage, 3 when an engine is missing, 4 on an analysis failure.

## How to work a design problem

1. Copy the input file and hash it. Never write to the user's path.
2. Inspect import fidelity, units and first-order quantities. Ask only for missing inputs
   that change the physical problem. If the existing lens misses a clear requested target,
   explain the mismatch and work toward that target. Do not silently infer objective
   manufacturer conventions or treat unsupported import content as harmless metadata.
3. Freeze the requirements before optimizing: actual required fields (including full field),
   wavelengths and weights, metrics with thresholds, hard constraints (EFL, track, edge
   thickness), variables with bounds.
4. Look before you optimize: layout, spot diagram, ray and OPD fans, Seidel table. Write
   the two-sentence diagnosis from [diagnosis.md](references/diagnosis.md).
5. Optimize progressively: first-order operands, then RMS spot, then wavefront or MTF.
   Open glass variables last and only when color is the limit.
6. Look again and re-diagnose. Compare against the diffraction limit.
7. Save the candidate, reload it, re-measure all hard requirements at their declared fields,
   wavelengths and sampling. A lower merit value or optimizer exit does not prove acceptance.
   Report the re-measured values, any missed targets, and whether the budget was exhausted.
8. If it will be built, tolerance it. Write `summary.json`, render the review, and keep
   a short `notes.md` of what you tried and why.

## Explaining results

- Every number carries its unit, field, wavelength and metric definition (RMS spot
  radius is not a diameter or FWHM; state the sampling for MTF).
- Name the likely dominant aberration and its evidence, then a variable worth investigating.
- Say what the optimizer traded, in Seidel terms or in the fans.
- Compare with the diffraction limit: Airy radius 1.22 λ F/#, MTF cutoff 1/(λ F/#).
- State a model limit in one clause where it matters (scalar, paraxial NA, nominal
  design), not in a paragraph. Nominal performance is not yield; say so once when relevant.
- Keep image distance distinct from back focal length, paraxial NA from real-ray NA,
  and EFL spread over wavelength from best-focus shift. Show before/after plots on matched
  scales. Lead reviews with the result and next action; rendering alone verifies no optics.

## Not this skill

Non-sequential and stray-light design, thin-film coating design, illumination and
non-imaging optics are outside the supported workflow. Explain the limitation briefly
and identify the missing analysis or suitable specialist tool; offer any relevant
supported calculation without presenting it as a solution to the unsupported problem.

## References

[Optiland recipes](references/optiland-recipes.md) ·
[Aberrations primer](references/aberrations.md) ·
[Diagnosis](references/diagnosis.md) ·
[Merit functions](references/merit-functions.md) ·
[Microscopy](references/microscopy.md) ·
[OCT](references/oct.md) ·
[Forms library](assets/forms/README.md) ·
[PSF and MTF](references/psf-mtf.md) ·
[Interferometry](references/interferometry.md) ·
[Tolerancing](references/tolerancing.md) ·
[OpticStudio](references/opticstudio.md) ·
[Evidence limits](references/evidence-limits.md) ·
[Audited mode](references/audited/README.md)
