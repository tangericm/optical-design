# Optical terms at a glance

[Documentation](README.md) / Glossary

Use this alongside the [quickstart](quickstart.md). Reports retain exact metric
names and units; a short label should never hide a different definition.

| Term | Meaning in this workflow |
|---|---|
| Prescription | The surface-by-surface description of a lens system, including materials and distances |
| Sequential | Rays encounter surfaces in a declared order; this workflow targets centered imaging systems |
| Singlet | One lens element, usually bounded by two optical surfaces |
| Aperture / entrance pupil | The opening, or its object-side image, that limits the admitted ray bundle |
| f-number | Effective focal length divided by entrance-pupil diameter for the usual infinity-focus convention |
| Field | An object position or direction away from the optical axis; this adapter uses angle fields |
| Wavelength | The light's wavelength, stated with its unit; 550 nm is 0.55 µm |
| Airy radius | The distance to the first dark ring for an ideal clear circular pupil; not the diameter or FWHM |
| PSF | Point spread function: the image of an ideal point under a stated optical model |
| MTF | Modulation transfer function: contrast transfer versus spatial frequency under stated conditions |
| RMS spot radius | Root-mean-square ray distance from the spot centroid for this tool's declared metric |
| Aberration | A departure from ideal imaging, such as spherical aberration, coma, or astigmatism |
| Merit function | A numerical objective used to rank trial designs; lower is better for the shipped minimization workflow |
| Hard requirement | A condition a candidate must satisfy, even if its merit improves |
| Refocus | Adjusting the final image-space air gap to improve focus within specified bounds |
| Sensitivity | How a metric changes near one model when a declared parameter is perturbed |
| Tolerance study | Results under specified parameter-variation distributions, samples, and compensation assumptions |
| Validation | Checking a saved candidate against declared conditions; separate conditions must be fixed before selection to remain independent |
| Receipt | A recorded job report with configuration, outcomes, file identities, and supporting evidence |
| Seidel aberrations | The five third-order monochromatic terms — spherical (SI), coma (SII), astigmatism (SIII), Petzval/field curvature (SIV), distortion (SV) — that describe how a real system departs from ideal imaging, named by the surface-by-surface sums Optiland's `optic.aberrations.seidels()` reports |
| Petzval sum | The field-curvature contribution set purely by surface curvatures and refractive indices, independent of aperture or stop position; a large sum means the image surface is inherently curved, correctable mainly by an index split or a field flattener |
| Ray fan | A plot of ray aberration (transverse image-plane error) versus pupil coordinate for one field and wavelength; its curve shape identifies the aberration — a tilted line is defocus, a symmetric parabola is spherical, an odd S-curve is coma |
| OPD fan | The optical-path-difference analog of a ray fan: wavefront error versus pupil coordinate, used the same way but in units of length or waves rather than transverse image-plane error |
| Telecentricity | A condition where the chief ray in image space (or object space) travels parallel to the optical axis at every field, so magnification does not change with defocus; reported as the chief-ray angle at the image, 0° being exactly telecentric |
| Chromatic focal shift | The change in effective focal length (or back focal distance) with wavelength, from dispersion in the glass; the longitudinal analog of lateral color, relevant whenever a design spans a wavelength band rather than one line |
| Confocal parameter | Twice the Rayleigh range of a focused Gaussian beam — the axial distance over which the beam stays near its waist size; in OCT it sets the depth of focus and trades directly against lateral resolution through the numerical aperture |
| Operand | One term in a merit function: a computed quantity (an EFL, an RMS spot size, a chief-ray angle) paired with a target, weight, and the input data needed to evaluate it |
| Variable | A prescription parameter (radius, thickness, conic, an asphere coefficient, a glass choice) an optimizer is allowed to change within its declared bounds while chasing the merit function |
| Damped least squares | The standard local optimization algorithm for lens design (Optiland's `LeastSquares`): iteratively adjusts variables to minimize the sum of squared operand residuals, damped to keep steps stable near a nonlinear optimum |
| Compensator | A variable — usually focus, sometimes a group spacing — that a tolerancing or Monte Carlo run is allowed to re-adjust after a perturbation, modeling the fact that a real assembly gets refocused at final test |
| Yield | The fraction of Monte Carlo trials (with declared perturbations, and any compensator) that pass the stated requirements; a conditional estimate under the chosen distributions and sample count, not a manufacturing guarantee |

For equations, assumptions, and source references, see [PSF/MTF](../skills/optical-design/references/psf-mtf.md),
[microscopy](../skills/optical-design/references/microscopy.md), and
[tolerancing](../skills/optical-design/references/tolerancing.md).
