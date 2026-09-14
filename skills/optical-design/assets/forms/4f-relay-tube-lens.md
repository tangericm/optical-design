# 4f relay / tube lens pair

Two identical air-spaced achromats (the `air-spaced-achromat` cell, scaled to 200 mm
EFL each and mirror-facing), separated by 366.3 mm — close to, but not exactly, the
thin-lens estimate of f1+f2=400 mm; the difference is the two lenses' own principal-
plane offsets, which is exactly why you solve this with a real ray trace instead of
trusting the thin-lens formula. 4 mm entrance pupil (f/50 per element, deliberately
slow — this is a relay, not an imaging lens), +/-1 degree field, 486.1/587.6/656.3 nm.

**Read the numbers correctly: this system is afocal by construction.** Two positive
lenses separated by the sum of their focal lengths have zero net power — paraxial EFL
comes out in the millions of mm, which means "infinite," not "broken." There is no
on-axis spot number worth reporting because nothing focuses; the reported "image"
surface is a 50 mm observation plane downstream of the second lens where the beam is
still a collimated 4 mm bundle. Judge this form on collimation, not spot size: a
marginal ray entering parallel to the axis exits parallel to the axis (confirmed to
better than 1e-8 in the build), and the chief ray angle magnification is -1 (unit,
inverting) between the input and output collimated spaces.

Good for: relaying an intermediate image or a pupil between two collimated-space
elements of an infinity-corrected microscope — two objectives, an objective and a
scanner, or a scanner and a tube lens — while keeping a real collimated region in the
middle for a mirror, filter, or DM. See eval scenario 2 for matching this pair's pupil
and sampling to an objective and a camera.

Release the group separation first (it sets the afocal condition and nothing else, so
it is safe to vary alone), then the individual element curvatures if pupil aberrations
at 4 mm need trimming — the built form has not had those touched at all.

Goodman, *Introduction to Fourier Optics*, ch. 5 (4f imaging systems); the tube-lens
conventions in `references/microscopy.md`.
