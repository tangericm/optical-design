---
name: optical-design
description: >
  Use when reviewing or improving sequential imaging optics, checking resolution,
  PSF/MTF, wavefront or interferometry data, analyzing OpticStudio prescriptions,
  or investigating microscopy and OCT performance and optical tolerances.
license: MIT
compatibility: Python 3.11+ and uv. Portable prescription jobs require Optiland 0.6.2. Native jobs require Windows, a valid OpticStudio ZOS-API license, ZOSPy 2.1.5 and pythonnet 3.1.0.
metadata:
  author: Eric Tang
  repo: https://github.com/tangericm/optical-design
  version: "0.1.0-dev.2"
---

# optical-design

Turn a system requirement into computed optical evidence and a reviewable model change.
Use the scripts for numerical results; identify assumptions, sources, engine versions,
units and analysis settings. Distinguish measured performance from estimates and unavailable data.

## Choose the workflow

| Request | Entry point | Read when relevant |
|---|---|---|
| Resolution, sampling, Gaussian beam, OCT limits | `scripts/resolve.py` | [Microscopy](references/microscopy.md), [OCT](references/oct.md) |
| Zernike coefficients, wavefront PSF/MTF | `scripts/zernike.py`, `scripts/wavefront.py` | [PSF/MTF validity](references/psf-mtf.md) |
| Interferometer maps and pass/surface interpretation | `scripts/interfero.py` | [Interferometry](references/interferometry.md) |
| Audit a sequential prescription against requirements | `scripts/design.py audit` | [Design workflow and schema](references/design-workflow.md) |
| Improve focus within authorized travel | `scripts/design.py refocus` | [Optimization](references/optimization.md) |
| Sensitivity or seeded Monte Carlo | `scripts/design.py tolerance` | [Tolerancing](references/tolerancing.md) |
| Local stock-lens shortlist | `scripts/catalog.py validate` / `match` | [Specifications and catalog schema](references/specifications.md) |
| Reproduce native Huygens/POP intensity profiles on unchanged models | `scripts/benchmark.py` | [Profile benchmark contract](references/profile-benchmark.md) |
| Numerical equivalence | `scripts/compare.py` | [Comparison boundaries](references/design-workflow.md#comparison) |

Prescription audit/refocus/tolerance adapters remain restricted to centered spherical/plane
sequential systems and scalar analyses. The separate native profile backend can analyze
complex surfaces and enable native polarization in mm, single-configuration sequential
models; its POP launch is an explicitly seeded Gaussian waist. This does not establish
general validity for arbitrary prescriptions, beam launches or polarization models.
General multi-variable redesign, live GUI attachment, non-sequential/stray-light analysis,
coatings optimization, thermal/structural coupling, manufacturing release and automatic
web-catalog import remain outside these workflows.

## Run and interpret

Run `uv --version`, then `uv run <skill-dir>/scripts/<name>.py --help` if syntax is unfamiliar.
Tier 0 scripts declare dependencies. Read the design workflow for pinned optional-engine
commands; use `uv run <skill-dir>/scripts/zos.py check --json` to test an actual native license.

For prescription work, establish fields, wavelengths, pupil, units, hard requirements and
analysis settings before optimizing. Use the user's existing specification when supplied.
Ask only for information that materially determines acceptance; label any provisional
assumption. The example specification is a synthetic demonstration, not a default requirement.

Jobs open a **copy** in an owned backend session. `refocus` changes only the final air gap,
within explicit bounds. The source remains unchanged. Accept a candidate only when all
declared constraints pass, its objective gain exceeds the threshold, and native save/reload
reproduces the result. Return baseline/candidate metrics, limitations, source/artifact hashes
and model/report paths. A failed or unavailable metric cannot support acceptance.

`tolerance` uses independent radius/thickness perturbations and no compensator. Report the
seed, distributions, analysis failures, sample count and Wilson interval; sampled pass rate
is conditional on those assumptions and is not a manufacturing-yield certification.

Exit codes: 0 completed/success; 1 comparison mismatch, unmet design requirements or no
acceptable refocus improvement; 2 usage; 3 missing engine/dependency; 4 analysis failure.
Tolerance completion (0) does not imply every trial passed. Inspect the report's yield.
After a failed job, inspect `failure.json`; use a fresh output directory for a retry.

For a profile benchmark, pin model/reference hashes and every case's analysis settings.
Analyze a copy in an owned native session without saving prescription changes. A run without
a reference can complete with `reference_validated: false`; completion is not validation.
Reference agreement establishes same-method numerical reproduction, not design acceptance.
Preserve native coordinate pitch and inspect threshold/ROI sampling status before interpreting
width or flatness. See [profile units and limitations](references/profile-benchmark.md).

## Scientific checks that change decisions

- State pupil geometry and amplitude, coherence, wavelength, image/object-space convention,
  and metric definition. Zernike coefficients require an explicit `fringe`, `noll` or `ansi`
  scheme; normalization and fit aperture affect RMS.
- For wavefront maps, NaNs mean opaque/outside-pupil pixels. They do not encode unknown
  samples to interpolate. Supply the pupil center/radius for translated, clipped or
  obstructed apertures; inspect inferred-geometry warnings.
- Maréchal is an approximation near high Strehl, not a convention detector. At 0.1 waves,
  disagreement with the truncated `1-(2πσ)^2` formula alone does not prove a scheme error.
  Pure defocus has an exact pupil-integral check; use computed diffraction results and
  the stated approximation range. See [PSF/MTF](references/psf-mtf.md).
- Compare aberrated MTF with the **same pupil amplitude and support** with phase removed.
  An annular or apodized pupil can exceed a clear circular reference at some frequencies.
  The clear-circle overlay is a separate reference, not a universal upper bound.
- Scalar/paraxial formulas do not establish high-NA vectorial performance. Express NA with
  refractive index and state approximation limits. Camera sampling also depends on
  magnification, coherence and pixel response; do not apply a universal `Q < 2` verdict.
- Interferometric measured OPD, single-pass wavefront and surface height differ. Set the
  quantity, pass factor and incidence angle explicitly; report removed piston/tilt/defocus.
- Geometric RMS spot radius, PSF width, Strehl and MTF are different metrics. Compare
  identical field/wavelength/axis/frequency and sampling settings, then assess the actual
  requirement. A visually attractive spot or nominal diffraction limit does not prove yield.
- An illumination intensity cut, a point-image PSF and an integrated marginal answer
  different questions. Huygens central cuts are normalized; POP cuts retain absolute
  irradiance. Combine incoherent spectral intensities with declared weights before peak
  normalization. Interpolated coordinates add no native spatial resolution, and a partially
  covered flatness ROI cannot support the full-ROI requirement.

## Representative start

For a camera/objective sampling question, run `resolve.py micro` with the stated wavelength,
NA, magnification and pixel pitch; explain its scalar model limit. For an authorized lens
refocus, follow [the executable example](references/design-workflow.md), substitute the
user's model/specification, and report the saved/reloaded candidate or the reason none passed.
