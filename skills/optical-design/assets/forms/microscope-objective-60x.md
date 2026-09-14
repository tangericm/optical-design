# Microscope objective, 60x

Same reverse-trace convention as the 20x form: infinite conjugate on the tube-lens
side (imageFNO 0.9 there, full field 1.0 degree in that space), NA 0.56 at the real
image (specimen) surface. Nine elements across seventeen surfaces — N-FK51/J-LLF2
cemented front pair, air gap, N-FK51 singlet, air gap, a fluorite-class group in
SF5/N-FK51/N-KZFS4, a LITHOTEC-CAF2 pair, and an N-FK51/N-SK11 rear cemented pair —
486.1 / 587.6 / 656.3 nm, total track 594.5 mm (long — this is a real multi-group
apochromat-class layout, not a compact toy). `optiland.samples.microscopes.Objective60x`
unmodified. On-axis RMS spot 11.5 um against a 0.60 um Airy radius at NA 0.56.

Good for: a starting shape for a high-element-count objective built from
low-dispersion and fluorite-class glasses (LITHOTEC-CAF2, N-FK51) — the material
palette that lets a design reach high NA (real 60x oil objectives run NA 0.9-1.4; this
sample sits lower, at NA 0.56, so treat it as a representative multi-group form and
NA-class placeholder rather than a catalog match to any specific 60x objective). The
nine-element, multi-group structure is what buys correction at high NA across a wide
spectral band; a Cooke- or Tessar-class element count simply cannot get there.

Release the air gaps between groups first — with this many elements, focus and
spherochromatism balance dominate before individual curvatures matter — then the
cemented pairs closest to the aperture stop.

Zhang and Gross, "Systematic design of microscope objectives," parts I-III, *Adv. Opt.
Techn.* (2019), on the 29 lens modules this class of design draws from.
