# Microscope objective, 20x

Modeled in Optiland's reverse-trace convention for infinity-corrected objectives: the
"object" is at infinity on the tube-lens side (entrance pupil 8.08 mm there, full field
1.0 degree in that space) and the real image, at NA 0.52, forms on the surface the
model calls "image" — physically the specimen plane. Six elements (N-SK16/SF4 cemented
front pair, air gap, N-SK16 singlet, air gap, N-SK16/SF4 cemented pair, N-K5 field
element), 486.1 / 587.6 / 656.3 nm.
`optiland.samples.microscopes.Microscope20x` unmodified. On-axis RMS spot at the
specimen plane is 48.9 um against a 0.65 um Airy radius at NA 0.52 — before using this
form, re-verify on-axis correction yourself (trace `Hx=Hy=0` and look at the ray fan);
a spot this far from diffraction-limited on-axis usually means a vignetting factor,
vignetted vs. unvignetted vertex-field weighting, or a vertex-weighted default sample
setting is fighting you, not that the underlying prescription is actually this bad.

Good for: a starting shape for a 20x-class air objective (NA around 0.4-0.5, dry,
finite or infinity working distance) or for reverse-engineering what tube lens and
sampling a real 20x objective in your lab needs — see `references/microscopy.md` for
the Nikon-200/Olympus-180/Zeiss-165/Leica-200 mm tube-lens convention and how it sets
system magnification and pixel sampling. NA above about 0.5 at this element count
starts fighting spherochromatism and coma hard; that is roughly where real objectives
add elements or move to a plan-apochromat design.

Release the two air gaps first (focus and NA balance), then the outer cemented pair's
curvatures.

Zhang and Gross, "Systematic design of microscope objectives," parts I-III, *Adv. Opt.
Techn.* (2019); Sasián, *Introduction to Lens Design*, ch. 15.
