# 4f relay / tube lens pair

Two identical air-spaced achromats (the `air-spaced-achromat` cell, scaled to 200 mm
EFL each, mirror-facing), separated by 366.3 mm — close to but not exactly the
thin-lens estimate of f1+f2=400 mm; the gap is each lens's own principal-plane offset,
exactly why you solve this with a real ray trace, not the thin-lens formula. 4 mm
entrance pupil (f/50 per element, deliberately slow — a relay, not an imager),
+/-1 degree field, 486.1/587.6/656.3 nm.

**Afocal by construction — read the numbers accordingly.** Two positive lenses
separated by the sum of their focal lengths have zero net power; paraxial EFL comes
out in the millions of mm, meaning "infinite," not "broken." There is no on-axis spot
worth reporting — the "image" surface is a 50 mm observation plane past the second
lens where the beam is still a collimated 4 mm bundle. Judge this on collimation: a
marginal ray entering parallel to the axis exits parallel to better than 1e-8, and
chief-ray angular magnification between the collimated spaces is -1.

Good for relaying an intermediate image or pupil between two collimated-space stages
of an infinity-corrected microscope, keeping a real collimated region in the middle
for a mirror, filter, or DM. See eval scenario 2 for pupil/sampling matching.

Release the group separation first (sets the afocal condition, safe alone), then
element curvatures if pupil aberrations need trimming — untouched in this build.

Goodman, *Introduction to Fourier Optics*, ch. 5; `references/microscopy.md`.
