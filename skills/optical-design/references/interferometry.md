# Interferometry interpretation

Before interpreting a map, record wavelength, phase/OPD units, reference/test path, pass count,
incidence angle, pupil geometry, phase sign, and which piston/tilt/defocus terms were removed.
Do not infer a surface specification from a wavefront number alone.

`interfero.py` distinguishes measured OPD, single-pass wavefront and surface height through
`--measurement`. Read the subcommand help for applicable arguments. The legacy factor of
two is reported as an assumption; use an explicit pass/quantity model for measured data.
The implemented surface conversion assumes simple reflective displacement geometry with
an incidence-angle cosine factor. It does not establish the conversion for arbitrary
refractive, tilted-reference or multi-path instruments. Preserve the raw measured OPD.

Phase unwrapping resolves modulo-phase ambiguity under data/continuity assumptions; it does
not reconstruct arbitrary missing phase or establish absolute piston. Low contrast,
disconnected pupils and large spatial phase steps need an acquisition/uncertainty review.
The numerical fit reports actual-mask reconstruction RMS, rank, conditioning and coverage;
coefficient RMS on a full unit disk is a different quantity for clipped/obstructed masks.

Use `interfero.py cavity` for a bounded simple wedge model. Zero relative tilt yields zero
fringe count and undefined/infinite fringe spacing, represented by null. For pupil
diffraction checks use [PSF/MTF](psf-mtf.md); do not compare a fitted residual with a
specification that includes removed terms. The phase-unwrapping implementation follows
[scikit-image's documented unwrap_phase API](https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.unwrap_phase).
