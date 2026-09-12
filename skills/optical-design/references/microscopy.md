# Microscopy relays

Define the modality first: fluorescence widefield, transmitted brightfield, coherent
laser imaging, confocal and structured illumination need different transfer models.
NA and wavelength influence resolution, but illumination coherence, specimen contrast,
condenser aperture and aberrations also matter. Magnification alone does not establish
specimen resolution. Report the chosen criterion instead of one universal resolution
number. [Nikon resolution reference](https://www.microscopyu.com/microscopy-basics/resolution).

For a relay audit, record objective identity, immersion medium, cover-glass condition,
object-space field, pupil location, tube-lens/relay arrangement, detector pitch, wavelength
band and usable working distance. Treat these as required inputs; do not fill unknown
objective correction data with a generic lens prescription.

Run the existing calculator for a declared conventional scalar estimate:

```powershell
uv run scripts/resolve.py micro --wavelength-um 0.52 --na 0.8 --magnification 40 --pixel-um 6.5 --json
```

The input is illustrative. Use the returned values and warnings; do not treat them as
verification of a real objective. Convert detector pitch to object-space sampling using
the actual system magnification, including any relay. Check the smallest required feature
and field edge, then verify the assembled prescription with the applicable PSF/MTF model.

Keep object-space depth of field distinct from the allowed displacement of the image
plane. Define the sharpness criterion and whether a quoted range is full or half width.
Leica describes depth of field in terms of acceptable object displacement with objective
and image plane fixed.
[Leica depth of field](https://www.leica-microsystems.com/science-lab/microscopy-basics/depth-of-field-in-microscopy).

Recommended acceptance evidence: required-field metrics, magnification and pupil clipping
checks, focus travel, and detector sampling. High-NA or polarization-sensitive performance
needs an appropriate vector model; the Tier 0 scalar calculator does not supply that
evidence. See [PSF/MTF limits](psf-mtf.md) and [specification contract](specifications.md).

Primary links checked 2026-09-12. The audit checklist is project workflow guidance.
