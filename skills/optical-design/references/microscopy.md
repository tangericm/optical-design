# Microscopy: objectives, tube lenses, relays

## Contents

- [Objective classes and correction](#objective-classes-and-correction)
- [Tube lenses, infinity conjugate, parfocal distance](#tube-lenses-infinity-conjugate-parfocal-distance)
- [Modelling an objective from NA and mag](#modelling-an-objective-without-its-prescription)
- [Resolution and sampling](#resolution-and-sampling)
- [Relays: 4f, pupil matching, Lagrange invariant](#relays-4f-pupil-matching-lagrange-invariant)
- [Field flatness, telecentricity, distortion](#field-flatness-telecentricity-distortion)
- [Design forms and where to get them](#design-forms-and-where-to-get-them)
- [Worked example: 20x/0.75 on a 200 mm tube](#worked-example-20x075-on-a-200-mm-tube)

## Objective classes and correction

Correction class trades element count for how many colors focus together and how flat
the field is. Achromats correct two colors and leave visible field curvature and edge
spherical/coma — fine for routine brightfield, wrong for quantitative field work. Plan
achromats add a field flattener (a thick negative meniscus near the image) at the same
color correction. Fluor/semi-apo objectives correct three colors and improve
UV-to-NIR transmission and NA per magnification. Apochromats correct three to four
colors and hold the flattest field at the highest NA — the only class worth using for
quantitative colocalization or ratiometric imaging across a wide field.

NA, working distance and field trade inside a fixed barrel: raising NA at constant
magnification steepens the marginal ray and eats WD; a flatter, wider field needs more
elements off-axis. A 20x can be 0.4 NA/20 mm WD (long-WD, live imaging) or 0.75 NA/1 mm
WD (fixed-sample) — same magnification, different objective. Ask for NA, WD and field
number together; magnification alone under-specifies the part.

Immersion matches medium index to the front element and sample to suppress the
spherical aberration a dry (n=1) objective picks up focusing into higher index, and is
what lets NA exceed 1.0: air tops out near 0.95, water reaches ~1.0–1.2, oil (n≈1.515)
reaches 1.3–1.49. Cover glass is part of the prescription: standard is 0.17 mm (#1.5),
and high-NA dry objectives are most sensitive — a few tens of microns off reintroduces
visible spherical aberration. Long-WD and water-dip objectives often carry a correction
collar for cover-glass thickness or immersion depth; dial it in, don't assume nominal.

"Infinity corrected" means the objective forms no real image alone — rays from an
on-axis point exit parallel to the axis (afocal), and a tube lens converts that
collimated space to a real image. The payoff is the collimated region: filters,
dichroics and beamsplitters sit there without shifting focus. Never mix objectives and
tube lenses across vendors without checking both EFL and color-correction split (below)
— a Nikon objective on a Zeiss tube changes both magnification and residual color.

## Tube lenses, infinity conjugate, parfocal distance

Tube-lens EFL is a vendor convention, not a physical constant, and it sets the actual
magnification once an objective is coupled to a camera:

| Vendor | Tube EFL | Notes |
|---|---|---|
| Nikon (CFI/CFI60) | 200 mm | |
| Leica (HCS) | 200 mm | some color correction split into the tube lens |
| Mitutoyo | 200 mm | infinity-corrected, no correction collar assumed |
| Olympus (UIS/UIS2) | 180 mm | |
| Zeiss (ICS) | 164.5 mm | color correction split into the tube lens |

`objective EFL = tube EFL / magnification`. A "20x" Nikon objective is a 10 mm EFL
element (200/20); the same nominal 20x on an Olympus body is a 9 mm EFL element
(180/20). Substituting a lens designed for one convention behind another rescales the
image and, for Leica/Zeiss, reintroduces color the objective assumed the tube would fix.

Parfocal distance (objective shoulder to focal plane) is standardized within a family
so objectives parfocus when you rotate the nosepiece: 45 mm for the older DIN standard
(also Olympus, Zeiss), 60 mm for Nikon CFI60. It is independent of the tube-lens EFL
above — don't conflate the two 60/45/200/180 numbers when speccing a custom nosepiece
or relay.

## Modelling an objective without its prescription

When you only have NA and magnification (no glass data), model the objective as an
ideal thin lens at `f_obj = tube EFL / magnification`, place the object at its front
focal point, and set its aperture stop one focal length behind it — one EFL from the
objective, in the collimated space. That location is what makes an infinity objective
telecentric in object space, and it is the plane to line up with a tube lens, scanner or
SLM (see relays, below).

Size that stop from the ray height a real marginal ray traces through a thin lens from
its focal point: `semi-diameter = f_obj * tan(asin(NA))`. For a 10x/0.25 Nikon-style
objective, `f_obj = 200/10 = 20 mm`, so `semi-diameter = 20 * tan(asin(0.25)) ≈ 5.16 mm`.
Use `tan(asin(NA))`, not NA itself — at 0.25 NA the two are within 3%, but the gap grows
fast at high NA and undersizes the stop if you drop the tangent.

In OpticStudio, define this with a **float-by-stop-size** aperture (a fixed stop
semi-diameter) plus **ray aiming**, rather than an object-space NA aperture type: with
the object exactly at the front focal point the system is afocal on the object side, and
solving for a marginal ray to hit a declared object-space NA there is the classic
non-convergent case. Fixing the stop size sidesteps the solve entirely.[^1][^2]

## Resolution and sampling

Independent of any relay, the scalar circular-pupil limits at the objective:

- Rayleigh: `0.61 λ / NA`
- Abbe (two-point, in-phase): `λ / (2 NA)`
- FWHM of the intensity PSF: `≈ 0.51 λ / NA`
- Axial: `≈ 2 n λ / NA²`
- Camera Nyquist pixel (object-referred to image space): `pixel = M · Abbe / 2`

```powershell
uv run scripts/resolve.py micro --wavelength-um 0.55 --na 0.75 --magnification 20 \
  --pixel-um 6.5 --json
```

Coherent/transmitted-laser imaging follows a different cutoff than incoherent
fluorescence emission — Abbe's `λ/(2NA)` assumes incoherent, in-phase point sources.
Above roughly NA 0.7–0.8, scalar diffraction breaks down; polarization and apodization
shift the PSF measurably, and a vector (Richards-Wolf) model is needed for anything
quantitative there.

## Relays: 4f, pupil matching, Lagrange invariant

A 4f relay of two lenses `f1, f2` separated by `f1 + f2` reimages an object at the front
focal plane of `f1` to the back focal plane of `f2` at magnification `-f2/f1`, with a
pupil-conjugate plane sitting midway, at each lens's own back/front focal plane. That
mid-relay plane is where a scan mirror, SLM or camera stop belongs: putting the *pupil*
there, not the field, keeps the scan telecentric — the mirror pivots the chief-ray angle
without walking the beam off-axis at the objective. Set the relay magnification to fill
the target aperture (galvo clear aperture, SLM active area) without vignetting or
wasting NA.

Check any proposed relay with the Lagrange (Smith-Helmholtz) invariant `H = n·u·y`
(marginal-ray angle times object/pupil height), conserved end to end by a lossless
system: `NA·(field half-height)` at the objective must match
`(galvo half-angle)·(pupil half-diameter)` once the relay magnification is applied — a
mismatch means the stated NA, field and relay magnification are over-constrained.

## Field flatness, telecentricity, distortion

Petzval sum (`Σ 1/(n·f)` over the powered surfaces) sets the field curvature that no
amount of stop-shifting removes — it is corrected with a field-flattening element
(a thick, low-power negative meniscus close to the image) or by splitting power across
more surfaces with alternating index, which is most of what separates a plan objective
from a plain achromat of the same NA.

Telecentricity in object space (chief ray parallel to the axis, stop at the front focal
plane) keeps magnification constant as the sample moves through focus — required for
comparing feature size across a focus range or a tiled scan. Telecentricity in image
space keeps irradiance and magnification stable as a detector shifts along the axis.
Distortion in a microscope relay is usually held under 0.1–1% for stitching and
metrology; state the criterion (max grid distortion vs. f-theta) rather than a bare %.

## Design forms and where to get them

- **Lister**: air-spaced doublet pair, low NA (≤0.25), the historical low-power form.
- **Amici**: triplet-based, moderate NA, corrects more color than a Lister at the same
  element count.
- **Petzval-type with field flattener**: the basis of most modern plan objectives —
  power split front/back with a flattening element near the image.
- **Double Gauss**: symmetric high-element-count form used for long-WD, higher-NA
  objectives and for tube lenses that need their own color and field correction.

Sources for starting points and worked forms: Zhang and Gross, "Systematic design of
microscope objectives," Parts I–III, *Adv. Opt. Techn.* 2019 — 29 catalogued lens
modules spanning these families.[^3] [lens-designs.com][ldc] is a public `.zmx`
collection including over 100 microscope objectives. Gross, *Handbook of Optical
Systems*, vol. 4 (Survey of Optical Instruments) covers the objective and tube-lens
chapters. Nikon's [MicroscopyU objective properties page][nmu] has the class/NA/WD
conventions above.

## Worked example: 20x/0.75 on a 200 mm tube

Nikon-convention 20x/0.75 objective, 200 mm tube lens, 6.5 µm camera pixel (e.g. a
2048×2048 sCMOS, 13.3 mm square sensor), λ = 0.55 µm.

Object-space pixel: `6.5/20 = 0.325 µm`. Abbe limit at NA 0.75: `0.55/(2·0.75) ≈
0.367 µm`; Nyquist camera pixel `M·Abbe/2 = 20·0.367/2 ≈ 3.67 µm`. The 6.5 µm camera is
undersampled against that target (`resolve.py micro` flags this) — fine for a survey
scan, not for claiming diffraction-limited data; a 2x relay or a smaller-pixel camera
closes the gap. Field of view on the 13.3 mm sensor: `13.3/20 ≈ 0.665 mm`.

For a scan or SLM relay off this objective, the back aperture is roughly `2·f_obj·NA =
2·(200/20)·0.75 = 15 mm` (paraxial estimate — real objectives run smaller). A bare 5 mm
galvo needs about a 3:1 demagnifying relay to receive that pupil without clipping;
check against the Lagrange invariant first, since demagnifying the pupil 3x triples the
marginal-ray angle the galvo and any downstream relay lens must accept.

[^1]: [Zemax: aperture settings for microscope objective simulation](https://community.zemax.com/got-a-question-7/aperture-settings-for-microscope-objective-simulation-1764)
[^2]: [Zemax: first-order simple microscope tutorial](https://community.zemax.com/got-a-question-7/tutorial-for-a-first-order-simple-microscope-design-in-zemax-3193)
[^3]: [Zhang and Gross, Part I](https://www.degruyterbrill.com/document/doi/10.1515/aot-2019-0002/html)

[ldc]: https://www.lens-designs.com/
[nmu]: https://www.microscopyu.com/microscopy-basics/properties-of-microscope-objectives
