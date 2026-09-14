# Capabilities and limits

[Documentation](README.md) / Capabilities

## What's inside

| Area | Shipped scope |
|---|---|
| Calculators (no engine) | Airy radius and FWHM; Rayleigh, Abbe and Sparrow limits; diffraction and geometric depth of focus; telescope Rayleigh and Dawes; Gaussian beam waist, Rayleigh range, divergence and focused spot; OCT axial resolution and lateral spot with confocal parameter; microscope lateral/axial resolution and Nyquist pixel. `uv run scripts/resolve.py <subcommand> --json` |
| Wavefront tools (no engine) | Zernike coefficients in Fringe, Noll and ANSI schemes; scalar FFT PSF, Strehl and MTF from coefficients or a measured map; interferogram interpretation (OPD, single pass, surface), phase unwrapping, fringe cavity model. `scripts/zernike.py`, `scripts/wavefront.py`, `scripts/interfero.py` |
| Thin scripts | `inspect_zmx.py` opens any real OpticStudio export through Optiland's own reader and reports surfaces, fields, wavelengths and ignored cosmetic directives; `first_order.py` runs the paraxial gate (EFL, BFL, F-number, pupils, chromatic focal shift, telecentricity) against a declared spec; `render_review.py` turns a `summary.json` plus PNGs into a self-contained HTML/Markdown review — no optical engine of its own |
| Optiland recipes | Fourteen short, tested snippets an agent adapts directly against Optiland 0.6.2: load/inspect/save, first-order summary, layout, spot diagram, ray and OPD fans, field curvature and distortion, Seidel and third-order aberrations, RMS wavefront/Strehl/MTF, build and run an optimization (damped least squares), global search then polish, glass substitution with GlassExpert, tolerancing (perturb/compensate/sample yield), re-measure a saved candidate, export a summary and figures. [Optiland recipes](../skills/optical-design/references/optiland-recipes.md) |
| Primer and domain references | [Aberrations](../skills/optical-design/references/aberrations.md) (five Seidel terms plus axial/lateral color, sign conventions, which variable controls each, Petzval sum, Maréchal/Rayleigh criteria); [diagnosis](../skills/optical-design/references/diagnosis.md); [microscopy](../skills/optical-design/references/microscopy.md); [OCT](../skills/optical-design/references/oct.md); [PSF/MTF](../skills/optical-design/references/psf-mtf.md); [interferometry](../skills/optical-design/references/interferometry.md); [merit functions](../skills/optical-design/references/merit-functions.md); [tolerancing](../skills/optical-design/references/tolerancing.md) |
| Forms library | Eleven starting designs (`.zmx` and Optiland JSON, each with commentary): cemented and air-spaced achromats, Cooke triplet, Tessar, double Gauss, Petzval, telephoto, 20x/60x microscope objectives, OCT semi-Plössl scan lens, 4f relay. [Forms library](../skills/optical-design/assets/forms/README.md) |
| Evals | Five scenarios in `evals/evals.json` — diagnose a `.zmx`, match an objective to a camera through a relay, rebalance a scan lens across a wavelength band, optimize a triplet, tolerance a doublet — plus `check_first_order.py` as ground truth for grading. [Evals](../skills/optical-design/evals/README.md) |
| Audited mode | The original job runner (`design.py`, `review.py`, `server.py`, `zos.py`, `benchmark.py`): every job works on a copy, hashes source and artifacts, re-measures the saved candidate after reload, and refuses a change that fails a declared requirement. Deliberately narrow — spherical/plane prescriptions on the portable backend (fixed conics and even aspheres on native), radius/thickness variables only, at most four for `optimize`, and six scalar metrics. [Audited mode](../skills/optical-design/references/audited/README.md) |
| OpticStudio | The same recipes and the audited job runner both run through licensed OpticStudio via ZOSPy 2.1.5 on Windows — optional, not required for any of the above. [OpticStudio](../skills/optical-design/references/opticstudio.md) |

## Engine and execution

| Backend | Needs | Status |
|---|---|---|
| Calculators and review rendering | Python 3.11+, uv; declared numerical dependencies | shipped, no optical engine |
| Optiland (recipes and audited mode) | Optiland 0.6.2 through `uv run --with optiland==0.6.2` | shipped; recipes cover most of what Optiland exposes, audited mode a bounded subset |
| OpticStudio (recipes and audited mode) | Windows, valid OpticStudio API license; ZOSPy 2.1.5, pythonnet 3.1.0 | optional, owned standalone session |

Exit codes across the thin scripts and audited mode: 0 success, 1 a failed gate,
requirement, or comparison mismatch, 2 usage, 3 missing engine, 4 analysis failure.
A completed tolerance job may contain failed trials; inspect its yield and errors.

## Model and analysis limits

The Optiland recipes carry whatever Optiland 0.6.2 itself supports: Standard,
EvenAsphere, OddAsphere, Forbes Q, Zernike, Chebyshev, toroidal, biconic and grid-sag
surfaces; radius, thickness, conic, asphere, polynomial coefficient and refractive-index
(GlassExpert) variables; damped least squares, global and evolutionary optimizers.
`inspect_zmx.py` and the recipes read a real OpticStudio export through Optiland's own
reader — cosmetic directives (`AUTH`, `ENVD`, `RAIM`, …) are reported as ignored rather
than rejecting the file.

Audited mode keeps its original, narrower contract: the portable backend supports
centered spherical/plane sequential systems, the native backend also supports fixed
Standard conics and EvenAspheric coefficients (fixed during edits and optimization).
Variables are radius and thickness only, at most four for `optimize`. Metrics are EFL,
F-number, total track, image distance, RMS spot radius and FFT MTF at one frequency.
Coatings, coordinate breaks and multi-configuration prescriptions reject.

Neither path covers non-sequential and stray-light design, thin-film coating design,
illumination and non-imaging optics, or manufacturing release. See
[evidence limits](../skills/optical-design/references/evidence-limits.md) for the
complete, terse list of numerical, optimization, and provenance limits, and
[compatibility](compatibility.md) for tested engine versions.
