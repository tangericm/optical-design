# Optical terms at a glance

[Documentation](README.md) / Glossary

Use this alongside the [example workflow](first-lens.md). Reports retain exact metric
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

For equations, assumptions, and source references, see [PSF/MTF](../skills/optical-design/references/psf-mtf.md),
[microscopy](../skills/optical-design/references/microscopy.md), and
[tolerancing](../skills/optical-design/references/tolerancing.md).
