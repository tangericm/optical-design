# Petzval lens

50.6 mm EFL, f/1.4, four elements in two widely separated groups (N-LAK12/SF4 cemented
front pair, then a long air gap, then a separated N-LAK12 / LF5 rear pair), 7 degrees
half field, 486.1 / 587.6 / 656.3 nm. `optiland.samples.objectives.PetzvalLens`
unmodified. On-axis RMS spot 96.7 um against a 0.95 um Airy radius at f/1.4 — this
sample is deliberately fast and narrow-field; do not expect a clean on-axis spot from
this form the way you would from a slower lens; it is here to show the shape and the
tradeoff, not to be used unmodified.

Good for: speed over field — projection lenses, fast relay optics, the historical
portrait-lens role. Two widely spaced achromatic-ish groups let you push aperture much
further than a Cooke triplet or Double Gauss at the same element count, at the direct
cost of field: the namesake Petzval field curvature is essentially unconstrained by
this topology (nothing forces the Petzval sum toward zero the way a symmetric stop
does), so the useful field stays under about 10 degrees half field without adding a
field-flattener element near the image.

Release the rear group's air gap first (it is the main field-curvature and focus
handle), then the front cemented pair's curvatures for spherical, and treat the wide
central air gap as a variable only once the two groups are each individually corrected
— it is what makes this form fast but also what limits the field.

Kingslake, *A History of the Photographic Lens* (Petzval, 1840); Sasián, *Introduction
to Lens Design*, ch. 13 (Petzval sum and field curvature).
