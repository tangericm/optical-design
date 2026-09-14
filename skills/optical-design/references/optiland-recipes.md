# Optiland recipes

Fourteen short, tested snippets for real lens-design work directly against Optiland 0.6.2, the engine this skill pins. Each is something to adapt, not a black box to call. All run as-is against `optiland.samples` objects, no fixture needed: `uv run --python 3.11 --with optiland==0.6.2 --with matplotlib python snippet.py` (add `--with scipy`, or `--with pandas --with seaborn` for tolerancing — normal Optiland dependencies already).

Conventions: lengths mm, wavelengths µm (`optic.primary_wavelength`, every `wavelength=`); multiply by 1000 for µm-scale display values. Field args to analysis classes are normalized `Hx, Hy` in `[-1, 1]`, not an index — `Hy=1.0` is the full-field edge; `fields="all"` uses `optic.fields`'s own points. `.view()` defaults to `plt.show()`; pass `show=False` and set `matplotlib.use("Agg")` before importing pyplot when headless, and save with `fig.savefig(...)`. `optiland.__version__` reports `0.6.1` even pinned to `optiland==0.6.2` — a packaging quirk, not a real mismatch. Work on a copy: hash the source before touching it, never write back to the input path, and re-measure whatever you save (recipe 13) before reporting a number.

## Contents

