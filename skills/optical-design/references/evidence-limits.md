# Evidence limits

Numerical assumptions apply where relevant to every result. The detailed job, mutation
and adapter contracts below describe audited mode; direct Optiland recipes have broader
capabilities but must independently preserve inputs and check saved-candidate requirements.
Import fidelity and unsupported source settings remain part of the result.

## Model scope

- Audited portable adapter: centered refractive spherical/plane systems, scalar analyses only.
- Direct Optiland code can use additional engine features; faithful import is assessed separately.
- Native: Standard conics, EvenAspheric A2–A16 fixed; units mm, solves fixed, no apertures/decenters/tilts.
- Native field normalization radial, no vignetting; 17-ray validation catches gross failures, not all clipping.
- Automatic apertures are not mechanical clear apertures.
- `inspect_zmx.py` opens any OpticStudio export through Optiland; the audited `design.py` portable path still accepts only its spherical subset.
- Coatings, coordinate breaks, multi-configuration prescriptions reject.
- Profile backend allows complex sequential surfaces with native polarization in mm single-config models.
- Profile backend does not expand scalar prescription adapters or certify arbitrary beam launch/coatings.

## Numerical validity

- Scalar Fraunhofer, uniform amplitude, binary pupil; no polarization, apodization or nonplanar image surface.
- FFT and Huygens differ in validity and sampling; consult engine docs for high-NA pupils.
- Pad minimum two, changes only focal-plane sampling, not measured pupil information.
- Without explicit normalization assumes symmetric rim; NaNs are opaque, not unmeasured pixels.
- Map input removes piston, tilt, defocus; record handling choices.
- Exponential variance approximate, cannot diagnose convention errors alone.
- Annular pupil exceeds clear-circle at some frequencies; use ideal_x/y bounds.
- Finite sampling, sampled peaks, width interpolation remain approximations.
- Q below two flags aliasing under stated cutoff; actual content scene-dependent.
- Native Huygens coordinates µm for mm models, converted to x_mm by dividing 1000.
- Do not add half-pixel offsets, recenter peaks or replace grid conventions when importing datasets.
- POP absolute irradiance W/mm²; one-D cut integral not transmitted power; central cut not marginal.
- Normalize active spectral weights, multiply absolute irradiance by weight then sum for incoherent mean.
- Do not sum independently peak-normalized profiles, coherent amplitudes or inactive wavelengths.
- Huygens wavelength zero uses active spectrum, not monochromatic sum.
- Widths are outermost crossings at 0.5 and exp(−2) with linear interpolation only.
- Missing outer crossings unavailable; undersampling marked even with interpolation.
- Flatness CV uses population std dev divided by mean without peak recentering.
- ROI fully covered, at least five samples, no gap > quarter width; narrow window insufficient.
- Spectral interpolation adds no spatial information, not energy-conserving.
- Preserve grid pitch/provenance not union as native resolution; diagnostics minimum checks.
- Matching curves cannot resolve Huygens–POP disagreement; wavelength-bandwidth approximates frequency.
- Phase index controls refraction, do not substitute group index; state one-way vs round-trip depth.

## Audited optimization and tolerancing

- Local deterministic search, not global optimum proof; small budgets provide only coarse exploration.
- Baseline may lie outside bounds; all applied values must lie inside.
- Search may miss narrow feasible intervals or local optima; one slot reserved for verification.
- Infeasible or unavailable required metrics never earn acceptance.
- Native calls can block past deadline; late results rejected; native code errors abort with evidence.
- Hash externally changed fails acceptance; report written only after successful restoration and teardown.
- Failures retain failure.json with restoration, source and attempted-evaluation evidence.
- Saved parameters must reproduce within 1e-12 relative / 1e-12 mm; reloaded objectives within 1e-5 / 1e-8.
- Tolerancing does not model complete manufacturing or alignment processes.
- Max_evaluations limits per-row analysis calls; global timeout remains cooperative between calls.
- Intervals conditional on declared perturbation model, engine, bounded rule; incomplete runs may stop informatively.
- Sampled pass fractions not manufacturing guarantees; two marginal intervals not confidence interval for improvement.
- Sensitivity ranking local, no interactions unless explicit; never drop unfavorable draws.
- Focus-only must be described as focus sensitivity, not yield analysis.
- Wilson method quantifies sampling uncertainty, not incorrect manufacturing model uncertainty.

## Audited provenance

- Jobs open copy in owned session; source unchanged; never reuse rejected candidates.
- Edit requires expected original and requested value; checks saved/reloaded candidate against requirements.
- Accept changed candidate only when all constraints pass and save/reload reproduces result.
- Expected originals checked before any evaluation; stale values abort operation.
- Coupled changes detected by checking after each setter.
- Inspection and backend getters must agree; undeclared state and axial translations must remain fixed.
- Reload must preserve requested cells, state, metric identities, units and values.
- Hashes pinned when created and checked after teardown; altered evidence cannot get new hashes.
- Measurement buffers copied at evaluation time; later calls cannot rewrite baselines.
- Output directories new or empty; report written only after successful teardown and verification.
- Never treat surviving candidate as accepted unless report successful and verified.
- Failed jobs preserve failure.json with evidence; sensitive data never embedded in logs.

## Outside scope

- Non-sequential, stray-light, thermal coupling, manufacturing release outside workflows.
- Audited mode excludes topology/glass optimization, live GUI, web-catalog import and portable aspheres.
  Direct recipes include glass substitution and conic/asphere variables; this is not audited acceptance.
- Coordinate breaks, multi-config, coating optimization, material/temperature tolerances, decenter/tilt unsupported.
- POP Gaussian-waist launch only, not arbitrary fields; manufacturing acceptance requires separate evidence.
- Magnification alone does not establish resolution; do not fill unknown objective data generically.
- High-NA or polarization-sensitive needs vector model; scalar calculator insufficient.
