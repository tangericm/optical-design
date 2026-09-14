# Diagnosis template

After every analysis (fans, spot, Seidel, field curvature), write two sentences: which aberration dominates, at which field
and wavelength, what evidence shows it, and which variable class to release next. See
[aberrations.md](aberrations.md) for the underlying formulae and variable-to-aberration map.

**Template**: "At [field], [wavelength], the [ray fan / OPD fan / Seidel table / field-
curvature plot] shows [signature], consistent with [aberration] dominating over
[secondary aberration]. Releasing [variable class] is the next move because [why it, and
not another variable, controls this term]."

**Example**: "At the 0.9 field, d-line, the tangential ray fan is a steep odd-symmetric
line while the sagittal fan is nearly flat, and `S_II` is 4x the next-largest Seidel term —
coma dominates, not astigmatism. Stop position is the next variable, since coma is the only
primary aberration a stop shift removes for free without touching spherical."

## Decision table

| Signature you observe | Likely cause | Confirm with | Next move |
|---|---|---|---|
| Ray fan same S-curve shape at every field | Spherical | `S_I` largest Seidel term, fan unchanged with field | Bend the lens (shape factor); split the element |
| Ray fan asymmetric, odd about center, grows with field | Coma | `S_II` term, tangential/sagittal fans differ | Shift the stop; rebalance bending |
| Tangential and sagittal fans have different slope at the same field | Astigmatism | `S_III` term, spot diagram shows crossed ellipse | Split the element; move the stop; add a meniscus |
| Whole fan shifts (looks like defocus) and the shift grows with field | Field curvature | Field-curvature plot bows away from zero with field, `S_IV` (Petzval) nonzero | Add a field flattener; rebalance glass power split by index |
| Grid lines bow with no added blur | Distortion | `S_V` term, chief-ray height vs paraxial prediction | Move the stop relative to the group; check telecentricity |
| Spot size grows across the band, color fringing at the edge | Axial or lateral color | Focus/height shift vs wavelength; `TAchC`/`TchC` operands | Reopen glass as a variable; re-pair Abbe numbers |
| Everything is close to the Airy disk and further "improvement" is noise | Diffraction-limited | RMS spot near `1.22 lambda F/#`, Strehl ≥ 0.8 | Stop optimizing this metric; check the next one (MTF, tolerance) |

## Classic misdiagnoses

- **Calling field curvature or defocus "spherical aberration."** Spherical is field-
  independent; if the blur or fan shape changes with field, it is field curvature,
  astigmatism, or plain defocus, not spherical. A Zemax community thread on exactly this
  confusion: "I think you may be confusing spherical aberration with defocus. They are two
  different aberrations," and the fix was per-field focus (multi-configuration or a variable
  image distance), not removing an operand
  ([community.zemax.com](https://community.zemax.com/got-a-question-7/removing-spherical-aberration-from-optimization-2027)).
- **Blaming the optimizer for a variable it cannot reach.** Spherical and the Petzval sum
  are stop-shift invariant (see [aberrations.md](aberrations.md#stop-shift)); no amount of
  stop-position search fixes them.
- **Treating a diffraction-limited residual as an error to chase.** Once RMS spot is near
  the Airy radius, further "improvement" is fitting sampling and ray-grid noise.
- **Reporting RMS spot radius as diameter**, understating a violation by 2x, or comparing a
  geometric spot to an MTF-based requirement.

## Why the optimizer looks stuck

- **A single image plane serves all fields.** Off-axis fields need their own best focus
  when field curvature is present; one shared image surface forces the merit function to
  average across fields instead of showing the real per-field aberration.
- **EFL, magnification and total track are over-constrained together.** These three are
  coupled by the first-order relations; fixing all three as separate hard targets leaves no
  freedom for the optimizer to satisfy any of them exactly. Fix two and let the third float.
- **Glass is frozen where color is the limiting aberration.** If axial or lateral color
  dominates, no amount of radius/thickness search closes the gap; the Abbe-number split has
  to become a variable.
- **Variables are sitting at their bounds.** Check the report's parameter vector against
  the declared bounds before concluding the search converged; a variable pinned at a bound
  usually means the bound, not the optimum, is limiting.