1. [Load, inspect, save](#1-load-inspect-and-save-a-copy) · 2. [First-order summary](#2-first-order-summary) · 3. [Layout plot](#3-layout-plot) · 4. [Spot diagram](#4-spot-diagram) · 5. [Ray/OPD fan](#5-ray-fan-and-opd-fan) · 6. [Field curvature/distortion](#6-field-curvature-and-distortion) · 7. [Seidel/third-order](#7-seidel-and-third-order-aberrations) · 8. [Wavefront/Strehl/MTF](#8-rms-wavefront-strehl-and-mtf) · 9. [Build/run optimization](#9-build-and-run-an-optimization-problem) · 10. [Global search, polish](#10-global-search-then-polish) · 11. [GlassExpert](#11-glass-substitution-with-glassexpert) · 12. [Tolerancing/yield](#12-tolerancing-perturb-compensate-sample-yield) · 13. [Re-measure saved candidate](#13-re-measure-the-saved-candidate) · 14. [Export summary.json](#14-export-figures-and-a-summaryjson)

## 1. Load, inspect, and save a copy
Use when you're handed a `.zmx` and need to look at it and start a working copy without touching the original.
```python
import hashlib
from pathlib import Path
from optiland.fileio import load_zemax_file, save_zemax_file, save_optiland_file
from optiland.samples.objectives import CookeTriplet

# Setup: synthesize a .zmx as the "input file" a user would hand you.
src = Path("input.zmx")
save_zemax_file(CookeTriplet(), str(src))

# --- recipe proper starts here ---
sha256 = hashlib.sha256(src.read_bytes()).hexdigest()
optic = load_zemax_file(str(src))            # never write back to `src`
optic.info()                                  # prints a surface table; returns None

out_dir = Path("out")
out_dir.mkdir(exist_ok=True)
save_optiland_file(optic, str(out_dir / "copy.json"))   # native round-trip format
save_zemax_file(optic, str(out_dir / "copy.zmx"))        # re-export to .zmx
print(sha256[:12], (out_dir / "copy.json").exists(), (out_dir / "copy.zmx").exists())
```
Read: `optic.info()` prints radius/thickness/material/conic/semi-aperture — the first sanity check; comparing the source hash before and after work is your receipt that `src` was never mutated. Pitfall: successful `load_zemax_file` parsing does not establish faithful representation of every OpticStudio setting. Use `inspect_zmx.py` to review units, unsupported directives, and importer warnings before accepting numerical results; non-mm prescriptions need explicit conversion. `save_zemax_file` writes UTF-16 LE and warns on glasses with no catalog entry — read those warnings.

## 2. First-order summary
Use before anything else — catches over-constrained specs (EFL, magnification and track length are coupled) before you waste a merit function on an impossible target.
```python
import numpy as np
from optiland.samples.objectives import CookeTriplet

optic = CookeTriplet()
p = optic.paraxial
n = len(optic.surfaces.surfaces)
image_distance = float(optic.surfaces.get_thickness(n - 2)[0])
bfl = image_distance + float(p.F2())  # back focus is relative to current image plane
print("EFL", p.f2(), "BFL", bfl, "image distance", image_distance, "FNO", p.FNO(), "total_track", optic.total_track)
print("EPD", p.EPD(), "XPD", p.XPD(), "mag", p.magnification(), "invariant", p.invariant())

orig = optic.wavelengths.primary_index  # EFL spread at each wavelength
for i, w in enumerate(optic.wavelengths.wavelengths):
    optic.wavelengths.primary_index = i
    print(w.value, "um -> EFL", float(p.f2()))
optic.wavelengths.primary_index = orig

y_chief, u_chief = p.chief_ray()  # paraxial chief ray heights/angles at the edge field
angle_deg = float(np.degrees(np.arctan(np.ravel(u_chief)[-1])))
print("image-space chief-ray angle (deg), 0 = telecentric:", angle_deg)
```
Read: BFL is measured from the last optical vertex to paraxial back focus; image distance is the current final air gap. Moving the image plane changes only the latter. EFL/F#/total-track is the spec-consistency check; per-wavelength EFL spread is a chromatic focal-length diagnostic, not the chromatic best-image-plane shift; chief-ray angle near 0° at the edge field means image-space telecentric. Pitfall: `paraxial.f2()` always uses `optic.primary_wavelength`, no wavelength argument — sweep by reassigning `optic.wavelengths.primary_index` and restoring it, as above.

## 3. Layout plot
Use for the first thing anyone should see: a cross-section with real rays, at every field and wavelength.
```python
import matplotlib
matplotlib.use("Agg")
from optiland.samples.objectives import CookeTriplet

optic = CookeTriplet()
fig, ax = optic.draw(fields="all", wavelengths="all", num_rays=5, figsize=(8, 4))
fig.savefig("layout.png", dpi=150)
```
Read: rays clipping a surface edge or the mechanical aperture are visible immediately, often faster than a vignetting table. Pitfall: `draw()` never calls `plt.show()` itself; still set the `Agg` backend before anything imports `matplotlib.pyplot`. `projection="XZ"` (default `"YZ"`) picks the plane.

## 4. Spot diagram
Use to see geometric blur by field and wavelength, against the diffraction limit.
```python
import matplotlib
matplotlib.use("Agg")
from optiland.samples.objectives import CookeTriplet
from optiland.analysis import SpotDiagram

optic = CookeTriplet()
spot = SpotDiagram(optic, fields="all", wavelengths="all")
rms = spot.rms_spot_radius()  # list[field][wavelength] of arrays, mm
for i, field in enumerate(spot.fields):
    print(field.coord, [float(v) for v in rms[i]])

fig, axs = spot.view(add_airy_disk=True, show=False)
fig.savefig("spot.png", dpi=150)

p = optic.paraxial
airy_radius_mm = 1.22 * float(p.FNO()) * optic.primary_wavelength / 1000.0
print("Airy radius (mm)", airy_radius_mm)
```
Read: RMS spot within 1-2x the Airy radius is essentially diffraction limited; several times larger means geometric aberration dominates. Pitfall: `rms_spot_radius()` centers on the chief ray by default; pass `reference="centroid"` at construction for centroid spots — the two differ under real coma.

## 5. Ray fan and OPD fan
Use to diagnose which aberration limits a field, by wavelength, from curve shape rather than a single number.
```python
import matplotlib
matplotlib.use("Agg")
from optiland.samples.objectives import CookeTriplet
from optiland.analysis import RayFan, PupilAberration

optic = CookeTriplet()
fan = RayFan(optic, fields="all", wavelengths="all")
fig, axs = fan.view(figsize=(9, 3.5), show=False)
fig.savefig("rayfan.png", dpi=150)

opd = PupilAberration(optic, fields="all", wavelengths="all")  # OPD fan
fig2, axs2 = opd.view(figsize=(9, 3.5), show=False)
fig2.savefig("opdfan.png", dpi=150)
```
Read, by shape: tilted line through origin = defocus; symmetric parabola = spherical; asymmetric S-curve odd about the origin = coma; tangential/sagittal fans separating = astigmatism; curves shifting vertically between wavelengths = lateral color. Pitfall: read at the specific field you're diagnosing, not averaged — coma only at 0.8-1.0 field says release a stop-shift/bending variable, not a spherical-correcting one.

## 6. Field curvature and distortion
Use to see how focus shift and image-height error grow with field, tangential versus sagittal.
```python
import matplotlib
matplotlib.use("Agg")
from optiland.samples.objectives import CookeTriplet
from optiland.analysis import FieldCurvature, Distortion

optic = CookeTriplet()
fc = FieldCurvature(optic, wavelengths="all")
fig, ax = fc.view(figsize=(6, 5), show=False)
fig.savefig("field_curvature.png", dpi=150)

dist = Distortion(optic, wavelengths="all")
fig2, ax2 = dist.view(figsize=(6, 5), show=False)
fig2.savefig("distortion.png", dpi=150)
```
Read: field curvature plots tangential/sagittal focus shift (mm) versus field — the gap is astigmatism, the mean is Petzval curvature; distortion is percent image-height error, positive pincushion, negative barrel. Pitfall: both plot versus real field coordinate, not normalized `Hy` — check axis units against a spec in degrees or mm of object height.

## 7. Seidel and third-order aberrations
Use once you need to know which term is responsible for poor image quality, so you pick the right variable.
```python
from optiland.samples.objectives import CookeTriplet

optic = CookeTriplet()
S = optic.aberrations.seidels()
print("Seidel sums SI..SV", S)

names = ["TSC", "SC", "CC", "TCC", "TAC", "AC", "TPC", "PC", "DC", "TAchC", "LchC", "TchC"]
vals = optic.aberrations.third_order()
for name, v in zip(names, vals):
    print(name, v.sum())
```
Read: `SI` spherical, `SII` coma, `SIII` astigmatism, `SIV` Petzval, `SV` distortion — one large term with the others small says exactly what's wrong; `third_order()` gives the same families per-surface first, to see which surface generates it. Variable that usually controls each: spherical — bending or a stop-side asphere; coma — stop position/shift; astigmatism — stop-to-element distance; Petzval — glass pair index split or a field flattener (bending barely touches it); distortion — stop position vs. a strongly-curved element; axial color — the crown/flint Abbe split; lateral color — glass choice plus stop position. Pitfall: these are paraxial sums, not real-ray RMS — offsetting large terms can still leave a small residual spot; cross-check with recipe 4.

## 8. RMS wavefront, Strehl, and MTF
Use to quantify diffraction-limited performance versus field and defocus, beyond geometric blur.
```python
import numpy as np
from optiland.samples.objectives import CookeTriplet
from optiland.analysis import RmsWavefrontErrorVsField, ThroughFocusMTF
from optiland.mtf import FFTMTF
from optiland.psf import ScalarFFTPSF

optic = CookeTriplet()
wf = RmsWavefrontErrorVsField(optic, num_fields=8)
wf.view(show=False)[0].savefig("rms_wavefront.png", dpi=150)
rms_waves = np.asarray(wf._wavefront_error)  # (field, wavelength)
marechal = np.exp(-(2 * np.pi * rms_waves) ** 2)  # only valid below ~0.2 waves RMS
strehl_fft = ScalarFFTPSF(optic, field=(0, 0), wavelength=optic.primary_wavelength).strehl_ratio()
print("rms waves on axis", rms_waves[0], "Marechal", marechal[0], "actual FFT Strehl", strehl_fft)

FFTMTF(optic, fields="all").view(add_reference=True)[0].savefig("mtf.png", dpi=150)  # dashed = diffraction limit

tf = ThroughFocusMTF(optic, spatial_frequency=30, delta_focus=0.02, num_steps=5)
tf.view(show=False)[0].savefig("through_focus_mtf.png", dpi=150)
```
Read: `add_reference=True` overlays the diffraction-limited MTF curve at the on-axis working F/# — close to it at your required frequency is a pass; through-focus MTF shows focus latitude and whether best focus sits away from paraxial focus. Pitfall: Maréchal's `Strehl ≈ exp(-(2π·RMS)²)` is valid only under ~0.2 waves RMS — above that it badly underestimates Strehl (above: ~0.5 waves RMS gives Maréchal ~1e-6 against an actual FFT Strehl around 0.3); trust `ScalarFFTPSF(...).strehl_ratio()` instead once you're not near diffraction limit. Scalar FFT MTF assumes unpolarized light on a clear pupil; not valid above roughly NA 0.6 (`VectorialFFTMTF` handles that).

## 9. Build and run an optimization problem
Use once requirements are frozen and you've picked free surfaces/parameters — the standard damped-least-squares path Optiland provides, no bespoke pattern search.
```python
from optiland.samples.objectives import CookeTriplet
from optiland.optimization import OptimizationProblem, LeastSquares

optic = CookeTriplet()
img = len(optic.surfaces.surfaces) - 1
problem = OptimizationProblem()
problem.add_operand("f2", target=optic.paraxial.f2(), weight=1.0, input_data={"optic": optic})  # 1) first-order op first
for hy in (0.0, 0.5, 0.8, 0.9):  # 2) then RMS spot at 0/0.5/0.8/0.9 of full field
    d = {"optic": optic, "surface_number": img, "Hx": 0.0, "Hy": hy, "num_rays": 6, "wavelength": optic.primary_wavelength}
    problem.add_operand("rms_spot_size", target=0.0, weight=1.0, input_data=d)
d = {"optic": optic, "surface_number": img, "Hx": 0.0, "Hy": 1.0, "Px": 0.0, "Py": 0.0, "wavelength": optic.primary_wavelength}
problem.add_operand("real_M", target=0.0, weight=0.5, input_data=d)  # 3) telecentricity: chief-ray angle at edge field
# variables: glass frozen (not a variable); radius/thickness/conic shown. Same call for aspheres:
# add_variable(optic, "asphere_coeff", surface_number=N, coeff_number=0, min_val=-1e-3, max_val=1e-3)
problem.add_variable(optic, "radius", surface_number=1, min_val=15, max_val=30)
problem.add_variable(optic, "thickness", surface_number=4, min_val=2, max_val=8)
problem.add_variable(optic, "conic", surface_number=5, min_val=-2, max_val=2)
before = (float(problem.sum_squared()), [v.variable.get_value() for v in problem.variables])
LeastSquares(problem).optimize(maxiter=50, method_choice="trf")
print("merit", before[0], "->", float(problem.sum_squared()))
for v, b in zip(problem.variables, before[1]):
    print(v.type, v.kwargs["surface_number"], b, "->", v.variable.get_value())
```
Read: `sum_squared()` before/after is the merit value, smaller is better; it does not establish acceptance. After saving and reloading, measure RMS spot at every required wavelength and field, including the full-field edge `Hy=1.0`, and compare each result with its frozen threshold. The edge chief-ray-angle operand above does not measure edge blur. Per-variable values above are real physical units (mm), not solver-scaled space. Pitfall: `v.value` is the *scaled* solver value — always read `v.variable.get_value()` to report a number; every operand needs `optic` in its `input_data`, paraxial ones included. Follow the progressive order in the comments — first-order operand first, then spot, then wavefront/MTF; freeze glass until shape converges.

## 10. Global search, then polish
Use when local least-squares gets stuck in a merit-function local minimum and you need a broader search before the final polish.
```python
from optiland.samples.objectives import CookeTriplet
from optiland.optimization import OptimizationProblem, LeastSquares, DifferentialEvolution

optic = CookeTriplet()
img = len(optic.surfaces.surfaces) - 1
problem = OptimizationProblem()
problem.add_operand("f2", target=optic.paraxial.f2(), weight=1.0, input_data={"optic": optic})
d = {"optic": optic, "surface_number": img, "Hx": 0.0, "Hy": 0.8, "num_rays": 6, "wavelength": optic.primary_wavelength}
problem.add_operand("rms_spot_size", target=0.0, weight=1.0, input_data=d)
problem.add_variable(optic, "radius", surface_number=1, min_val=15, max_val=30)  # DE needs finite bounds on every var
problem.add_variable(optic, "conic", surface_number=5, min_val=-1, max_val=1)

DifferentialEvolution(problem).optimize(maxiter=3, workers=1, disp=False)  # coarse global step, tiny budget
print("after DE", float(problem.sum_squared()))
LeastSquares(problem).optimize(maxiter=30, method_choice="trf")  # polish to a local optimum
print("after polish", float(problem.sum_squared()))
```
Read: DE's merit after the coarse step won't be fully converged — the point is landing in the right basin; the polish afterward should drop further, fast. Pitfall: `DifferentialEvolution.optimize()` raises `ValueError` if any variable lacks a bound, unlike `LeastSquares`. A real budget is `maxiter` in the hundreds with `workers=-1`; here `maxiter=3, workers=1` only keeps this recipe fast. `CMAES` is the other global option, same bounded-variable requirement.

## 11. Glass substitution with GlassExpert
Use to search a glass catalog for a better crown/flint choice instead of hand-picking candidates.
```python
from optiland.samples.objectives import CookeTriplet
from optiland.optimization import OptimizationProblem, GlassExpert

optic = CookeTriplet()
print("before", optic.surfaces.surfaces[1].material_post.name)
problem = OptimizationProblem()
problem.add_operand("f2", target=optic.paraxial.f2(), weight=1.0, input_data={"optic": optic})
d = {"optic": optic, "surface_number": 7, "Hx": 0.0, "Hy": 0.8, "num_rays": 6, "wavelength": optic.primary_wavelength}
problem.add_operand("rms_spot_size", target=0.0, weight=1.0, input_data=d)
candidates = ["SK16", "N-BK7", "N-SK16", "LAK9", "N-SSK8", "F2", "N-F2", "SF5"]
problem.add_variable(optic, "material", surface_number=1, glass_selection=candidates)
problem.add_variable(optic, "radius", surface_number=1, min_val=15, max_val=30)  # local refinement needs a continuous var
GlassExpert(problem).run(num_neighbours=2, maxiter=20, disp=False, verbose=False)
print("after", optic.surfaces.surfaces[1].material_post.name)
```
Read: `GlassExpert` greedily searches (n_d, V_d) space — a broad catalog pass, then a focused pass near the winner, scoring each candidate with a local optimization; `material_post.name` after `run()` is the chosen glass. Pitfall: it needs at least one continuous variable alongside `"material"` — per-candidate scoring runs a local optimization and fails with a bounds error otherwise. To lock a glass, just don't add a `"material"` variable for that surface in any later problem — omission is the lock.

## 12. Tolerancing: perturb, compensate, sample yield
Use to turn "how sensitive is this to manufacturing error" into a number: a sensitivity sweep per tolerance, then a Monte Carlo yield estimate with everything applied at once.
```python
import numpy as np
from optiland.samples.objectives import CookeTriplet
from optiland.tolerancing import Tolerancing
from optiland.tolerancing.perturbation import DistributionSampler, RangeSampler
from optiland.tolerancing.sensitivity_analysis import SensitivityAnalysis
from optiland.tolerancing.monte_carlo import MonteCarlo

optic = CookeTriplet()
op = {"optic": optic, "surface_number": 7, "Hx": 0.0, "Hy": 0.0, "num_rays": 6, "wavelength": optic.primary_wavelength}
sens = Tolerancing(optic)
sens.add_operand("rms_spot_size", input_data=op)
r0 = float(optic.surfaces.radii[1])
sens.add_perturbation("radius", RangeSampler(r0 - 0.05, r0 + 0.05, 5), surface_number=1)
sens.add_compensator("thickness", surface_number=6, min_val=40, max_val=45)  # focus compensator
SensitivityAnalysis(sens).run()  # sweeps one perturbation at a time; see sens output in ._results
mc_tol = Tolerancing(optic)  # separate problem: Monte Carlo perturbs everything at once
mc_tol.add_operand("rms_spot_size", input_data=op)
for s in (1, 2, 3, 5, 6):
    r0 = float(optic.surfaces.radii[s])
    mc_tol.add_perturbation("radius", DistributionSampler("normal", loc=r0, scale=0.05, seed=s), surface_number=s)
mc_tol.add_compensator("thickness", surface_number=6, min_val=40, max_val=45)
mc = MonteCarlo(mc_tol)
mc.run(num_iterations=30)
spot = mc._results[mc.operand_names[0]].to_numpy()
n, k, z = len(spot), int(np.sum(spot < 0.0044)), 1.96  # requirement: RMS spot < 4.4 um
p = k / n
half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)  # Wilson score interval
center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
print(f"yield {p:.2f}, Wilson 95% CI [{center - half:.2f}, {center + half:.2f}]")
```
Read: `SensitivityAnalysis._results` is a per-step DataFrame — the tolerance that moves the operand most is the one to tighten first; report the Monte Carlo yield with its Wilson interval, not the raw fraction — 30 trials gives a wide interval and a normal-approximation CI breaks down near 0 or 1. Pitfall: `Perturbation.apply()` sets the variable to the sampler's value directly, not a delta — `DistributionSampler("normal", loc=0.0, ...)` drives a radius to near-zero and NaNs result; use `loc=<current value>`, as above. `SensitivityAnalysis` requires `RangeSampler`; `MonteCarlo` expects `DistributionSampler` — use two `Tolerancing` instances, not one.

## 13. Re-measure the saved candidate
Use as the last step before reporting any number: prove the saved file reproduces the number you're about to claim.
```python
import hashlib
from pathlib import Path
from optiland.samples.objectives import CookeTriplet
from optiland.fileio import save_optiland_file, load_optiland_file
from optiland.analysis import SpotDiagram

optic = CookeTriplet()
rms_before = float(SpotDiagram(optic, fields=[(0.0, 0.0)]).rms_spot_radius()[0][0])

out = Path("candidate.json")
save_optiland_file(optic, str(out))
sha_saved = hashlib.sha256(out.read_bytes()).hexdigest()

reloaded = load_optiland_file(str(out))
rms_after = float(SpotDiagram(reloaded, fields=[(0.0, 0.0)]).rms_spot_radius()[0][0])

print("pre-save RMS", rms_before, "post-reload RMS", rms_after)
assert abs(rms_before - rms_after) < 1e-9, "save/reload did not round-trip the metric"
print("hash of saved candidate", sha_saved[:12])
```
Read: the two RMS values should agree to numerical noise; if not, the save/load path silently changed the model (a dropped solve, an unresolved pickup) — don't trust it. Pitfall: this is cheap and belongs in every workflow that saves a file, not as a one-off test — the same discipline the skill's job runner enforces by construction, applied to code you write yourself.

## 14. Export figures and a summary.json
Use as the final step of a review: bundle first-order numbers, metrics, and the figures a human will look at into one file a renderer can consume.
```python
import hashlib, json
from importlib.metadata import version
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
from optiland.samples.objectives import CookeTriplet
from optiland.analysis import SpotDiagram
from optiland.mtf import FFTMTF

optic = CookeTriplet()
out = Path("review"); out.mkdir(exist_ok=True)
optic.draw(fields="all", wavelengths="all")[0].savefig(out / "layout.png", dpi=150, bbox_inches="tight")
spot = SpotDiagram(optic, fields="all", wavelengths="all", reference="centroid")
spot.view(add_airy_disk=True, show=False)[0].savefig(out / "spot.png", dpi=150, bbox_inches="tight")
FFTMTF(optic, fields="all").view(add_reference=True)[0].savefig(out / "mtf.png", dpi=150, bbox_inches="tight")
rms = spot.rms_spot_radius()
model_hash = hashlib.sha256(json.dumps(optic.to_dict(), sort_keys=True, default=str).encode()).hexdigest()
summary = {
    "schema_version": 1,
    "model": "CookeTriplet", "sha256": model_hash, "sha256_kind": "in_memory_json",
    "engine": {"name": "optiland", "version": version("optiland")},
    "evidence": {"status": "measured", "method": "SpotDiagram; centroid reference; all configured fields and wavelengths"},
    "first_order": {"EFL": {"value": float(optic.paraxial.f2()), "unit": "mm"},
                    "F/#": {"value": float(optic.paraxial.FNO()), "unit": "1"},
                    "Total track": {"value": float(optic.total_track), "unit": "mm"}},
    "metrics": [{"name": "RMS spot radius", "field": str(field.coord), "wavelength": float(w.value),
                 "value": float(rms[i][j]) * 1000, "unit": "um"}
                for i, field in enumerate(spot.fields) for j, w in enumerate(spot.wavelengths)],
    "figures": {"layout": "layout.png", "spot": "spot.png", "mtf": "mtf.png"},
    "captions": {"layout": "Ray paths through the lens at all configured fields and wavelengths.",
                 "spot": "Geometric blur by field and wavelength. Smaller spots mean tighter ray concentration; the circle is the Airy reference.",
                 "mtf": "Contrast transfer versus spatial frequency; compare each field with the dashed diffraction reference."},
}
(out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
print(sorted(p.name for p in out.iterdir()))
```
Read: this emits version 1 of the contract documented in `scripts/render_review.py`; pass its `review/summary.json` directly to that script with `--summary` and a user-owned `--out` HTML path. No requirement was declared, so the report does not claim acceptance or diffraction-limited performance. Add numeric `requirement: {"max": ...}` or `{"min": ...}` per metric only when agreed; the renderer derives threshold status and rejects contradictory `pass` flags. A `verdict`, if supplied, is visibly an authored interpretation. The default evidence status is `supplied`; `measured` records the analysis method; `reloaded` additionally requires a saved candidate hash and exactly one round-trip check for every reported metric. Each check copies the metric's `name`, all supplied `field`, `wavelength`, `frequency`, `axis` conditions, and `unit`; its `after_reload` must equal the reported `value`, and its `before_save` must agree within its declared finite `tolerance`. Rendering never independently verifies optical claims. Pitfall: `sha256_kind` distinguishes source file bytes, saved candidate bytes, and the in-memory JSON representation used here. Recipe 13 shows how to obtain saved-file evidence; `scripts/walkthrough.py --out <new-user-directory>` connects a bundled model, bounded focus, save/reload and this report contract.

## Links

[Optiland documentation](https://optiland.readthedocs.io/en/latest/) and its [analysis framework guide](https://optiland.readthedocs.io/en/latest/developers_guide/analysis_framework.html). Source read for every recipe above, for the full argument list of any class used only partially here: [`fileio`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/fileio/__init__.py), [`paraxial.py`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/paraxial.py), [`aberrations`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/aberrations/__init__.py), [`optimization`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/optimization/__init__.py), [`glass_expert.py`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/optimization/optimizer/scipy/glass_expert.py), [`tolerancing`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/tolerancing/core.py).
