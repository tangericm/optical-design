# Microscope objective, 20x

Modeled in Optiland's reverse-trace convention: "object" at infinity on the tube-lens
side (8.08 mm entrance pupil there, 1.0 degree full field in that space), real image
at NA 0.52 on the surface the model calls "image" — physically the specimen plane.
Six elements (N-SK16/SF4 cemented pair, air gap, N-SK16 singlet, air gap, N-SK16/SF4
cemented pair, N-K5 field element), 486.1 / 587.6 / 656.3 nm.
`optiland.samples.microscopes.Microscope20x` unmodified. On-axis RMS spot at the
specimen plane is 48.9 um against a 0.65 um Airy radius at NA 0.52 — before trusting
this number, re-trace `Hx=Hy=0` yourself; a spot this far from diffraction-limited
on-axis usually means a vignetting-factor or field-weighting default is fighting you,
not that the prescription is really this bad.

Good for a starting shape at NA 0.4-0.5, dry, or for reverse-engineering what tube lens
and sampling a real 20x objective needs — see `references/microscopy.md` for the
Nikon-200/Olympus-180/Zeiss-165/Leica-200 mm tube-lens convention. NA above about 0.5
at this element count fights spherochromatism and coma hard; real objectives add
elements or go plan-apochromat there.

Release the two air gaps first (focus, NA balance), then the outer cemented pair.

Zhang and Gross, "Systematic design of microscope objectives," *Adv. Opt. Techn.*
(2019); Sasián, *Introduction to Lens Design*, ch. 15.
