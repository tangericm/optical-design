# Aberration and diffraction primer

The principles and formulae behind every number the scripts report: the five Seidel
aberrations and color, how each shows up in a spot diagram or fan plot, which variable
class corrects it, the diffraction limits that say when you are done, and the sign and
unit conventions to state alongside any result.

## Contents

- [Sign conventions and units](#sign-conventions-and-units)
- [Wavefront and transverse aberration notation](#wavefront-and-transverse-aberration-notation)
- [The five Seidel aberrations plus color](#the-five-seidel-aberrations-plus-color)
- [Petzval sum and field flatness](#petzval-sum-and-field-flatness)
- [Stop shift](#stop-shift)
- [Scaling rules](#scaling-rules)
- [Diffraction limits and criteria](#diffraction-limits-and-criteria)
- [Chromatic aberration](#chromatic-aberration)
- [Sources](#sources)

## Sign conventions and units

State these with every number you report; they are the most common source of a factor-of-two
or a sign error, not the arithmetic.

- **Field**: full or half field, angle (deg, object or image space) or image height (mm).
  `Hy = 0.7` is a normalized field fraction, not a field angle.
- **Wavelength**: vacuum wavelength in nm or um unless stated, and which medium (air vs
  immersion) the propagation constant uses.
- **Spot size**: RMS radius, RMS diameter, geometric (100%) radius and FWHM differ by up to
  4x. State which one a number is before comparing it to a requirement.
- **F-number / NA**: working (image-space) F/# differs from the infinity F/#; for microscope
  objectives use NA, not F/#, once NA exceeds about 0.25.
- **Sign of curvature/thickness**: light travels left to right; radius is positive if the
  center of curvature is to the right of the surface, thickness positive in the direction of
  propagation. Optiland and most `.zmx` files follow this.

## Wavefront and transverse aberration notation

The wavefront error at the exit pupil, relative to the reference sphere, is written as a
power series in normalized pupil coordinates `(rho, theta)` and normalized field `h`
(Hopkins notation, used by Optiland's Seidel operands and by most lens-design texts):

```
W(h, rho, theta) = W020 rho^2                      (defocus)
                  + W040 rho^4                      (spherical)
                  + W131 h rho^3 cos(theta)          (coma)
                  + W222 h^2 rho^2 cos^2(theta)      (astigmatism)
                  + W220 h^2 rho^2                   (field curvature)
                  + W311 h^3 rho cos(theta)          (distortion)
```

Transverse ray error at the image is proportional to the pupil gradient of `W`:
`(eps_x, eps_y) ~ -(R/n') grad_pupil(W)` (use physical pupil coordinates;
normalized coordinates require the pupil-radius scale factor), so each transverse term has one fewer
power of `rho` than its wavefront term. That single relation explains every row below:
spherical's wavefront is quartic in aperture so its ray error is cubic; coma's wavefront is
cubic in aperture and linear in field so its ray error is quadratic in aperture; and so on.

## The five Seidel aberrations plus color

| Aberration | Wavefront term | Transverse form | Spot diagram | Ray fan | OPD fan | Primary variable |
|---|---|---|---|---|---|---|
| Spherical | `W040 rho^4` | `eps ~ rho^3`, field-independent | Circular blur, same at every field, grows with aperture | Symmetric S-curve, same at all fields | Symmetric bowl, same at all fields | Lens bending (shape factor), stop-independent |
| Coma | `W131 h rho^3 cos(theta)` | `eps ~ h rho^2` | Asymmetric "comet" flare pointing toward or away from axis, worse off-axis | Even quadratic tangential ray error vs signed pupil coordinate; may be offset by the reference ray | Odd cubic tangential OPD, possibly with reference tilt removed; grows with field | Stop position (shift), lens bending |
| Astigmatism | `W222 h^2 rho^2 cos^2(theta)` | `eps ~ h^2 rho` | Elongated or crossed ellipse; tangential and sagittal foci separate | Tangential fan slopes differently from sagittal fan; equal aperture, unequal slope | Saddle shape, opposite sign in the two pupil axes | Stop shift, element splitting, meniscus bending |
| Field curvature | `W220 h^2 rho^2` | `eps ~ h^2 rho` | Best focus shifts axially with field; sharp on-axis, soft at the edge at one focus | Fan tilts as a whole (looks like defocus) but the tilt grows with field | Whole fan shifts in piston/defocus with field | Field flattener, Petzval-reducing element, glass power split |
| Distortion | `W311 h^3 rho cos(theta)` | `eps ~ h^3`, aperture-independent | No blur; grid lines bow in (pincushion) or out (barrel), image points stay sharp | Constant mapping offset vs pupil coordinate; chief ray is at pupil center, not the fan edge | Linear pupil tilt relative to Gaussian image; removed when the reference follows the displaced image | Stop position relative to a lens group, especially in wide-field or telecentric designs |
| Axial (longitudinal) color | Focus shift `Delta f(lambda)` | Blur circle whose size depends on defocus at each wavelength | Colored halo, same shape as spherical but with per-wavelength focus offset | Fans for each wavelength are offset along the defocus axis, same shape otherwise | OPD bowls for each wavelength offset in piston/defocus | Glass pair (Abbe number split), achromat power split |
| Lateral (transverse) color | Chief-ray height difference `Delta y'(lambda)` | Image height differs by wavelength at fixed field | Color fringing that grows linearly with field, worst at the edge | Chief-ray endpoints separate by wavelength; marginal-ray shape is unaffected | Small, mostly a field-dependent piston/tilt difference between wavelengths | Stop position, achromatizing the chief ray (not just the marginal ray) |

Field curvature and astigmatism share the same `h^2 rho^2` wavefront dependence; the
Seidel sums keep them as separate terms (`S_III` astigmatism, `S_IV` Petzval) because they
respond to different variables and because Petzval curvature is what remains when
astigmatism is corrected to zero (see below).

## Petzval sum and field flatness

For centered refracting surfaces, define the Petzval sum with positive radius toward
+z and surface power `Phi_j = (n_after,j - n_before,j) / R_j`:

```
P = sum_j Phi_j / (n_before,j * n_after,j)
  = sum_j (n_after,j - n_before,j) / (R_j * n_before,j * n_after,j)
```

Both adjacent indices matter. For a thin lens of index `n` in air, its two surfaces
combine to `P = phi_element / n`; only under that thin-element-in-air approximation
may the element formula replace the surface sum. For the usual axial image-sag
convention the Petzval radius satisfies `1/R_P = -n_image * P`; state the convention
when comparing signed curvature plots. See Sasián, [Theory of sixth-order wave
aberrations, Table 3](https://wp.optics.arizona.edu/jsasian/wp-content/uploads/sites/33/2016/03/published-six-order-theory.pdf),
whose curvature increment is `c * Delta(1/n)`.

Petzval curvature describes the common image shell when astigmatism is zero, which
need not be flat. Redistributing positive and negative element powers and indices can
reduce the sum; a near-image negative field flattener is one possible design choice.
A zero sum alone does not remove astigmatism or higher-order field errors. Confirm
actual sagittal and tangential best-focus surfaces across the required field.

## Stop shift

In centered third-order theory, moving the stop with fixed power distribution,
conjugates and marginal-ray normalization leaves spherical (`S_I`) and Petzval
(`S_IV`) unchanged. Coma acquires a term proportional to stop shift times spherical;
astigmatism and distortion also change. A stop shift can therefore trade these terms,
but does not remove coma "for free." Aperture changes, vignetting, high-order effects
and altered conjugates require a new trace. Exact symmetry cancellation requires
matching object/image conjugates and symmetric groups; a Cooke triplet is not in
general such a symmetric system. Confirm the effect in actual fans and Seidel data.

## Scaling rules

How each aberration's size changes as you change the aperture (`y`, the marginal ray
height or semi-aperture) or the field (`h`), for a fixed design:

| Aberration | Wavefront scales as | Transverse ray scales as |
|---|---|---|
| Spherical | `y^4` | `y^3` |
| Coma | `y^3 h` | `y^2 h` |
| Astigmatism / field curvature | `y^2 h^2` | `y h^2` |
| Distortion | `y h^3` | `h^3` (aperture-independent) |

Stopping down one stop (aperture halved) cuts transverse spherical 8x, but lateral color
and distortion do not depend on aperture at all. Doubling the field grows distortion's
transverse error 8x (`h^3`) against only 4x for astigmatism and field curvature (`h^2`),
which is why distortion and lateral color, not astigmatism, usually dominate at the edge of
a wide-field lens.

## Diffraction limits and criteria

- **Airy radius**: `r_Airy = 1.22 * lambda * F/#` (image-space F/#), or `0.61 * lambda / NA`
  in object space — the practical floor for spot size.
- **Incoherent MTF cutoff**: `f_cutoff = 1 / (lambda * F/#)` cycles/mm, where the
  diffraction MTF of a clear circular pupil reaches zero. No correction raises contrast
  above the diffraction envelope past this frequency.
- **Rayleigh quarter-wave criterion**: peak-to-valley wavefront error `<= lambda/4` is the
  classical threshold for "acceptable" imaging, a loose one relative to Maréchal.
- **Maréchal criterion**: RMS wavefront error `sigma <= lambda/14` corresponds to Strehl
  ratio `~0.8`, the conventional "diffraction-limited" line, from the small-aberration
  expansion `S ~ 1 - (2*pi*sigma)^2` (valid only for `sigma` small, `S` near 1).
- **Mahajan's exponential approximation**: `S ~ exp(-(2*pi*sigma)^2)` (sigma in waves)
  tracks the true Strehl further from focus than the linear Maréchal form and is the one
  the Tier 0 wavefront tool reports. Both agree well above `S ~ 0.6`; below that, treat the
  reported Strehl as an estimate and prefer an actual PSF/MTF calculation (Mahajan, JOSA 73,
  860, 1983).
- **Image-space depth of focus**: `delta_z ~ +/- 2 * lambda * (F/#)^2`, the axial range over
  which the geometric blur stays within about one Airy radius.
- **Object-space depth of field for a microscope**: `DOF ~ n * lambda / NA^2` (the
  diffraction term; add a geometric term `n * e / (M * NA)` for a finite detector pixel/CoC
  size `e`). NA, not F/#, is the right aperture variable once NA exceeds about 0.25.

## Chromatic aberration

- **Thin-element achromat condition**: for two thin elements in contact with powers
  `phi_1, phi_2` and Abbe numbers `V_1, V_2`, zero axial color at the two design
  wavelengths requires `phi_1 / V_1 + phi_2 / V_2 = 0` together with `phi_1 + phi_2 = phi`
  (the total power). Solving gives `phi_1 = phi * V_1 / (V_1 - V_2)`, which is why an
  achromat pairs a low-index crown (`phi_1 > 0`, high `V`) with a high-index flint
  (`phi_2 < 0`, low `V`).
- **Secondary spectrum**: correcting axial color at two wavelengths (typically F and C)
  leaves a residual focus shift at a third (commonly d or g), because relative partial
  dispersion `P = (n_x - n_F) / (n_F - n_C)` is not exactly linear in `V` across the glass
  catalog. Glasses off the "normal line" in the `P`-`V` diagram (fluorites, anomalous-
  dispersion FK/KZFS types) reduce it — the difference between an achromat and an apochromat.
- **Chromatic focal shift over a band**: for a source of bandwidth `Delta_lambda`, expect a
  focal shift of order `f/V` scaled by `Delta_lambda` relative to the design pair's
  separation. This matters most for OCT, where SLD or swept sources span tens to over a
  hundred nm (`Delta_lambda/lambda` often 5-10%); a shift comparable to or larger than the
  coherence-gated axial resolution (typically a few um) smears the A-scan and must be
  checked across the full source band, not just two design wavelengths ([OCT](oct.md)).

## Sources

- M. J. Kidger, *Fundamental Optical Design*, SPIE Press, 2001 — Seidel theory, stop-shift
  identities, practical variable-to-aberration mapping.
- W. J. Smith, *Modern Optical Engineering*, 4th ed., McGraw-Hill, 2007 — diffraction
  limits, depth of focus, general design practice.
- J. Sasián, *Introduction to Lens Design*, Cambridge University Press, 2019 — wavefront
  polynomial notation, Petzval sum derivation, aberration-to-variable correspondence.
- R. R. Shannon, *The Art and Science of Optical Design*, Cambridge University Press, 1997
  — practical correction strategy by variable class.
- V. N. Mahajan, "Strehl ratio for primary aberrations in terms of their aberration
  variance," [JOSA 73, 860 (1983)](https://opg.optica.org/josa/abstract.cfm?uri=josa-73-6-860)
  — the exponential Strehl approximation and its validity range.
- Ansys/Zemax knowledge base, ["What is a Point Spread Function"](https://optics.ansys.com/hc/en-us/articles/42661723066515-What-is-a-Point-Spread-Function)
  and the community thread on [confusing spherical aberration with defocus](https://community.zemax.com/got-a-question-7/removing-spherical-aberration-from-optimization-2027)
  (see [diagnosis.md](diagnosis.md) for the full misdiagnosis list).
- ray-optics ([mjhoptics/ray-optics](https://github.com/mjhoptics/ray-optics)) for y-ybar
  first-order layout diagrams that make stop-shift and Petzval arguments visual.

## Controlled signature checks

For a signed meridional pupil coordinate `p`, set one normalized wavefront coefficient
to 1 and others to zero. Differentiation gives the shape of transverse error (overall
sign/scale and reference tilt depend on the ray-fan convention):

| Isolated contribution | Wavefront section | Transverse shape | Applicability |
|---|---|---|---|
| Defocus | `p^2` | `2p`, odd straight line | Fixed image plane |
| Spherical | `p^4` | `4p^3`, odd cubic | Primary spherical in a centered system |
| Coma | `h*p^3` | `3h*p^2`, even parabola | Tangential section at nonzero field |
| Astigmatism | `h^2*p^2` | `2h^2*p` in tangential section | Compare sagittal section and focus |
| Distortion | `h^3*p` | `h^3`, constant offset | Gaussian-image reference; chief-ray reference removes it |
| Axial color | `a(lambda)*p^2` | `2a(lambda)*p` | Wavelength-dependent defocus at one image plane |

These are controlled low-order checks, not unique diagnoses of mixed real lenses.
For example `p = [-1, -0.5, 0, 0.5, 1]` gives coma `[3, .75, 0, .75, 3]` at `h=1`.
Plot against signed pupil coordinate and compare with the measured fan's reference.
Sasián's linked paper, Eq. (2) and Table 1, supplies the polynomial convention.
