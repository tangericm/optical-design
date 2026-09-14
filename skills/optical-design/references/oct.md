# OCT: sample-arm optics

## Contents

- [Axial and lateral resolution are independent](#axial-and-lateral-resolution-are-independent)
- [Sample-arm forms](#sample-arm-forms)
- [What to require and measure over scan and band](#what-to-require-and-measure-over-scan-and-band)
- [Worked example: 840 nm, 4 mm beam, 36 mm scan lens](#worked-example-840-nm-4-mm-beam-36-mm-scan-lens)
- [Ray trace versus interferometric measurement](#ray-trace-versus-interferometric-measurement)

## Axial and lateral resolution are independent

Axial resolution comes from the source spectrum through the interferometer, not from
the sample-arm optics; lateral resolution comes from the sample-arm focusing geometry
alone. Design them separately, then check the one coupling that matters — depth of
focus versus imaging range — below.

For a Gaussian spectrum of FWHM `Δλ` centered at `λ0`, in a medium of index `n`:

`δz = (2 ln2 / π) · λ0² / (n Δλ)`

840 nm center, 50 nm FWHM, air: `δz ≈ 6.2 µm`. The same source in tissue (`n ≈ 1.38`)
gives `δz ≈ 4.5 µm` — the coherence length in air divided by the group index, not the
bandwidth recomputed at a shifted center wavelength.

Lateral resolution and depth of focus come from the focusing beam, using the OCT-typical
1/e² form:

`δx ≈ 4 λ f / (π d)` (equivalent to the `0.61 λ/NA` Rayleigh form for a Gaussian beam)

`b = π δx² / (2 λ)` — the confocal parameter, twice the Rayleigh range, the axial span
over which the beam stays within `√2` of its waist size.

Tighter lateral focus (smaller `δx`, larger effective NA) buys resolution at the direct
cost of `b`, which shrinks with `δx²` — a fast scan lens that resolves 3 µm laterally
may hold focus over only tens of microns, well inside a single B-scan's depth range.

Imaging range from spectrometer sampling, per detector pixel of bandwidth
`Δλ_pixel`: `z_max = λ0² / (4 Δλ_pixel)` — the Nyquist-limited unambiguous depth of the
spectral-domain system, independent of the source bandwidth above.

Depth coordinates need the **group** index, not the phase index used for ray-trace
refraction — using phase index for depth scaling under-corrects dispersive media.
Sources: [NCBI OCT technology chapter](https://www.ncbi.nlm.nih.gov/books/NBK554044/);
Drexler and Fujimoto, *Optical Coherence Tomography*, ch. 2.

```powershell
uv run scripts/resolve.py oct-axial --center-wavelength-um 0.84 --bandwidth-nm 50 \
  --n 1.38 --json
uv run scripts/resolve.py oct-lateral --wavelength-um 0.84 --focal-mm 36 \
  --beam-diameter-mm 4 --json
uv run scripts/resolve.py gaussian --wavelength-um 0.84 --input-w-mm 2 \
  --focal-mm 36 --json
```

## Sample-arm forms

- **Single achromat.** Cheapest, usable to about ±2° of scan before off-axis
  aberration eats the spot budget — fine for a fixed-beam probe, marginal for a
  wide-field galvo scan.
- **Semi-Plössl (two achromats face to face).** Near diffraction-limited spot out to
  about ±6° of scan against ~2° for the single doublet — the standard upgrade when a
  scan lens isn't justified but a single element isn't enough
  ([Yang et al., Appl. Opt. 55, 646 (2016)](https://opg.optica.org/ao/abstract.cfm?uri=ao-55-4-646),
  reporting near-diffraction-limited performance to 6.4° against 2° for a single
  achromat).
- **Telecentric f-theta scan lens.** Purpose-built for galvo scanning: flat, telecentric
  field with controlled distortion across the full scan angle. Vendor example, Thorlabs
  LSM03/LSM03-BB (36 mm EFL, 4 mm entrance pupil, ±10.6° single-axis scan; LSM03 covers
  1250–1380 nm, the -BB variant 800–1100 nm) and LSM03-VIS (39 mm EFL, 25.1 mm working
  distance, 9.9 µm mean spot, 0.58 mm depth of view, 10.3 mm FOV, 400–700 nm) — verify
  against the current datasheet before locking a BOM
  ([Thorlabs scan lenses](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_ID=10343)).
- **Keplerian relay between two galvo mirrors.** For a two-axis scan, relay the first
  mirror onto the second so both pivot points are conjugate to the entrance pupil —
  without it the second axis scans off a moving pupil and the field vignettes and
  aberrates asymmetrically as the first mirror moves
  ([Zemax: simulating 2D galvo mirrors](https://community.zemax.com/got-a-question-7/simulation-of-2d-galvano-mirrors-in-zemax-3821)).
- **Reflective Schwarzschild.** Two-mirror, all-reflective, no chromatic focal shift —
  the option when the source bandwidth is too broad (or spans too many decades, e.g.
  visible through NIR) for any refractive form to hold focus across it
  ([Schwarzschild scan objective for OCT](https://pmc.ncbi.nlm.nih.gov/articles/PMC6410919/)).

## What to require and measure over scan and band

Run each of these across the full scan angle and the full source FWHM, not just on
axis at the center wavelength:

- Lateral spot size versus scan angle — the number the sample-arm form list above is
  ranked by.
- Chromatic focal shift across the source FWHM, relative to the confocal parameter `b`
  at the design wavelength — small compared to `b` is invisible in the B-scan;
  comparable to `b` measurably softens focus at the band edges.
- Telecentricity error, measured as image-space chief-ray angle at the sample — this is
  what flattens or bows a B-scan. Custom broadband telecentric objectives have reached
  1.3 arcsec nominal telecentricity over a 40 mm field
  ([Xu, Chaudhuri and Rolland, Opt. Express 27, 6184 (2019)](https://opg.optica.org/oe/fulltext.cfm?uri=oe-27-5-6184)),
  useful as a sense of how tight "good" is for a metrology-grade design; imaging systems
  run looser.
- f-theta distortion — scan-angle-to-image-height linearity, which is what a flattening
  algorithm downstream assumes is already correct.
- Beam clipping at the galvo mirror clear aperture across the full scan range, not just
  at zero scan angle.
- Back reflections and ghost foci near zero delay — any near-normal-incidence surface
  in the sample arm puts a bright ghost at its own optical path length, which can land
  inside the imaging range.
- Reference-arm dispersion matching to the sample-arm glass path, including the
  objective and any relay — a mismatch broadens the axial PSF symmetrically and is
  usually the first thing to check when measured `δz` exceeds the Gaussian-spectrum
  estimate.
- Working distance, against the physical probe or handpiece envelope.

## Worked example: 840 nm, 4 mm beam, 36 mm scan lens

840 nm ± 25 nm FWHM source (Δλ = 50 nm), 4 mm 1/e² beam at the scan lens, an
LSM03-BB-class 36 mm EFL telecentric scan lens.

Lateral: `δx = 4·0.84·36 / (π·4) ≈ 9.6 µm`; confocal parameter
`b = π·9.6² / (2·0.84) ≈ 173 µm` (`resolve.py oct-lateral` above). Axial, Gaussian
spectrum: `δz ≈ 6.2 µm` in air, `≈ 4.5 µm` in tissue (`n = 1.38`).

A 150 µm chromatic focal shift across the source band is worth checking against `b`,
not against `δz` — 150 µm is about 87% of the 173 µm confocal parameter, so it is not
negligible: the blue and red edges of the source would focus close to one confocal
parameter apart, softening the effective lateral resolution and sensitivity at the band
edges even though the shift is invisible in the axial-resolution number. That is the
usual case for correcting focal shift with an achromatizing pair rather than dismissing
it because it is small compared to the working distance.

## Ray trace versus interferometric measurement

A sequential ray trace verifies the geometric and diffraction-limited parts of the
sample arm — spot size and its scan-angle dependence, telecentricity, distortion,
vignetting and chromatic focal shift against a computed depth of focus. It does not
verify interferometric sensitivity (source power, detector and reference-arm
efficiency reaching the detector), roll-off with depth (a spectrometer or swept-source
property, not a sample-arm one), or the measured axial PSF (which folds in real source
spectral shape, dispersion mismatch and reconstruction windowing that a Gaussian-FWHM
formula only approximates). Budget the sample arm by ray trace; confirm the system by
measuring an axial PSF and a roll-off curve on the assembled instrument.
