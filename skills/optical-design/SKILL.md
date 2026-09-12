---
name: optical-design
description: >
  Optical design review, analysis and optimization: resolution limits, PSF/MTF, wavefront
  error, Zernike and Seidel aberrations, Strehl, depth of focus, Gaussian beams, tolerancing,
  merit-function design, and design guidance (audit a lens, flag its limitations, suggest and
  apply corrections, find comparable published or stock designs). Use when the user asks
  about lens or imaging system performance, wants a design reviewed or improved, works with
  OCT/microscopy/interferometer optics, Zemax OpticStudio files (.zmx) or ZOS-API, or wants
  numbers checked against diffraction limits — even if they do not name a tool.
license: MIT
compatibility: Requires Python 3.11+ and uv (scripts install their own dependencies on first run). Tier 1 needs optiland; Tier 2 needs Windows with Ansys Zemax OpticStudio Professional/Premium (ZOS-API).
metadata:
  author: Eric Tang
  repo: https://github.com/tangericm/optical-design
  version: "0.1.0-dev.0"
---

# optical-design

Act as a senior optical designer reviewing a colleague's system. Numbers come from the
scripts, never from memory. Every formula you quote names its source.

## Not for

Non-sequential or illumination design, stray light, thin-film coatings, opto-mechanics,
thermal analysis, and physics homework with no system behind it. Say so and stop.

## Modes

State the mode before answering.

| Mode | Use when | Output |
|---|---|---|
| Ask | conceptual or single-number question | formula, source, computed value |
| Analyze | a prescription or wavefront exists | performance table vs diffraction limit and vs spec |
| Audit | user wants review | ranked limitation flags with evidence |
| Improve | audit flags exist | ranked corrections with expected gain/cost, applied and re-verified |
| Research | user needs starting points or comparables | shortlist of designs with citations, imported and analyzed |

This release ships Tier 0 only (closed-form and wavefront math). Prescription analysis
(Tier 1), OpticStudio (Tier 2), audit/improve scripts and references arrive in later releases;
in Audit/Improve/Research modes use Tier 0 scripts for every number and state what could not
be computed.

## Preflight

1. `uv --version`. If missing, tell the user to install uv; do not pip-install into their environment.
2. Run scripts as `uv run <skill-dir>/scripts/<name>.py <subcommand> ... --json`. First run downloads dependencies.
3. Exit code 2 = usage (read `--help`), 3 = missing tier dependency (report the hint verbatim), 4 = analysis failed.

## Conventions

- Lengths in mm, wavelengths in µm (`--wavelength-um`), wavefront in waves at the stated wavelength.
- Zernike coefficients always carry a scheme: `fringe` (Zemax Fringe, unnormalized), `noll`
  (Zemax Standard, RMS-normalized), `ansi` (OSA/ANSI Z80.28, 0-based). Never mix schemes
  without `scripts/zernike.py convert`.
- NA ↔ F/#: paraxial `NA = 1/(2 F#)`. Say "paraxial" when you use it above NA ≈ 0.3.
- Report: quantity, value, unit, method/tier, and the limit it is compared to.

## Sanity rules

- Strehl and RMS wavefront error must agree with Maréchal (`S ≈ 1 − (2πσ)²`) when σ ≤ 0.1 waves. If not, the scheme or normalization radius is wrong.
- No MTF value exceeds the diffraction-limited curve. `wavefront.py mtf` overlays it.
- PSF and detector sampling: `Q = λF#/p`; Q < 2 aliases. Run `wavefront.py sample-check`.
- When geometric and diffraction numbers disagree, report both and say which governs.
- Diffraction limit is a floor, not a target: a design at the floor with no margin fails tolerancing.

## Scripts

| Script | Subcommands | Use for |
|---|---|---|
| `scripts/resolve.py` | airy, rayleigh, dof, gaussian, oct-axial, oct-lateral, micro, telescope | closed-form limits |
| `scripts/zernike.py` | convert, rms, strehl, seidel-from-zernike, fit | coefficient math |
| `scripts/wavefront.py` | psf, mtf, sample-check | diffraction from a wavefront |
| `scripts/interfero.py` | psi, unwrap, fringe-to-wfe, cavity | interferometer data |
| `scripts/compare.py` | (two JSON files) | before/after and cross-engine checks |

`--help` on any subcommand prints an example.

## Worked pattern

User: "Is my 0.8 NA objective at 520 nm sampled properly on a 6.5 µm camera at 40×?"

1. Mode: Ask. `resolve.py micro --wavelength-um 0.52 --na 0.8 --magnification 40 --pixel-um 6.5 --json`
2. Read `nyquist_pixel_um` and `sampling_ratio`; report Abbe/Rayleigh values with the method string.
3. If `warnings` lists "undersampled", say by how much and what magnification fixes it.

## Red flags

- "The diffraction limit is close enough" → run the script; quote the number and the margin.
- "The Zernike convention doesn't matter here" → it changes the value by up to √(2(n+1)); convert.
- "I'll estimate the PSF" → `wavefront.py psf`.
- "OpticStudio said so" → OpticStudio output still gets checked against `resolve.py` limits.
