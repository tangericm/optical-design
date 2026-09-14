# Diagnosis template

After every analysis (fans, spot, Seidel, field curvature), write two sentences: which aberration dominates, at which field
and wavelength, what evidence shows it, and which variable class to release next. See
[aberrations.md](aberrations.md) for the underlying formulae and variable-to-aberration map.

**Template**: "At [field], [wavelength], the [ray fan / OPD fan / Seidel table / field-
curvature plot] shows [signature], consistent with [aberration] dominating over
[secondary aberration]. Releasing [variable class] is the next move because [why it, and
not another variable, controls this term]."

**Example**: "At the 0.9 field, d-line, the tangential ray fan has a dominant even
quadratic shape versus signed pupil coordinate, consistent with primary coma; the
Seidel decomposition and field dependence support that interpretation. Test stop
position and lens bending next, while monitoring astigmatism, distortion and throughput."
A steep odd linear fan instead indicates a focus-like term; differing tangential and
sagittal slopes can indicate astigmatism. Compare actual fans, not just Seidel rankings.

## Decision table

| Signature you observe | Likely cause | Confirm with | Next move |
|---|---|---|---|
| Ray fan same S-curve shape at every field | Spherical | `S_I` largest Seidel term, fan unchanged with field | Bend the lens (shape factor); split the element |
| Even quadratic tangential fan vs signed pupil coordinate, grows with field | Coma | `S_II` term, tangential/sagittal fans differ | Shift the stop; rebalance bending |
| Tangential and sagittal fans have different slope at the same field | Astigmatism | `S_III` term, spot diagram shows crossed ellipse | Split the element; move the stop; add a meniscus |
| Linear fan slope changes with field (focus-like term) | Field curvature | Field-curvature plot bows away from zero with field, `S_IV` (Petzval) nonzero | Add a field flattener; rebalance glass power split by index |
| Grid lines bow with no added blur | Distortion | `S_V` term, chief-ray height vs paraxial prediction | Move the stop relative to the group; check telecentricity |
| Spot size grows across the band, color fringing at the edge | Axial or lateral color | Focus/height shift vs wavelength; `TAchC`/`TchC` operands | Reopen glass as a variable; re-pair Abbe numbers |
| Geometric spot approaches the Airy scale | Diffraction may matter | Compute PSF, wavefront/Strehl or the specified MTF | Evaluate the actual diffraction requirement before deciding to stop |

## Classic misdiagnoses

- **Calling field curvature or defocus "spherical aberration."** Primary spherical in
  centered third-order theory is field independent. Mixed aberrations and higher-order
  spherical can vary across real fields; changing blur alone does not identify a term.
  Separate cubic spherical fan shape from linear defocus and compare per-field best
  focus diagnostically, then evaluate the actual shared detector plane.
- **Blaming the optimizer for a variable it cannot reach.** A pure stop shift at fixed
  aperture/conjugates leaves primary spherical and Petzval invariant. Changes to the
  sampled aperture or higher-order effects can still change measured performance.
- **Treating an Airy-scale geometric spot as proof of diffraction-limited performance.**
  RMS geometric spot and Airy first-zero radius are different measures. Confirm the
  specified wavefront, Strehl or MTF criterion at every required condition.
- **Reporting RMS spot radius as diameter**, understating a violation by 2x, or comparing a
  geometric spot to an MTF-based requirement.

## Why the optimizer looks stuck

- **A single image plane serves all fields.** With field curvature, per-field refocus
  helps diagnose the image shell but cannot replace validation at the real shared
  detector. Optimize a compromise plane or correct the field curvature as required.
- **First-order targets may be inconsistent.** EFL, magnification, track, conjugates
  and principal-plane locations are coupled. Check the actual layout and available
  degrees of freedom before relaxing a requirement; no universal "fix two" rule holds.
- **Glass may limit color correction.** Examine glass dispersion and element power
  distribution together. Radius/thickness changes can change color, but a restricted
  glass/power combination may leave no useful solution; consider catalog alternatives.
- **Variables are sitting at their bounds.** Check the report's parameter vector against
  the declared bounds before concluding the search converged; a variable pinned at a bound
  usually means the bound, not the optimum, is limiting.
