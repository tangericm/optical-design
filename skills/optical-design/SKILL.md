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
  version: "2.0.0"
---

# optical-design

Help the user design, understand and improve lenses. Compute with Optiland (or licensed
OpticStudio) by writing short scripts from the recipes; use the bundled calculators for
closed-form numbers; explain every result in the language of aberrations, with units and
the conditions it was measured under. You do the work; the skill supplies the knowledge,
the recipes and the discipline.

## Start here

| The user wants | Do | Read |
|---|---|---|
| A number: resolution, depth of focus, Gaussian beam, OCT, camera sampling | `uv run scripts/resolve.py <subcommand> --json` | [microscopy](references/microscopy.md), [OCT](references/oct.md) |
| To understand a lens file | `scripts/inspect_zmx.py`, then `scripts/first_order.py`, then layout, spot and fans from the recipes | [Optiland recipes](references/optiland-recipes.md), [diagnosis](references/diagnosis.md) |
| To improve a lens | First-order gate, freeze requirements, then least squares (recipe 9) | [merit functions](references/merit-functions.md), [aberrations](references/aberrations.md) |
| To start a new design | Pick a form by F-number, field and NA, scale it to the EFL | [forms library](assets/forms/README.md) |
| Yield or tolerances | Recipe 12 with a focus compensator | [tolerancing](references/tolerancing.md) |
| To interpret wavefront or interferometer data | `scripts/zernike.py`, `scripts/wavefront.py`, `scripts/interfero.py` | [PSF/MTF](references/psf-mtf.md), [interferometry](references/interferometry.md) |
| A review to hand off | Write `summary.json` and PNGs (recipe 14), then `scripts/render_review.py` | `render_review.py --help` |
| Licensed OpticStudio | Same workflow through ZOSPy | [OpticStudio](references/opticstudio.md) |
| A hash-verified receipt for a bounded change | `scripts/design.py` audited mode | [audited mode](references/audited/README.md) |

Run any script with `--help` first. Scripts exit 0 on success, 1 on a failed gate or
requirement, 2 on usage, 3 when an engine is missing, 4 on an analysis failure.

## How to work a design problem

1. Copy the input file and hash it. Never write to the user's path.
2. Inspect, then run the first-order gate. If EFL, F-number, field, wavelengths or
   conjugates disagree with the request, stop and ask; they are coupled and the rest of
   the work depends on them.
3. Freeze the requirements before optimizing: fields (0, 0.5, 0.8, 0.9 of full field),
   wavelengths and weights, metrics with thresholds, hard constraints (EFL, track, edge
   thickness), variables with bounds.
4. Look before you optimize: layout, spot diagram, ray and OPD fans, Seidel table. Write
   the two-sentence diagnosis from [diagnosis.md](references/diagnosis.md).
5. Optimize progressively: first-order operands, then RMS spot, then wavefront or MTF.
   Open glass variables last and only when color is the limit.
6. Look again and re-diagnose. Compare against the diffraction limit.
7. Save the candidate, reload it, re-measure. Report the re-measured value.
8. If it will be built, tolerance it. Write `summary.json`, render the review, and keep
   a short `notes.md` of what you tried and why.

## Explaining results

- Every number carries its unit, field, wavelength and metric definition (RMS spot
  radius is not a diameter or FWHM; state the sampling for MTF).
- Name the dominant aberration and the evidence for it, then the variable that controls it.
- Say what the optimizer traded, in Seidel terms or in the fans.
- Compare with the diffraction limit: Airy radius 1.22 λ F/#, MTF cutoff 1/(λ F/#).
- State a model limit in one clause where it matters (scalar, paraxial NA, nominal
  design), not in a paragraph. Nominal performance is not yield; say so once when relevant.

## Not this skill

Non-sequential and stray-light design, thin-film coating design, illumination and
non-imaging optics. Say so and stop.

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
