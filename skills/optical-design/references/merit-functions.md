# Building a merit function

The practitioner recipe for turning a specification into an operand list an optimizer can
actually converge on, plus the audited-mode composite merit that `scripts/design.py`
implements when you need the receipt discipline instead of hand-written code. For the
aberration theory behind why each operand matters, see [aberrations.md](aberrations.md)
and [diagnosis.md](diagnosis.md); for runnable Optiland snippets beyond the one skeleton
below, see [optiland-recipes.md](optiland-recipes.md).

## Contents

- [Build order](#build-order)
- [Freeze glass early](#freeze-glass-early)
- [Field and wavelength sampling](#field-and-wavelength-sampling)
- [Hard constraints, targets and weights](#hard-constraints-targets-and-weights)
- [The over-constraint check](#the-over-constraint-check)
- [Edge and center thickness](#edge-and-center-thickness)
- [Telecentricity and distortion](#telecentricity-and-distortion)
- [Reading the merit history](#reading-the-merit-history)
- [An Optiland skeleton](#an-optiland-skeleton)
- [Audited-mode composite merit (design.py)](#audited-mode-composite-merit-designpy)

## Build order

Build the merit function in this order and do not skip ahead: first-order operands (EFL,
magnification, back focus, total track), then RMS spot, then OPD or RMS wavefront, then MTF
at the frequencies the requirement actually names. A Zemax community thread on generic
merit-function construction puts it plainly: the default wizard operands "target the basic
image quality of the system (RMS spot, RMS wavefront, Contrast)... the bedrock of getting
good image quality," and problem-specific operands (chief ray angle, distortion, custom
constraints) get added only "once the system reaches viability"
([community.zemax.com](https://community.zemax.com/got-a-question-7/generic-optimization-mf-for-lens-design-problem-solving-4733)).
Chasing MTF before first-order and spot size wastes evaluations on a system that cannot
converge for a more basic reason. The Ansys singlet tutorial follows the same order: optimize
RMS spot radius about the centroid first, then layer in thickness and edge-thickness bounds
([Ansys singlet part 3](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization)).

## Freeze glass early

Treat glass as fixed while radius, thickness and conic converge; a material variable makes
every other gradient noisier and can hide a shape problem behind a glass swap that will not
survive re-optimization. Reopen glass only when the diagnosis says color is the limiting
aberration (axial or lateral color dominant — see [diagnosis.md](diagnosis.md)), and then
vary it deliberately: either a declared candidate list or Optiland's GlassExpert, not a
free continuous index/Abbe pair with no catalog constraint.

## Field and wavelength sampling

Fields at 0, 0.5, 0.8 and 0.9 of full field are one illustrative optimization grid. A microscope-design
thread gives the reasoning directly: use non-uniform field heights "0.0, 0.5, 0.8, 0.9...
this weights the optimization toward higher aberrations at edge fields" instead of
diluting the merit function with redundant near-axis samples where third-order aberrations
are small by construction
([community.zemax.com](https://community.zemax.com/got-a-question-7/designing-a-microscope-3013)).
Weight fields and wavelengths deliberately rather than leaving every sample at weight 1:
weight the field where the requirement is tightest (often the edge) more heavily, and
weight wavelengths by the source's actual spectral weighting, not uniformly across the band.

Final acceptance must include **1.0 full field**, each required wavelength and the
actual requirement boundary (frequency, pupil/aperture and focus convention). Increase
sampling until results are stable enough for the stated tolerance. Optimization samples
at 0.9 field cannot establish an edge-of-field requirement.

## Hard constraints, targets and weights

Keep acceptance separate from optimization guidance. A **hard acceptance requirement**
must pass independently of merit. An operand **target** is a weighted equality residual;
operand `min_val`/`max_val` are inequality penalties that contribute residual only outside
the interval. In Optiland 0.6.2 these are soft penalties, not guaranteed feasibility
constraints: see [`Operand.delta_ineq()` and `delta()`](https://github.com/optiland/optiland/blob/v0.6.2/optiland/optimization/operand/operand.py).
A large weight still permits tradeoffs. Bounds on optimization **variables** constrain
the search parameters when supported by the selected solver, a separate mechanism from
operand penalties. Validate all physical requirements again on the final saved/reloaded
candidate. `scripts/design.py` independently gates hard requirements on acceptance.

## The over-constraint check

EFL, magnification, total track, conjugates and principal-plane locations are coupled.
Whether three targets are inconsistent depends on the layout and its remaining degrees
of freedom; a multi-element system can move its principal planes. Run a paraxial
feasibility check with the actual fixed quantities and variable bounds before deciding
which target to relax. Do not apply a universal "fix two, float the third" rule.

## Edge and center thickness

Center and edge thickness are manufacturing and vignetting constraints, not image-quality
operands — model them as bounds, not targets. The Ansys singlet tutorial bounds center
thickness between 2 and 12 mm and requires edge thickness greater than 2 mm via the glass
boundary constraints, independent of the RMS spot objective being minimized
([Ansys singlet part 3](https://optics.ansys.com/hc/en-us/articles/42661700528275-How-to-design-a-singlet-lens-Part-3-Optimization)).
Use Optiland's `edge_thickness` operand with `min_val` as an inequality penalty and an
intentional weight. Then measure and gate the final edge thickness independently.

## Telecentricity and distortion

Telecentricity is a constraint on the chief ray angle at the image (or, for object-space
telecentricity, at the entrance pupil), not on spot size. Distortion is a constraint on
chief-ray height versus its paraxial prediction, not on wavefront error at all (see the
[distortion row in aberrations.md](aberrations.md#the-five-seidel-aberrations-plus-color)).
The microscope thread's `RAID`-style approach — sampling chief-ray angle across several
field points and driving it toward zero — is the general pattern for telecentric scan and
relay lenses
([community.zemax.com](https://community.zemax.com/got-a-question-7/designing-a-microscope-3013)).
In Optiland, build these from ray-tracing operands at `Px=Py=0` (chief ray) rather than the
hexapolar spot/wavefront operands used for image quality.

## Reading the merit history

Falling merit with shrinking step size is normal convergence; a flat history with the step
size still large usually means a variable is pinned at its bound (see
[diagnosis.md](diagnosis.md#why-the-optimizer-looks-stuck)), not a converged optimum. Stop
when: the merit is no longer improving by more than the evaluation noise floor (ray-grid
sampling, finite-difference step size), the residual is already at or below the
diffraction limit for the metric in question, or every remaining gain requires a variable
class (usually glass) you have deliberately not released yet. Do not keep adding
evaluation budget to squeeze a merit value below what the sampling density can resolve.

## An Optiland skeleton

```python
from optiland.optimization import OptimizationProblem, LeastSquares
problem = OptimizationProblem()
# 1. First-order: hold EFL near 50 mm
problem.add_operand("f2", target=50.0, weight=10, input_data={"optic": lens})
# 2. RMS spot at 0, 0.5, 0.8, 0.9 field (not uniform); glass still frozen
spot = {"optic": lens, "surface_number": -1, "num_rays": 6, "wavelength": 0.587}
for Hy in (0.0, 0.5, 0.8, 0.9):
    problem.add_operand("rms_spot_size", target=0.0, input_data={**spot, "Hx": 0, "Hy": Hy})
# 3. Edge thickness inequality penalty; final acceptance still needs an explicit check
edge = {"optic": lens, "surface_number": 2}
problem.add_operand("edge_thickness", min_val=2.0, input_data=edge)

problem.add_variable(lens, "radius", surface_number=2)
problem.add_variable(lens, "thickness", surface_number=2, min_val=2.0, max_val=12.0)
LeastSquares(problem).optimize()
# After saving/reloading: evaluate every requirement, including Hy=1.0 and all
# declared wavelengths. Neither a low merit nor min_val proves acceptance.
```

See [optiland-recipes.md](optiland-recipes.md) for the OPD/wavefront and Seidel-table
recipes, glass variables via GlassExpert, and the full analysis set.

## Audited-mode composite merit (design.py)

`design.py`'s objective uses supported measured metrics at exact field/wavelength/frequency
identities; hard requirements remain separate gates an improved merit cannot override. A
scalar objective keeps its schema: `{"metric": "rms_spot_um", "field": 1, "wavelength": 1,
"direction": "minimize"}`. For several conditions or mixed units, use a composite:

```json
{"direction": "minimize", "aggregation": "weighted_rms", "terms": [
  {"metric": "efl_mm", "unit": "mm", "target": 50, "scale": 2, "weight": 1},
  {"metric": "rms_spot_um", "field": 1, "wavelength": 1,
   "unit": "um", "target": 0, "scale": 10, "weight": 3},
  {"metric": "mtf", "field": 2, "wavelength": 1, "frequency": 50,
   "axis": "sagittal", "unit": "1", "target": 0.8, "scale": 0.1, "weight": 2}]}
```

Merit is `sqrt(sum(weight_i * ((value_i - target_i) / scale_i)^2) / sum(weight_i))`. Scales
express the deviation's significance; weights adjust relative emphasis after normalization.
Targets express equality — values above and below an MTF target both incur a residual; use
a separate minimum-MTF requirement for a one-sided bound. Reports carry `objective_value`
and `objective_breakdown` (per-term measured value, target, scale, weight, signed
`normalized_residual`, `weighted_residual`) wherever merit is evaluated. Python consumers
use `DesignSpec.objective_metrics`, `objective_breakdown(spec, measurements)` and
`objective_value(spec, measurements)`.
